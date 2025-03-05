from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import TaskForm, ProjectForm, CommentForm, IssueForm, LabelForm
from .models import Task, Project, Comment, Issue, Label

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contacts.html')

@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    projects = Project.objects.filter(owner=request.user)
    comments = Comment.objects.filter(user=request.user)
    issues = Issue.objects.filter(user=request.user)
    labels = Label.objects.all() 
    return render(request, 'dashboard.html', {
        'tasks': tasks,
        'projects': projects,
        'comments': comments,
        'issues': issues,
        'labels': labels,
    })

@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            form.save_m2m()
            return redirect('dashboard')
    else:
        form = TaskForm()
    return render(request, 'create_task.html', {'form': form})

@login_required
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task)
    return render(request, 'update_task.html', {'form': form, 'task': task})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('dashboard')
    return render(request, 'delete_task.html', {'task': task})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.completed = not task.completed
        task.save()
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            form.save_m2m()
            return redirect('dashboard')
    else:
        form = ProjectForm()
    return render(request, 'create_project.html', {'form': form})

@login_required
def update_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'update_project.html', {'form': form, 'project': project})

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    if request.method == 'POST':
        project.delete()
        return redirect('dashboard')
    return render(request, 'delete_project.html', {'project': project})

@login_required
def add_comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.save()
            return redirect('dashboard')
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form})

@login_required
def update_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CommentForm(instance=comment)
    return render(request, 'update_comment.html', {'form': form, 'comment': comment})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == 'POST':
        comment.delete()
        return redirect('dashboard')
    return render(request, 'delete_comment.html', {'comment': comment})

@login_required
def add_issue(request):
    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.user = request.user
            issue.save()
            return redirect('dashboard')
    else:
        form = IssueForm()
    return render(request, 'add_issue.html', {'form': form})

@login_required
def update_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id, user=request.user)
    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES, instance=issue)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = IssueForm(instance=issue)
    return render(request, 'update_issue.html', {'form': form, 'issue': issue})

@login_required
def delete_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id, user=request.user)
    if request.method == 'POST':
        issue.delete()
        return redirect('dashboard')
    return render(request, 'delete_issue.html', {'issue': issue})

@login_required
def close_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id, user=request.user)
    if request.method == 'POST':
        issue.closed = not issue.closed
        issue.save()
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def add_label(request):
    if request.method == 'POST':
        form = LabelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = LabelForm()
    return render(request, 'add_label.html', {'form': form})

@login_required
def update_label(request, label_id):
    label = get_object_or_404(Label, id=label_id)  
    if request.method == 'POST':
        form = LabelForm(request.POST, instance=label)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = LabelForm(instance=label)
    return render(request, 'update_label.html', {'form': form, 'label': label})

@login_required
def delete_label(request, label_id):
    label = get_object_or_404(Label, id=label_id)  
    if request.method == 'POST':
        label.delete()
        return redirect('dashboard')
    return render(request, 'delete_label.html', {'label': label})