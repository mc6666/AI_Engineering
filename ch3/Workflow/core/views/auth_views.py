from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages


def login_view(request):
    # 已登入者直接跳到儀表板，避免重複顯示登入頁
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # 支援 ?next= 參數，讓被攔截的請求登入後直接回到原頁面
            return redirect(request.GET.get("next", "dashboard"))
        messages.error(request, "帳號或密碼錯誤")
    return render(request, "auth/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard_view(request):
    # 依角色分流：管理者進入後台，一般員工進入使用者儀表板
    employee = getattr(request.user, "employee", None)
    if employee and employee.is_admin:
        return redirect("admin_dashboard")
    return redirect("user_dashboard")
