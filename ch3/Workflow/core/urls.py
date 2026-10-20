from django.urls import path
from core.views.auth_views import login_view, logout_view, dashboard_view
from core.views import admin_views, user_views

urlpatterns = [
    # 進入點：依角色自動分流到管理後台或使用者儀表板
    path("", dashboard_view, name="dashboard"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # --- 管理後台路由（需 is_admin） ---
    path("admin-panel/", admin_views.admin_dashboard, name="admin_dashboard"),

    # 員工維護
    path("admin-panel/employees/", admin_views.employee_list, name="employee_list"),
    path("admin-panel/employees/create/", admin_views.employee_create, name="employee_create"),
    path("admin-panel/employees/<int:pk>/edit/", admin_views.employee_edit, name="employee_edit"),
    path("admin-panel/employees/<int:pk>/delete/", admin_views.employee_delete, name="employee_delete"),

    # 組織樹
    path("admin-panel/org/", admin_views.org_tree_view, name="org_tree"),
    path("admin-panel/org/save/", admin_views.org_tree_save, name="org_tree_save"),

    # 簽核類別與步驟設定
    path("admin-panel/workflows/", admin_views.workflow_list, name="workflow_list"),
    path("admin-panel/workflows/create/", admin_views.workflow_create, name="workflow_create"),
    path("admin-panel/workflows/<int:pk>/edit/", admin_views.workflow_edit, name="workflow_edit"),
    path("admin-panel/workflows/<int:pk>/delete/", admin_views.workflow_delete, name="workflow_delete"),
    path("admin-panel/workflows/<int:pk>/steps/", admin_views.workflow_steps, name="workflow_steps"),
    path("admin-panel/workflows/<int:pk>/steps/save/", admin_views.workflow_step_save, name="workflow_step_save"),

    # 表單設計
    path("admin-panel/workflows/<int:pk>/form/", admin_views.form_design, name="form_design"),

    # 案件總覽
    path("admin-panel/cases/", admin_views.admin_case_list, name="admin_case_list"),
    path("admin-panel/cases/<int:pk>/", admin_views.admin_case_detail, name="admin_case_detail"),

    # --- 一般使用者路由 ---
    path("dashboard/", user_views.user_dashboard, name="user_dashboard"),

    # 申請流程
    path("apply/", user_views.apply_select_workflow, name="apply_select"),
    path("apply/<int:pk>/", user_views.apply_form, name="apply_form"),

    # 案件查詢與追蹤
    path("my-cases/", user_views.my_cases, name="my_cases"),
    path("cases/<int:pk>/", user_views.case_detail, name="case_detail"),
    path("cases/<int:pk>/withdraw/", user_views.withdraw_case, name="withdraw_case"),

    # 簽核作業
    path("approvals/", user_views.pending_approvals, name="pending_approvals"),
    path("approvals/<int:record_pk>/", user_views.approve_case, name="approve_case"),
]
