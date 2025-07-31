from django.urls import path  # type: ignore
from . import views


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('employee-login/', views.employee_login, name='employee_login'),
    path('employee-dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employee-logout/', views.employee_logout, name='employee_logout'),

    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('create-task/', views.create_task, name='create_task'),
    path('tasks/', views.all_tasks, name='all_tasks'),
    path('all-tasks/', views.all_tasks, name='all_tasks'),
    path('tasks/<int:pk>/edit/', views.edit_task, name='edit_task'),
    path('tasks/<int:pk>/delete/', views.delete_task, name='delete_task'),

    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.add_or_edit_employee, name='add_employee'),
    path('employees/edit/<int:pk>/', views.add_or_edit_employee, name='edit_employee'),
    path('employees/delete/<int:pk>/', views.delete_employee, name='delete_employee'),

    path('add-employee/', views.add_employee, name='add_employee'),  # Optional if duplicate
    path('manage-users/', views.manage_users, name='manage_users'),
    path('add-user/', views.add_user, name='add_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),

    # ✅ Updated notification route name for template compatibility
    path('notifications/', views.view_notifications, name='notifications'),
    path('alerted-tasks/', views.alerted_tasks, name='alerted_tasks'),

    # Homepage as dashboard
    path('', views.dashboard, name='dashboard'),
# type: ignore

]
