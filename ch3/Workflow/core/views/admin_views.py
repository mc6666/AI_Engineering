import json
from pathlib import Path
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction

from core.models import Employee, WorkflowCategory, WorkflowStep, FormTemplate, Case, CaseApprovalRecord
from core.decorators import admin_required
from core.services import get_dept_list


# 從設定路徑讀取組織樹 JSON
def get_org_tree():
    path = settings.ORG_TREE_PATH
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


# 將組織樹寫回 JSON 檔（ensure_ascii=False 保留中文字元）
def save_org_tree(data):
    path = settings.ORG_TREE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


@admin_required
def admin_dashboard(request):
    # 首頁顯示系統概況統計
    context = {
        "total_employees": Employee.objects.count(),
        "total_workflows": WorkflowCategory.objects.count(),
        "total_cases": Case.objects.count(),
        "pending_cases": Case.objects.filter(status="pending").count(),
    }
    return render(request, "admin/dashboard.html", context)


# --- 員工管理 ---

@admin_required
def employee_list(request):
    employees = Employee.objects.select_related("user").order_by("name")
    return render(request, "admin/employee_list.html", {"employees": employees})


@admin_required
def employee_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        tel = request.POST.get("tel", "").strip()
        dept = request.POST.get("department_code", "").strip()
        is_admin = request.POST.get("is_admin") == "on"
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not name or not email or not username or not password:
            messages.error(request, "必填欄位不可空白")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "帳號已存在")
        elif Employee.objects.filter(email=email).exists():
            messages.error(request, "Email 已存在")
        else:
            # User 與 Employee 必須同時建立，用 atomic 確保不會只建一半
            with transaction.atomic():
                user = User.objects.create_user(username=username, password=password, email=email)
                Employee.objects.create(user=user, name=name, email=email, tel=tel, department_code=dept, is_admin=is_admin)
            messages.success(request, f"員工 {name} 已新增")
            return redirect("employee_list")
    return render(request, "admin/employee_form.html", {"action": "新增"})


