"""
執行: python create_initial_data.py
建立初始管理者帳號與測試資料
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "approval_system.settings")
django.setup()

from django.contrib.auth.models import User
from core.models import Employee, WorkflowCategory, WorkflowStep

# 管理者帳號
admin_user, created = User.objects.get_or_create(username="admin")
if created:
    admin_user.set_password("admin1234")
    admin_user.save()
    Employee.objects.create(user=admin_user, name="系統管理者", email="admin@company.com", is_admin=True)
    print("已建立管理者: admin / admin1234")

# 測試員工
user1, created = User.objects.get_or_create(username="user1")
if created:
    user1.set_password("user1234")
    user1.save()
    Employee.objects.create(user=user1, name="張小明", email="user1@company.com", department_code="IT")
    print("已建立員工: user1 / user1234")

user2, created = User.objects.get_or_create(username="manager1")
if created:
    user2.set_password("user1234")
    user2.save()
    Employee.objects.create(user=user2, name="李主管", email="manager1@company.com", department_code="IT")
    print("已建立員工: manager1 / user1234")

# 測試簽核類別
if not WorkflowCategory.objects.exists():
    wf = WorkflowCategory.objects.create(
        name="請假申請",
        description="員工請假流程，含直屬主管及人資審核",
        num_levels=2,
    )
    emp_manager = Employee.objects.get(email="manager1@company.com")
    WorkflowStep.objects.create(category=wf, step_number=1, name="直屬主管審核", approver_type="direct_manager")
    WorkflowStep.objects.create(category=wf, step_number=2, name="人資確認", approver_type="specific_employee", specific_approver=emp_manager)
    print(f"已建立簽核類別: {wf.name}")

print("\n初始資料建立完成！")
print("登入網址: http://127.0.0.1:8000/login/")
print("管理者: admin / admin1234")
print("員工:   user1 / user1234")
print("主管:   manager1 / user1234")
