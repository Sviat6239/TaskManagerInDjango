from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import TaskForm, ProjectForm, CommentForm, IssueForm, LabelForm, DeadlineForm
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
        'task_form': TaskForm(),
        'project_form': ProjectForm(),
        'comment_form': CommentForm(),
        'issue_form': IssueForm(),
        'label_form': LabelForm(),
        'deadline_form': DeadlineForm(),
    }
    return render(request, 'dashboard.html', context)

@login_required
@csrf_exempt
def create_task(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            form.save_m2m()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'item': {
                        'id': task.id,  
                        'title': task.title,
                        'description': task.description,
                        'stage': task.stage,
                        'deadline': task.deadline.isoformat() if task.deadline else None,
                        'completed': task.completed
                    }
                })
            return redirect('dashboard')
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(form.errors)})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            form.save_m2m()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'item': {
                        'id': task.id,
                        'title': task.title,
                        'description': task.description,
                        'stage': task.stage,
                        'deadline': task.deadline.isoformat() if task.deadline else None,
                        'completed': task.completed
                    }
                })
            return redirect('dashboard')
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(form.errors)})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        task.delete()
        if is_ajax:
            return JsonResponse({'success': True})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def create_project(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            form.save_m2m()

            task_count = 0
            while f'task_title_{task_count}' in request.POST:
                title = request.POST.get(f'task_title_{task_count}')
                description = request.POST.get(f'task_description_{task_count}', '')
                deadline = request.POST.get(f'task_deadline_{task_count}')
                stage = request.POST.get(f'task_stage_{task_count}', '0')
                completed = f'task_completed_{task_count}' in request.POST

                if title and deadline:
                    try:
                        task = Task(
                            title=title,
                            description=description,
                            deadline=deadline,
                            stage=int(stage),
                            completed=completed,
                            user=request.user
                        )
                        task.save()
                        project.tasks.add(task)
                    except ValueError as e:
                        print(f"Error creating task {task_count}: {e}")

                task_count += 1

            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'item': {
                        'id': project.id,
                        'name': project.name,
                        'description': project.description,
                        'members_count': project.members.count(),
                        'tasks_count': project.tasks.count()
                    }
                })
            return redirect('dashboard')
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(form.errors)})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def update_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            project.save()
            form.save_m2m()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'item': {
                        'id': project.id,
                        'name': project.name,
                        'description': project.description,
                        'members_count': project.members.count(),
                        'tasks_count': project.tasks.count()
                    }
                })
            return redirect('dashboard')
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(form.errors)})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        project.delete()
        if is_ajax:
            return JsonResponse({'success': True})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def add_comment(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'item': {
                        'id': comment.id,
                        'text': comment.text,
                        'task_title': comment.task.title if comment.task else 'N/A'
                    }
                })
            return redirect('dashboard')
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(form.errors)})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def update_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = CommentForm(request.POST, request.FILES, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'item': {
                        'id': comment.id,
                        'text': comment.text,
                        'task_title': comment.task.title if comment.task else 'N/A'
                    }
                })
            return redirect('dashboard')
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(form.errors)})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        comment.delete()
        if is_ajax:
            return JsonResponse({'success': True})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def add_issue(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = IssueForm(request.POST, request.FILES)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.user = request.user
            issue.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'item': {
                        'id': issue.id,
                        'text': issue.text,
                        'task_title': issue.task.title if issue.task else 'N/A',
                        'closed': issue.closed
                    }
                })
            return redirect('dashboard')
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(form.errors)})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def update_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id, user=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = IssueForm(request.POST, request.FILES, instance=issue)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'item': {
                        'id': issue.id,
                        'text': issue.text,
                        'task_title': issue.task.title if issue.task else 'N/A',
                        'closed': issue.closed
                    }
                })
            return redirect('dashboard')
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(form.errors)})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def delete_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id, user=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        issue.delete()
        if is_ajax:
            return JsonResponse({'success': True})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def add_label(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = LabelForm(request.POST)
        if form.is_valid():
            label = form.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'item': {
                        'id': label.id,
                        'name': label.name,
                        'color': label.color
                    }
                })
            return redirect('dashboard')
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(form.errors)})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def update_label(request, label_id):
    label = get_object_or_404(Label, id=label_id)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = LabelForm(request.POST, instance=label)
        if form.is_valid():
            label = form.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'item': {
                        'id': label.id,
                        'name': label.name,
                        'color': label.color
                    }
                })
            return redirect('dashboard')
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(form.errors)})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def delete_label(request, label_id):
    label = get_object_or_404(Label, id=label_id)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        label.delete()
        if is_ajax:
            return JsonResponse({'success': True})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def close_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id, user=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        issue.closed = True
        issue.save()
        Notification.objects.create(
            user=request.user,
            task=issue.task,
            message=f"Issue '{issue.text[:50]}...' closed"
        )
        if is_ajax:
            return JsonResponse({
                'success': True,
                'item': {
                    'id': issue.id,
                    'text': issue.text,
                    'task_title': issue.task.title if issue.task else 'N/A',
                    'closed': issue.closed
                }
            })
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def reopen_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id, user=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        issue.closed = False
        issue.save()
        Notification.objects.create(
            user=request.user,
            task=issue.task,
            message=f"Issue '{issue.text[:50]}...' reopened"
        )
        if is_ajax:
            return JsonResponse({
                'success': True,
                'item': {
                    'id': issue.id,
                    'text': issue.text,
                    'task_title': issue.task.title if issue.task else 'N/A',
                    'closed': issue.closed
                }
            })
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def create_deadline(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = DeadlineForm(request.POST)
        if form.is_valid():
            deadline = form.save(commit=False)
            deadline.owner = request.user
            deadline.save()
            Notification.objects.create(
                user=request.user,
                task=deadline.task,
                message=f"New deadline created: {deadline.title}"
            )
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'item': {
                        'id': deadline.id,
                        'title': deadline.title,
                        'due_date': deadline.due_date.isoformat() if deadline.due_date else None,
                        'task_title': deadline.task.title if deadline.task else 'N/A',
                        'description': deadline.description,
                        'is_completed': deadline.is_completed,
                        'is_overdue': deadline.is_overdue
                    }
                })
            return redirect('dashboard')
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(form.errors)})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def update_deadline(request, deadline_id):
    deadline = get_object_or_404(Deadline, id=deadline_id, owner=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = DeadlineForm(request.POST, instance=deadline)
        if form.is_valid():
            deadline = form.save()
            Notification.objects.create(
                user=request.user,
                task=deadline.task,
                message=f"Deadline '{deadline.title}' updated"
            )
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'item': {
                        'id': deadline.id,
                        'title': deadline.title,
                        'due_date': deadline.due_date.isoformat() if deadline.due_date else None,
                        'task_title': deadline.task.title if deadline.task else 'N/A',
                        'description': deadline.description,
                        'is_completed': deadline.is_completed,
                        'is_overdue': deadline.is_overdue
                    }
                })
            return redirect('dashboard')
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(form.errors)})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def delete_deadline(request, deadline_id):
    deadline = get_object_or_404(Deadline, id=deadline_id, owner=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        deadline.delete()
        Notification.objects.create(
            user=request.user,
            task=deadline.task,
            message=f"Deadline '{deadline.title}' deleted"
        )
        if is_ajax:
            return JsonResponse({'success': True})
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def close_deadline(request, deadline_id):
    deadline = get_object_or_404(Deadline, id=deadline_id, owner=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        deadline.is_completed = True
        deadline.save()
        Notification.objects.create(
            user=request.user,
            task=deadline.task,
            message=f"Deadline '{deadline.title}' completed"
        )
        if is_ajax:
            return JsonResponse({
                'success': True,
                'item': {
                    'id': deadline.id,
                    'title': deadline.title,
                    'due_date': deadline.due_date.isoformat() if deadline.due_date else None,
                    'task_title': deadline.task.title if deadline.task else 'N/A',
                    'description': deadline.description,
                    'is_completed': deadline.is_completed,
                    'is_overdue': deadline.is_overdue
                }
            })
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def reopen_deadline(request, deadline_id):
    deadline = get_object_or_404(Deadline, id=deadline_id, owner=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        deadline.is_completed = False
        deadline.save()
        Notification.objects.create(
            user=request.user,
            task=deadline.task,
            message=f"Deadline '{deadline.title}' reopened"
        )
        if is_ajax:
            return JsonResponse({
                'success': True,
                'item': {
                    'id': deadline.id,
                    'title': deadline.title,
                    'due_date': deadline.due_date.isoformat() if deadline.due_date else None,
                    'task_title': deadline.task.title if deadline.task else 'N/A',
                    'description': deadline.description,
                    'is_completed': deadline.is_completed,
                    'is_overdue': deadline.is_overdue
                }
            })
        return redirect('dashboard')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')