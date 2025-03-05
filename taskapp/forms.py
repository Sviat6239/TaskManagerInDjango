from django import forms
from .models import Task, Project, Comment, Issue, Label, Deadline, Notification
from auth_app.models import CustomUser 

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'completed', 'stage', 'deadline', 'access', 'attachment']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'access': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'stage': forms.NumberInput(attrs={'class': 'form-control'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['access'].queryset = CustomUser.objects.all()
        self.fields['access'].required = False

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'members', 'tasks'] 
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'members': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'tasks': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['members'].queryset = CustomUser.objects.all()
        self.fields['tasks'].queryset = Task.objects.all()
        self.fields['tasks'].required = False

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['task', 'text', 'attachment']
        widgets = {
            'task': forms.Select(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task'].queryset = Task.objects.all()

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['task', 'text', 'attachment']
        widgets = {
            'task': forms.Select(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task'].queryset = Task.objects.all()

class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['name', 'color', 'tasks']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'tasks': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tasks'].queryset = Task.objects.all()

class DeadlineForm(forms.ModelForm):
    class Meta:
        model = Deadline
        fields = ['title', 'due_date', 'task', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'task': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task'].queryset = Task.objects.all()
        self.fields['task'].required = False

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['user', 'task', 'message']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'task': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = CustomUser.objects.all()
        self.fields['task'].queryset = Task.objects.all()

class AddFriendForm(forms.Form):
    pass