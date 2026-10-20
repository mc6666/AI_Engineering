from django.db import models
from django.contrib.auth.models import User


# 員工資料：對應 Django 內建 User，擴充姓名、部門、電話等欄位
class Employee(models.Model):
    # null=True 允許尚未綁定 Django User 帳號的員工資料存在
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee", null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    tel = models.CharField(max_length=20, blank=True)
    # 對應組織樹節點的 code，用於查找所屬部門主管
    department_code = models.CharField(max_length=50, blank=True)
    # True 代表系統管理者角色，可存取 admin-panel 所有功能
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "員工"
        verbose_name_plural = "員工"


# 簽核類別：定義一種申請流程的名稱、層級數與步驟
class WorkflowCategory(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # 審核層級數決定需要幾關簽核；管理者須在步驟設定中建立對應數量的 WorkflowStep
    num_levels = models.PositiveIntegerField(default=1, verbose_name="審核層級數")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "簽核類別"
        verbose_name_plural = "簽核類別"


# 簽核步驟：每一關的審核人員設定，隸屬於某個 WorkflowCategory
class WorkflowStep(models.Model):
    APPROVER_TYPE_CHOICES = [
        ("direct_manager", "直屬主管"),   # 依申請人部門沿組織樹向上找對應層級主管
        ("dept_manager", "部門主管"),      # 指定部門的主管，或申請人的上一級部門主管
        ("specific_employee", "指定人員"), # 固定指定某位員工
    ]
    category = models.ForeignKey(WorkflowCategory, on_delete=models.CASCADE, related_name="steps")
    # step_number 決定執行順序；同一 category 不可重複
    step_number = models.PositiveIntegerField()
    name = models.CharField(max_length=200)
    approver_type = models.CharField(max_length=50, choices=APPROVER_TYPE_CHOICES)
    # 僅 approver_type == "specific_employee" 時使用；員工刪除時設為 NULL
    specific_approver = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_steps"
    )
    # 僅 approver_type == "dept_manager" 時使用；空白則取申請人上一級部門
    specific_dept = models.CharField(max_length=50, blank=True, verbose_name="指定部門")
    # True 表示此步驟需多人同時簽核（並簽），全部核准才能進入下一關
    is_parallel = models.BooleanField(default=False, verbose_name="並簽")

    class Meta:
        ordering = ["step_number"]
        unique_together = [["category", "step_number"]]
        verbose_name = "簽核步驟"
        verbose_name_plural = "簽核步驟"

    def __str__(self):
        return f"{self.category.name} - 第{self.step_number}關 {self.name}"


# 表單範本：每個簽核類別對應一份自訂 HTML 表單與欄位結構定義
class FormTemplate(models.Model):
    category = models.OneToOneField(WorkflowCategory, on_delete=models.CASCADE, related_name="form_template")
    # 管理者可輸入任意 HTML 作為表單內容預覽
    html_content = models.TextField(blank=True)
    # JSON 陣列，每個元素描述一個欄位：{"name": "field_key", "label": "顯示名稱", "type": "text"}
    field_schema = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category.name} 表單"

    class Meta:
        verbose_name = "表單設計"
        verbose_name_plural = "表單設計"


# 申請案件：紀錄一筆申請的完整狀態與動態表單填寫內容
class Case(models.Model):
    STATUS_CHOICES = [
        ("draft", "草稿"),
        ("pending", "待審核"),
        ("approved", "已核准"),
        ("rejected", "已退回"),
        ("withdrawn", "已撤回"),
    ]
    workflow = models.ForeignKey(WorkflowCategory, on_delete=models.PROTECT, related_name="cases")
    subject = models.CharField(max_length=500)
    body = models.TextField(blank=True)
    # 依 FormTemplate.field_schema 動態收集的表單欄位值，以 dict 儲存
    form_data = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    # 目前正在等待審核的步驟編號；核准後遞增，全部核准則狀態改為 approved
    current_step = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="created_cases")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # approved / rejected 為最終結果旗標，搭配日期欄位供查詢統計使用
    approved = models.BooleanField(null=True, blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    rejected = models.BooleanField(null=True, blank=True)
    rejected_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"[{self.get_status_display()}] {self.subject}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "案件"
        verbose_name_plural = "案件"


# 簽核記錄：每一位審核人員在某一步驟的簽核動作明細
class CaseApprovalRecord(models.Model):
    ACTION_CHOICES = [
        ("approve", "核准"),
        ("reject", "退回"),
        ("comment", "備註"),
    ]
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="approval_records")
    step_number = models.PositiveIntegerField()
    step_name = models.CharField(max_length=200)
    approver = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="approval_records")
    # action 為 NULL 代表尚未處理（待簽核）
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, null=True, blank=True)
    comment = models.TextField(blank=True)
    action_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["step_number", "created_at"]
        verbose_name = "簽核記錄"
        verbose_name_plural = "簽核記錄"

    def __str__(self):
        return f"{self.case} - {self.step_name} - {self.approver}"
