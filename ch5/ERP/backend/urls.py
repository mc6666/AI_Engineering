from django.urls import path

from . import views

app_name = 'backend'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/add/', views.RoleCreateView.as_view(), name='role_add'),
    path('roles/<int:pk>/edit/', views.RoleUpdateView.as_view(), name='role_edit'),
    path('roles/<int:pk>/delete/', views.RoleDeleteView.as_view(), name='role_delete'),
    path('roles/<int:pk>/functions/', views.RoleAssignFunctionsView.as_view(), name='role_assign_functions'),
    path('roles/<int:pk>/users/', views.RoleAssignUsersView.as_view(), name='role_assign_users'),

    path('functions/', views.FunctionListView.as_view(), name='function_list'),
    path('functions/add/', views.FunctionCreateView.as_view(), name='function_add'),
    path('functions/<int:pk>/edit/', views.FunctionUpdateView.as_view(), name='function_edit'),
    path('functions/<int:pk>/delete/', views.FunctionDeleteView.as_view(), name='function_delete'),
]
