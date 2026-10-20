from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from core.models import Employee, WorkflowCategory, WorkflowStep, Case, CaseApprovalRecord, FormTemplate
from core.decorators import employee_required
from core.services import get_next_approver, resolve_approver


@employee_required
def user_dashboard(request):
    emp = request.user.employee
    # 最近 5 筆自己的案件與待簽數量，供首頁快速預覽
    my_cases = Case.objects.filter(created_by=emp).order_by("-created_at")[:5]
    pending_qs = CaseApprovalRecord.objects.filter(approver=emp, action__isnull=True)
    pending_count = pending_qs.count()
    pending_approvals = pending_qs.select_related("case").order_by("-created_at")[:5]
    return render(request, "user/dashboard.html", {
        "my_cases": my_cases,
        "pending_count": pending_count,
        "pending_approvals": pending_approvals,
    })


@employee_required
def apply_select_workflow(request):
    # 列出所有可申請的簽核類別，讓使用者選擇要填寫哪種表單
    workflows = WorkflowCategory.objects.prefetch_related("steps").order_by("name")
    return render(request, "user/apply_select.html", {"workflows": workflows})


@employee_required
def apply_form(request, pk):
    wf = get_object_or_404(WorkflowCategory, pk=pk)
    form_template = getattr(wf, "form_template", None)

    if request.method == "POST":
        subject = request.POST.get("subject", "").strip()
        body = request.POST.get("body", "").strip()
        if not subject:
            messages.error(request, "主旨不可空白")
        else:
            emp = request.user.employee
            # 依 field_schema 動態收集表單欄位值，儲存為 JSON
            form_data = {}
            if form_template and form_template.field_schema:
                for field in form_template.field_schema:
                    key = field.get("name", "")
                    if key:
                        form_data[key] = request.POST.get(key, "")

            case = Case.objects.create(
                workflow=wf,
                subject=subject,
                body=body,
                form_data=form_data,
                status="pending",
                current_step=1,
                created_by=emp,
            )
            # 送出後立即建立第 1 關的簽核待辦記錄
            _create_approval_records_for_step(case, 1, emp)
            messages.success(request, f"案件「{subject}」已送出")
            return redirect("my_cases")

    return render(request, "user/apply_form.html", {"wf": wf, "form_template": form_template})


def _create_approval_records_for_step(case, step_number, submitter):
    """為指定步驟建立簽核待辦記錄；並簽時每位審核人各建一筆，action 為 NULL 表示待處理。"""
    steps = case.workflow.steps.filter(step_number=step_number)
    for step in steps:
        approver = resolve_approver(step, submitter)
        if approver:
            CaseApprovalRecord.objects.create(
                case=case,
                step_number=step_number,
                step_name=step.name,
                approver=approver,
            )


@employee_required
def my_cases(request):
    emp = request.user.employee
    status_filter = request.GET.get("status", "")
    cases = Case.objects.filter(created_by=emp).select_related("workflow").order_by("-created_at")
    # 依 ?status= 篩選，空值時顯示全部
    if status_filter:
        cases = cases.filter(status=status_filter)
    return render(request, "user/my_cases.html", {
        "cases": cases,
        "status_filter": status_filter,
        "status_choices": Case.STATUS_CHOICES,
    })


@employee_required
def case_detail(request, pk):
    case = get_object_or_404(Case, pk=pk)
    emp = request.user.employee
    # 允許：申請人本人、曾被指派為審核人、系統管理者
    is_approver = case.approval_records.filter(approver=emp).exists()
    if case.created_by != emp and not is_approver and not emp.is_admin:
        messages.error(request, "無權限查看此案件")
        return redirect("my_cases")
    records = case.approval_records.select_related("approver").all()
    return render(request, "user/case_detail.html", {"case": case, "records": records})


@employee_required
def pending_approvals(request):
    # 只取 action 為 NULL 的記錄，即尚未處理的待簽案件
    emp = request.user.employee
    records = CaseApprovalRecord.objects.filter(
        approver=emp, action__isnull=True
    ).select_related("case", "case__workflow", "case__created_by").order_by("-created_at")
    return render(request, "user/pending_approvals.html", {"records": records})


@employee_required
def approve_case(request, record_pk):
    emp = request.user.employee
    # 同時確認：此記錄屬於當前使用者且尚未處理，防止重複簽核或跨人操作
    record = get_object_or_404(CaseApprovalRecord, pk=record_pk, approver=emp, action__isnull=True)
    case = record.case

    if request.method == "POST":
        action = request.POST.get("action")
        comment = request.POST.get("comment", "").strip()

        if action not in ("approve", "reject"):
            messages.error(request, "無效操作")
            return redirect("pending_approvals")

        record.action = action
        record.comment = comment
        record.action_date = timezone.now()
        record.save()

        if action == "reject":
            # 任一人退回即整筆案件退回，不等待其他並簽人員
            case.status = "rejected"
            case.rejected = True
            case.rejected_date = timezone.now()
            case.save()
            messages.success(request, f"案件「{case.subject}」已退回")
        else:
            # 並簽情況：檢查同一步驟所有審核人員是否均已處理
            step_records = case.approval_records.filter(step_number=record.step_number)
            all_approved = all(r.action == "approve" for r in step_records)
            any_rejected = any(r.action == "reject" for r in step_records)

            if any_rejected:
                # 並簽中有人退回
                case.status = "rejected"
                case.rejected = True
                case.rejected_date = timezone.now()
                case.save()
            elif all_approved:
                # 本步驟全員核准，判斷是否有下一關
                next_step = record.step_number + 1
                has_next = case.workflow.steps.filter(step_number=next_step).exists()
                if has_next:
                    # 進入下一關：更新 current_step 並建立新一批待簽記錄
                    case.current_step = next_step
                    case.save()
                    _create_approval_records_for_step(case, next_step, case.created_by)
                    messages.success(request, f"已核准，案件進入第 {next_step} 關")
                else:
                    # 所有步驟皆完成，案件全部核准
                    case.status = "approved"
                    case.approved = True
                    case.approved_date = timezone.now()
                    case.save()
                    messages.success(request, f"案件「{case.subject}」已全部核准完成")
            else:
                # 並簽尚有其他人未處理，繼續等待
                messages.success(request, "已核准，等待其他並簽人員")

        return redirect("pending_approvals")

    return render(request, "user/approve_form.html", {"record": record, "case": case})


@employee_required
def withdraw_case(request, pk):
    # 僅允許申請人本人且案件狀態為 pending 時才可撤回
    emp = request.user.employee
    case = get_object_or_404(Case, pk=pk, created_by=emp, status="pending")
    if request.method == "POST":
        case.status = "withdrawn"
        case.save()
        messages.success(request, f"案件「{case.subject}」已撤回")
        return redirect("my_cases")
    return render(request, "user/withdraw_confirm.html", {"case": case})
