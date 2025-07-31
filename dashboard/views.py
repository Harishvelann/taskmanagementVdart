from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.contrib import messages

from .models import Profile, Task, Notification, Employee
from .forms import AddEmployeeForm, TaskForm, EmployeeForm

# ------------------- 🔐 Admin Login -------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': "Invalid username or password"})
    return render(request, 'login.html')


# ------------------- 🚪 Admin Logout -------------------
def logout_view(request):
    logout(request)
    return redirect('login')


# ------------------- 📊 Admin Dashboard -------------------
@login_required
def dashboard(request):
    today = timezone.now().date()
    context = {
        'employee_count': Employee.objects.count(),
        'task_count': Task.objects.count(),
        'overdue_count': Task.objects.filter(due_date__lt=today, status__in=['pending', 'in_progress']).count(),
        'no_deadline_count': Task.objects.filter(due_date__isnull=True).count(),
        'due_today_count': Task.objects.filter(due_date=today).count(),
        'pending_count': Task.objects.filter(status='pending').count(),
        'in_progress_count': Task.objects.filter(status='in_progress').count(),
        'completed_count': Task.objects.filter(status='completed').count(),
        'notification_count': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    return render(request, 'dashboard/dashboard.html', context)


# ------------------- ✅ Create Task -------------------
@login_required
def create_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            form.save_m2m()

            if task.alert_all:
                for employee in task.assigned_employees.all():
                    if employee.user:
                        Notification.objects.create(
                            user=employee.user,
                            task=task,
                            message=f"You have been assigned a new task: '{task.title}' by {request.user.username}."
                        )
            messages.success(request, "Task created successfully!")
            return redirect('dashboard')
    else:
        form = TaskForm()
    return render(request, 'dashboard/create_task.html', {'form': form})


# ------------------- 👥 Manage Users -------------------
@login_required
def manage_users(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    users = User.objects.all()
    return render(request, 'dashboard/manage_users.html', {'users': users})


@login_required
def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_staff = bool(request.POST.get('is_staff'))
        is_superuser = bool(request.POST.get('is_superuser'))

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save()
            messages.success(request, 'User added successfully.')
            return redirect('manage_users')

    return render(request, 'dashboard/add_user.html')


@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.is_staff = bool(request.POST.get('is_staff'))
        user.is_superuser = bool(request.POST.get('is_superuser'))
        user.save()
        messages.success(request, 'User updated successfully.')
        return redirect('manage_users')
    return render(request, 'dashboard/edit_user.html', {'user': user})


@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('manage_users')


# ------------------- 🧑‍💼 Employee Management -------------------
@login_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'dashboard/employee_list.html', {'employees': employees})


@login_required
def add_or_edit_employee(request, pk=None):
    employee = get_object_or_404(Employee, pk=pk) if pk else None
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'dashboard/employee_form.html', {'form': form})


@login_required
def add_employee(request):
    if not request.user.is_superuser:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AddEmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            role = form.cleaned_data['role']
            profile_picture = form.cleaned_data.get('profile_picture')

            if User.objects.filter(email=email).exists():
                form.add_error('email', 'An employee with this email already exists.')
            else:
                random_password = get_random_string(length=10)
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=random_password,
                    first_name=name
                )
                Profile.objects.create(
                    user=user, name=name, phone=phone, role=role,
                    profile_picture=profile_picture, email=email
                )
                Employee.objects.create(
                    user=user, name=name, email=email, phone=phone,
                    role=role, profile_picture=profile_picture
                )

                try:
                    send_mail(
                        subject='Welcome to TaskPro',
                        message=(f"Hello {name},\n\nYour account has been created.\nUsername: {email}\nPassword: {random_password}"),
                        from_email=None,
                        recipient_list=[email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print("Email sending failed:", e)

                return redirect('employee_list')
    else:
        form = AddEmployeeForm()
    return render(request, 'dashboard/add_employee.html', {'form': form})


@login_required
def delete_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.delete()
    return redirect('employee_list')


# ------------------- 📃 All Tasks -------------------
@login_required
def all_tasks(request):
    tasks = Task.objects.prefetch_related('assigned_employees').order_by('-created_at')
    return render(request, 'dashboard/all_tasks.html', {'tasks': tasks})


# ------------------- ✏️ Edit Task -------------------
@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('all_tasks')
    else:
        form = TaskForm(instance=task)
    return render(request, 'dashboard/edit_task.html', {'form': form, 'task': task})


# ------------------- ❌ Delete Task -------------------
@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('all_tasks')
    return render(request, 'dashboard/confirm_delete.html', {'task': task})


# ------------------- 🔔 Notifications -------------------
@login_required
def view_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'dashboard/notifications.html', {'notifications': notifications})


@login_required
def alerted_tasks(request):
    alerts = Notification.objects.filter(user=request.user, task__isnull=False).order_by('-timestamp')
    alerts.update(is_read=True)
    return render(request, 'dashboard/alerted_tasks.html', {'alerts': alerts})

# ------------------- 🔐 Employee Login -------------------
def employee_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # ✅ Only allow hardcoded credentials
        if username == 'employee' and password == 'employee123':
            request.session['employee_logged_in'] = True
            return redirect('employee_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'dashboard/employee_login.html')


# ------------------- 📋 Employee Dashboard -------------------
def employee_dashboard(request):
    if not request.session.get('employee_logged_in'):
        return redirect('employee_login')

    # Show all tasks for the employee dashboard
    tasks = Task.objects.all().order_by('-created_at')  # Optional ordering newest first

    return render(request, 'dashboard/employee_dashboard.html', {'tasks': tasks})


# ------------------- 🚪 Employee Logout -------------------
def employee_logout(request):
    request.session.flush()
    return redirect('employee_login')
