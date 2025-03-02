from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import TaskForm, ProjectForm, CommentForm, IssueForm, LabelForm, DeadlineForm
from .models import Task, Comment, Project, Label, Issue, Notification, Deadline
from auth_app.models import CustomUser

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contacts.html')

@login_required
def dashboard(request):
    own_tasks = Task.objects.filter(user=request.user)
    accessible_tasks = Task.objects.filter(access__contains=request.user.uid).exclude(user=request.user)
    tasks = own_tasks | accessible_tasks  
    
    projects = Project.objects.filter(owner=request.user)
    comments = Comment.objects.filter(user=request.user)
    issues = Issue.objects.filter(user=request.user)
    labels = Label.objects.all()
    deadlines = Deadline.objects.filter(owner=request.user)
    notifications = Notification.objects.filter(user=request.user, read=False)
    friends = request.user.friends.all()

    print(f"Tasks: {tasks}")
    print(f"Projects: {projects}")
    print(f"Deadlines: {deadlines}")

    context = {
        'tasks': tasks.distinct(),  
        'projects': projects,
        'comments': comments,
        'issues': issues,
        'labels': labels,
        'deadlines': deadlines,
        'notifications': notifications,
        'friends': friends,
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
def add_friend(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        friend_uid = request.POST.get('friend_uid')
        
        try:
            friend = CustomUser.objects.get(uid=friend_uid)
            if friend != request.user and request.user.add_friend(friend):
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'friend': {
                            'id': friend.id,
                            'email': friend.email,
                            'uid': friend.uid,
                            'first_name': friend.first_name,
                            'last_name': friend.last_name
                        }
                    })
                return redirect('dashboard')
            else:
                error_msg = 'User is already your friend or invalid operation'
        except CustomUser.DoesNotExist:
            error_msg = 'User with this UID does not exist'

        if is_ajax:
            return JsonResponse({'success': False, 'error': error_msg})
        return redirect('dashboard')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def remove_friend(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        friend_uid = request.POST.get('friend_uid')
        
        try:
            friend = CustomUser.objects.get(uid=friend_uid)
            if friend != request.user and request.user.remove_friend(friend):
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'friend': {
                            'id': friend.id,
                            'email': friend.email,
                            'uid': friend.uid,
                            'first_name': friend.first_name,
                            'last_name': friend.last_name
                        }
                    })
                return redirect('dashboard')
            else:
                error_msg = 'User is not your friend or invalid operation'
        except CustomUser.DoesNotExist:
            error_msg = 'User with this UID does not exist'

        if is_ajax:
            return JsonResponse({'success': False, 'error': error_msg})
        return redirect('dashboard')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def manage_task_access(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        friend_uid = request.POST.get('friend_uid')
        action = request.POST.get('action')

        try:
            friend = CustomUser.objects.get(uid=friend_uid)
            if friend not in request.user.friends.all():
                raise ValueError("This user is not your friend")

            if action == 'add':
                success = task.add_friend_access(friend_uid)
                message = f"Access granted to {friend.email} for task '{task.title}'"
            elif action == 'remove':
                success = task.remove_friend_access(friend_uid)
                message = f"Access removed for {friend.email} from task '{task.title}'"
            else:
                raise ValueError("Invalid action")

            if success:
                task.save()
                Notification.objects.create(
                    user=request.user,
                    task=task,
                    message=message
                )
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'task_id': task.id,
                        'access_uids': task.get_access_uids()
                    })
            else:
                error_msg = 'No changes made to access'

        except CustomUser.DoesNotExist:
            error_msg = 'User with this UID does not exist'
        except ValueError as e:
            error_msg = str(e)

        if is_ajax:
            return JsonResponse({'success': False, 'error': error_msg})
        return redirect('dashboard')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

@login_required
@csrf_exempt
def get_friends(request):
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        friends = request.user.friends.all().values(
            'id', 'email', 'uid', 'first_name', 'last_name'
        )
        return JsonResponse({'success': True, 'friends': list(friends)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
@csrf_exempt
def get_access_list(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        access_list = task.get_access_uids()
        return JsonResponse({'success': True, 'access_list': access_list})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
@csrf_exempt
def manage_task_access(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        friend_uid = request.POST.get('friend_uid')
        action = request.POST.get('action')

        try:
            friend = CustomUser.objects.get(uid=friend_uid)
            if friend not in request.user.friends.all():
                raise ValueError("This user is not your friend")

            if action == 'add':
                success = task.add_friend_access(friend_uid)
                message = f"Access granted to {friend.email} for task '{task.title}'"
            elif action == 'remove':
                success = task.remove_friend_access(friend_uid)
                message = f"Access removed for {friend.email} from task '{task.title}'"
            else:
                raise ValueError("Invalid action")

            if success:
                task.save()
                Notification.objects.create(
                    user=request.user,
                    task=task,
                    message=message
                )
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'task_id': task.id,
                        'access_uids': task.get_access_uids()
                    })
            else:
                error_msg = 'No changes made to access'

        except CustomUser.DoesNotExist:
            error_msg = 'User with this UID does not exist'
        except ValueError as e:
            error_msg = str(e)

        if is_ajax:
            return JsonResponse({'success': False, 'error': error_msg})
        return redirect('dashboard')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    return redirect('dashboard')

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
def close_task(request, task_id, complete=True):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        task.completed = complete
        task.save()
        action = "completed" if complete else "reopened"
        Notification.objects.create(
            user=request.user,
            task=task,
            message=f"Task '{task.title[:50]}...' {action}"
        )
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

@login_required
@csrf_exempt
def get_list(request, type):
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        items = []
        if type == 'task':
            own_tasks = Task.objects.filter(user=request.user)
            accessible_tasks = Task.objects.filter(access__contains=request.user.uid).exclude(user=request.user)
            tasks = (own_tasks | accessible_tasks).distinct()
            items = tasks.values('id', 'title', 'description', 'stage', 'deadline', 'completed')
        elif type == 'project':
            items = Project.objects.filter(owner=request.user).values(
                'id', 'name', 'description', 'members_count', 'tasks_count'
            )
        elif type == 'deadline':
            items = Deadline.objects.filter(owner=request.user).values(
                'id', 'title', 'due_date', 'task__title', 'description', 'is_completed', 'is_overdue'
            )
        elif type == 'comment':
            items = Comment.objects.filter(user=request.user).values(
                'id', 'text', 'task__title'
            )
        elif type == 'issue':
            items = Issue.objects.filter(user=request.user).values(
                'id', 'text', 'task__title', 'closed'
            )
        elif type == 'label':
            items = Label.objects.all().values(
                'id', 'name', 'color'
            )
        return JsonResponse({'success': True, 'items': list(items)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})