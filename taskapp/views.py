from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import TaskForm, ProjectForm, CommentForm, IssueForm, LabelForm
from .models import Task, Comment, Project, Label, Issue, Notification, Deadline

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
    deadlines = Deadline.objects.filter(owner=request.user)
    notifications = Notification.objects.filter(user=request.user, read=False)

    context = {
        'tasks': tasks,
        'projects': projects,
        'comments': comments,
        'issues': issues,
        'labels': labels,
        'deadlines': deadlines,
        'notifications': notifications,
    }
    return render(request, 'dashboard.html', context)

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
            task = form.save(commit=False)
            task.save()
            form.save_m2m()
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
            project = form.save(commit=False)
            project.save()
            form.save_m2m()
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
            comment = form.save(commit=False)
            comment.save()
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
            issue = form.save(commit=False)
            issue.save()
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

@login_required
def close_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id, user=request.user)
    if request.method == 'POST':
        issue.closed = True
        issue.save()
        Notification.objects.create(
            user=request.user,
            task=issue.task,
            message=f"Проблема '{issue.text[:50]}...' закрыта"
        )
        return redirect('dashboard')
    return render(request, 'close_issue.html', {'issue': issue})

@login_required
def reopen_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id, user=request.user)
    if request.method == 'POST':
        issue.closed = False
        issue.save()
        Notification.objects.create(
            user=request.user,
            task=issue.task,
            message=f"Проблема '{issue.text[:50]}...' повторно открыта"
        )
        return redirect('dashboard')
    return render(request, 'reopen_issue.html', {'issue': issue})

# Deadline Views: CRUD + Закрытие/Открытие
@login_required
def create_deadline(request):
    if request.method == 'POST':
        form = DeadlineForm(request.POST)
        if form.is_valid():
            deadline = form.save(commit=False)
            deadline.owner = request.user
            deadline.save()
            Notification.objects.create(
                user=request.user,
                task=deadline.task,
                message=f"Создан новый дедлайн: {deadline.title}"
            )
            return redirect('dashboard')
    else:
        form = DeadlineForm()
    return render(request, 'create_deadline.html', {'form': form})

@login_required
def update_deadline(request, deadline_id):
    deadline = get_object_or_404(Deadline, id=deadline_id, owner=request.user)
    if request.method == 'POST':
        form = DeadlineForm(request.POST, instance=deadline)
        if form.is_valid():
            deadline = form.save()
            Notification.objects.create(
                user=request.user,
                task=deadline.task,
                message=f"Дедлайн '{deadline.title}' обновлен"
            )
            return redirect('dashboard')
    else:
        form = DeadlineForm(instance=deadline)
    return render(request, 'update_deadline.html', {'form': form, 'deadline': deadline})

@login_required
def delete_deadline(request, deadline_id):
    deadline = get_object_or_404(Deadline, id=deadline_id, owner=request.user)
    if request.method == 'POST':
        deadline.delete()
        Notification.objects.create(
            user=request.user,
            task=deadline.task,
            message=f"Дедлайн '{deadline.title}' удален"
        )
        return redirect('dashboard')
    return render(request, 'delete_deadline.html', {'deadline': deadline})

@login_required
def close_deadline(request, deadline_id):
    deadline = get_object_or_404(Deadline, id=deadline_id, owner=request.user)
    if request.method == 'POST':
        deadline.is_completed = True
        deadline.save()
        Notification.objects.create(
            user=request.user,
            task=deadline.task,
            message=f"Дедлайн '{deadline.title}' завершен"
        )
        return redirect('dashboard')
    return render(request, 'close_deadline.html', {'deadline': deadline})

@login_required
def reopen_deadline(request, deadline_id):
    deadline = get_object_or_404(Deadline, id=deadline_id, owner=request.user)
    if request.method == 'POST':
        deadline.is_completed = False
        deadline.save()
        Notification.objects.create(
            user=request.user,
            task=deadline.task,
            message=f"Дедлайн '{deadline.title}' повторно открыт"
        )
        return redirect('dashboard')
    return render(request, 'reopen_deadline.html', {'deadline': deadline})
