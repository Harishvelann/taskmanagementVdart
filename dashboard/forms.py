from django import forms  # type: ignore
from .models import Employee, Profile, Task


# ---------------- Add Employee Form ----------------
class AddEmployeeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'name', 'email', 'phone', 'role']


# ---------------- Task Form ----------------
class TaskForm(forms.ModelForm):
    assigned_employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'style': 'width: 100%'
        }),
        required=False,
        label='Assign Employees'
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'status', 'assigned_employees', 'alert_all']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Task Title', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'alert_all': 'Alert Assigned Employees'
        }


# ---------------- Employee Form ----------------
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