@admin_required
def employee_edit(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        emp.name = request.POST.get("name", emp.name).strip()
        emp.email = request.POST.get("email", emp.email).strip()
        emp.tel = request.POST.get("tel", "").strip()
        emp.department_code = request.POST.get("department_code", "").strip()
        emp.is_admin = request.POST.get("is_admin") == "on"
        emp.save()
        # 同步更新 Django User 的 email，保持一致
        if emp.user:
            emp.user.email = emp.email
            emp.user.save()
        messages.success(request, "員工資料已更新")
        return redirect("employee_list")
    return render(request, "admin/employee_form.html", {"emp": emp, "action": "編輯"})


@admin_required
def employee_delete(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        # 刪除 User 會透過 CASCADE 同時刪除 Employee；若無綁定帳號則直接刪 Employee
        if emp.user:
            emp.user.delete()
        else:
            emp.delete()
        messages.success(request, "員工已刪除")
        return redirect("employee_list")
    return render(request, "admin/employee_confirm_delete.html", {"emp": emp})


# --- 組織樹管理 ---

@admin_required
def org_tree_view(request):
    tree = get_org_tree()
    employees = Employee.objects.all().order_by("name")
    # tree_json 傳給前端 JS 以 interactive 方式編輯樹狀結構
    return render(request, "admin/org_tree.html", {"tree_json": json.dumps(tree, ensure_ascii=False), "employees": employees})


@admin_required
def org_tree_save(request):
    if request.method == "POST":
        try:
            data = json.loads(request.POST.get("tree_json", "[]"))
            save_org_tree(data)
            messages.success(request, "組織樹已儲存")
        except json.JSONDecodeError:
            messages.error(request, "JSON 格式錯誤")
    return redirect("org_tree")


# --- 簽核類別管理 ---

@admin_required
def workflow_list(request):
    workflows = WorkflowCategory.objects.prefetch_related("steps").order_by("name")
    return render(request, "admin/workflow_list.html", {"workflows": workflows})


@admin_required
def workflow_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        desc = request.POST.get("description", "").strip()
        num_levels = int(request.POST.get("num_levels", 1))
        if not name:
            messages.error(request, "名稱不可空白")
        else:
            wf = WorkflowCategory.objects.create(name=name, description=desc, num_levels=num_levels)
            messages.success(request, f"簽核類別 {name} 已新增")
            # 建立後直接導到步驟設定頁，引導管理者完成流程配置
            return redirect("workflow_steps", pk=wf.pk)
    return render(request, "admin/workflow_form.html", {"action": "新增"})


@admin_required
def workflow_edit(request, pk):
    wf = get_object_or_404(WorkflowCategory, pk=pk)
    if request.method == "POST":
        wf.name = request.POST.get("name", wf.name).strip()
        wf.description = request.POST.get("description", "").strip()
        wf.num_levels = int(request.POST.get("num_levels", 1))
        wf.save()
        messages.success(request, "簽核類別已更新")
        return redirect("workflow_list")
    return render(request, "admin/workflow_form.html", {"wf": wf, "action": "編輯"})


@admin_required
def workflow_delete(request, pk):
    wf = get_object_or_404(WorkflowCategory, pk=pk)
    if request.method == "POST":
        wf.delete()
        messages.success(request, "簽核類別已刪除")
        return redirect("workflow_list")
    return render(request, "admin/workflow_confirm_delete.html", {"wf": wf})


@admin_required
def workflow_steps(request, pk):
    wf = get_object_or_404(WorkflowCategory, pk=pk)
    steps = wf.steps.all()
    employees = Employee.objects.all().order_by("name")
    depts = get_dept_list()
    return render(request, "admin/workflow_steps.html", {"wf": wf, "steps": steps, "employees": employees, "depts": depts})


@admin_required
def workflow_step_save(request, pk):
    wf = get_object_or_404(WorkflowCategory, pk=pk)
    if request.method == "POST":
        # 採用「全刪再重建」策略，簡化步驟順序與數量異動的處理邏輯
        wf.steps.all().delete()
        step_names = request.POST.getlist("step_name")
        approver_types = request.POST.getlist("approver_type")
        specific_approvers = request.POST.getlist("specific_approver")
        specific_depts = request.POST.getlist("specific_dept")
        # is_parallel 只傳送有勾選的步驟編號（value = step index）
        is_parallels = request.POST.getlist("is_parallel")

        for i, (name, atype) in enumerate(zip(step_names, approver_types), start=1):
            if not name.strip():
                continue
            idx = i - 1
            approver_id = specific_approvers[idx] if idx < len(specific_approvers) else ""
            dept_val = specific_depts[idx] if idx < len(specific_depts) else ""
            parallel = str(i) in is_parallels
            WorkflowStep.objects.create(
                category=wf,
                step_number=i,
                name=name.strip(),
                approver_type=atype,
                specific_approver_id=approver_id if approver_id else None,
                specific_dept=dept_val,
                is_parallel=parallel,
            )
        messages.success(request, "簽核步驟已儲存")
    return redirect("workflow_steps", pk=pk)


# --- 表單設計 ---

@admin_required
def form_design(request, pk):
    wf = get_object_or_404(WorkflowCategory, pk=pk)
    # 若尚未設計過表單，自動建立一筆空白的 FormTemplate
    template, _ = FormTemplate.objects.get_or_create(category=wf)
    if request.method == "POST":
        template.html_content = request.POST.get("html_content", "")
        try:
            schema = json.loads(request.POST.get("field_schema", "[]"))
        except json.JSONDecodeError:
            schema = []
        template.field_schema = schema
        template.save()
        messages.success(request, "表單設計已儲存")
        return redirect("form_design", pk=pk)
    return render(request, "admin/form_design.html", {"wf": wf, "template": template})


# --- 案件總覽（管理者視角）---

@admin_required
def admin_case_list(request):
    # 支援依狀態與簽核類別同時篩選
    status_filter = request.GET.get("status", "")
    workflow_filter = request.GET.get("workflow", "")
    cases = Case.objects.select_related("workflow", "created_by").order_by("-created_at")
    if status_filter:
        cases = cases.filter(status=status_filter)
    if workflow_filter:
        cases = cases.filter(workflow_id=workflow_filter)
    workflows = WorkflowCategory.objects.all()
    return render(request, "admin/case_list.html", {
        "cases": cases,
        "workflows": workflows,
        "status_filter": status_filter,
        "workflow_filter": workflow_filter,
        "status_choices": Case.STATUS_CHOICES,
    })


@admin_required
def admin_case_detail(request, pk):
    case = get_object_or_404(Case, pk=pk)
    records = case.approval_records.select_related("approver").all()
    return render(request, "admin/case_detail.html", {"case": case, "records": records})
