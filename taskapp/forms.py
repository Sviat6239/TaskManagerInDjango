from django import forms
from .models import Task, Project, Comment, Issue, Label

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'completed', 'stage', 'deadline', 'access', 'attachment']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'members']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['task', 'text', 'attachment']

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['task', 'text', 'attachment']

class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['name', 'color', 'tasks']