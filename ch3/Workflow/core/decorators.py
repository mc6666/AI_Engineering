from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


# 管理者專用裝飾器：未登入導向登入頁，非管理者導向一般使用者儀表板
def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # 保留原始目標路徑，登入後可直接跳回
            return redirect(f"/login/?next={request.path}")
        employee = getattr(request.user, "employee", None)
        if not employee or not employee.is_admin:
            messages.error(request, "需要管理者權限")
            return redirect("user_dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper


# 員工專用裝飾器：未登入導向登入頁，已登入但無員工資料者提示設定
def employee_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/login/?next={request.path}")
        employee = getattr(request.user, "employee", None)
        # User 存在但尚未建立 Employee 記錄時（如 superuser 未綁定），拒絕存取
        if not employee:
            messages.error(request, "請先完成員工資料設定")
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper
