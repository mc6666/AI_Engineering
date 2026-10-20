from django import forms
from django.contrib.auth import get_user_model

from accounts.models import Function, Role

User = get_user_model()


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name']


class FunctionForm(forms.ModelForm):
    class Meta:
        model = Function
        fields = ['code', 'name', 'description']


class RoleAssignFunctionsForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['functions']
        widgets = {'functions': forms.CheckboxSelectMultiple}


class RoleAssignUsersForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['users']
        widgets = {'users': forms.CheckboxSelectMultiple}
