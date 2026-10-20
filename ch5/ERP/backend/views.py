from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from accounts.models import Function, Role

from .forms import FunctionForm, RoleAssignFunctionsForm, RoleAssignUsersForm, RoleForm


class BackofficeAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class IndexView(BackofficeAccessMixin, TemplateView):
    template_name = 'backend/index.html'


class RoleListView(BackofficeAccessMixin, ListView):
    model = Role
    template_name = 'backend/role_list.html'
    context_object_name = 'roles'


class RoleCreateView(BackofficeAccessMixin, CreateView):
    model = Role
    form_class = RoleForm
    template_name = 'backend/role_form.html'
    success_url = reverse_lazy('backend:role_list')


class RoleUpdateView(BackofficeAccessMixin, UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'backend/role_form.html'
    success_url = reverse_lazy('backend:role_list')


class RoleDeleteView(BackofficeAccessMixin, DeleteView):
    model = Role
    template_name = 'backend/role_confirm_delete.html'
    success_url = reverse_lazy('backend:role_list')


class RoleAssignFunctionsView(BackofficeAccessMixin, UpdateView):
    model = Role
    form_class = RoleAssignFunctionsForm
    template_name = 'backend/assign_functions.html'
    success_url = reverse_lazy('backend:role_list')


class RoleAssignUsersView(BackofficeAccessMixin, UpdateView):
    model = Role
    form_class = RoleAssignUsersForm
    template_name = 'backend/assign_users.html'
    success_url = reverse_lazy('backend:role_list')


class FunctionListView(BackofficeAccessMixin, ListView):
    model = Function
    template_name = 'backend/function_list.html'
    context_object_name = 'functions'


class FunctionCreateView(BackofficeAccessMixin, CreateView):
    model = Function
    form_class = FunctionForm
    template_name = 'backend/function_form.html'
    success_url = reverse_lazy('backend:function_list')


class FunctionUpdateView(BackofficeAccessMixin, UpdateView):
    model = Function
    form_class = FunctionForm
    template_name = 'backend/function_form.html'
    success_url = reverse_lazy('backend:function_list')


class FunctionDeleteView(BackofficeAccessMixin, DeleteView):
    model = Function
    template_name = 'backend/function_confirm_delete.html'
    success_url = reverse_lazy('backend:function_list')
