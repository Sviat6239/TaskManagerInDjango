from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST

from .forms import TaskForm, ProjectForm, CommentForm, IssueForm, LabelForm
from .models import Task, Project, Comment, Issue, Label, Notification
from auth_app.models import CustomUser, Invitation
from datetime import datetime, timedelta


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
    labels = Label.objects.filter(tasks__user=request.user).distinct()
    notifications = Notification.objects.filter(user=request.user, read=False)
    sent_invitations = Invitation.objects.filter(sender=request.user)
    received_invitations = Invitation.objects.filter(recipient_email=request.user.email, is_used=False)

    return render(request, 'dashboard.html', {
        'tasks': tasks,
        'projects': projects,
        'comments': comments,
        'issues': issues,
        'labels': labels,
        'notifications': notifications,
        'sent_invitations': sent_invitations,
        'received_invitations': received_invitations,
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

            project_id = request.POST.get('project_id')
            if project_id:
                from .models import Project
                try:
                    project = Project.objects.get(id=project_id, owner=request.user)
                    project.tasks.add(task)
                except Project.DoesNotExist:
                    pass

            return redirect('dashboard')
    else:
        project_id = request.GET.get('project_id')
        initial = {'project': project_id} if project_id else {}
        form = TaskForm(initial=initial)

    return render(request, 'create_task.html', {
        'form': form,
        'project_id': project_id if project_id else None
    })


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
    if request.method == 'POST':
        try:
            task = get_object_or_404(Task, id=task_id, user=request.user)
            task.delete()
            return JsonResponse({'success': True, 'message': 'Task deleted successfully'})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


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
        name = request.POST.get('name')
        description = request.POST.get('description')
        task_ids = request.POST.getlist('tasks')
        new_tasks = request.POST.getlist('new_tasks[]')

        project = Project.objects.create(
            name=name,
            description=description,
            owner=request.user
        )

        if task_ids:
            tasks = Task.objects.filter(id__in=task_ids, user=request.user)
            project.tasks.set(tasks)

        default_deadline = datetime.now() + timedelta(days=7)
        for task_title in new_tasks:
            if task_title.strip():
                task = Task.objects.create(
                    title=task_title,
                    user=request.user,
                    deadline=default_deadline
                )
                project.tasks.add(task)

        return redirect('dashboard')
    return redirect('dashboard')


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
@require_POST
def add_comment(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        task_id = request.POST.get('task_id')
        project_id = request.POST.get('project_id')
        parent_id = request.POST.get('parent_id')

        if not text or not text.strip():
            return JsonResponse({'success': False, 'error': 'Comment text cannot be empty'}, status=400)

        try:
            if task_id and project_id:
                return JsonResponse({'success': False, 'error': 'Cannot comment on both task and project'}, status=400)
            elif task_id:
                task = Task.objects.get(id=task_id)
                comment = Comment.objects.create(
                    user=request.user,
                    text=text,
                    task=task,
                    parent=Comment.objects.get(id=parent_id) if parent_id else None
                )
            elif project_id:
                project = Project.objects.get(id=project_id)
                comment = Comment.objects.create(
                    user=request.user,
                    text=text,
                    project=project,
                    parent=Comment.objects.get(id=parent_id) if parent_id else None
                )
            else:
                return JsonResponse({'success': False, 'error': 'Task or project ID is required'}, status=400)

            return JsonResponse({
                'success': True,
                'message': 'Comment added successfully',
                'comment': {
                    'id': comment.id,
                    'text': comment.text,
                    'created_at': comment.created_at.isoformat(),
                    'author': comment.user.email if comment.user else None,
                    'parent_id': comment.parent.id if comment.parent else None
                }
            })
        except (Task.DoesNotExist, Project.DoesNotExist, Comment.DoesNotExist) as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


@login_required
@require_POST
def update_comment(request, comment_id):
    if request.method == 'POST':
        print(f"Updating comment with ID: {comment_id}")
        try:
            comment = get_object_or_404(Comment, id=comment_id, user=request.user)
            text = request.POST.get('text')
            if text and text.strip():
                comment.text = text
                comment.save()
                print(f"Comment {comment_id} updated successfully")
                return JsonResponse({
                    'success': True,
                    'comment': {
                        'id': comment.id,
                        'text': comment.text,
                        'created_at': comment.created_at.isoformat(),
                        'author': comment.user.email if comment.user else None,
                        'parent_id': comment.parent.id if comment.parent else None
                    }
                })
            else:
                return JsonResponse({'success': False, 'error': 'Comment text cannot be empty'}, status=400)
        except Exception as e:
            print(f"Error updating comment {comment_id}: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=404)

@login_required
@require_POST
def delete_comment(request, comment_id):
    if request.method == 'POST':
        print(f"Deleting comment with ID: {comment_id}")
        try:
            comment = get_object_or_404(Comment, id=comment_id, user=request.user)
            comment.delete()
            print(f"Comment {comment_id} deleted successfully")
            return JsonResponse({'success': True, 'message': 'Comment deleted'})
        except Exception as e:
            print(f"Error deleting comment {comment_id}: {str(e)}")  # Лог ошибки
            return JsonResponse({'success': False, 'error': str(e)}, status=404)


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

@login_required
def create_invitation(request):
    if request.method == 'POST':
        recipient_email = request.POST.get('email')
        invitation_type = request.POST.get('invitation_type', 'registration')
        if recipient_email:
            invitation = Invitation.objects.create(
                sender=request.user,
                recipient_email=recipient_email,
                invitation_type=invitation_type
            )
            invite_link = request.build_absolute_uri(f"/accept-invite/{invitation.id}/")
            try:
                send_mail(
                    f'You’re Invited to Tasker {"as a Friend" if invitation_type == "friendship" else ""}!',
                    f'Join Tasker using this link: {invite_link}',
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient_email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send email: {e}")
                return render(request, 'create_invitation.html', {'error': 'Failed to send invitation.'})
            return redirect('dashboard')
    return render(request, 'create_invitation.html')

@login_required
def accept_friend_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id, invitation_type='friendship', is_used=False)
    if invitation.recipient_email != request.user.email:
        return redirect('dashboard')

    sender = invitation.sender
    recipient = request.user
    if sender not in recipient.friends.all():
        recipient.friends.add(sender)

    invitation.is_used = True
    invitation.save()

    other_invitations = Invitation.objects.filter(
        sender=sender,
        recipient_email=recipient.email,
        invitation_type='friendship',
        is_used=False
    )
    for inv in other_invitations:
        inv.is_used = True
        inv.save()

    return redirect('dashboard')

@login_required
def share_profile(request):
    profile_link = request.build_absolute_uri(f"/profile/{request.user.id}/")
    return render(request, 'share_profile.html', {'profile_link': profile_link})

def view_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    is_friend = request.user.is_authenticated and user in request.user.friends.all()
    return render(request, 'view_profile.html', {
        'profile_user': user,
        'is_friend': is_friend,
        'friends_count': user.friends.count(),
    })

@login_required
def add_friend(request, user_id):
    friend = get_object_or_404(CustomUser, id=user_id)
    if friend != request.user and friend not in request.user.friends.all():
        request.user.friends.add(friend)
    return redirect('view_profile', user_id=user_id)

@login_required
def remove_friend(request, user_id):
    friend = get_object_or_404(CustomUser, id=user_id)
    if friend in request.user.friends.all():
        request.user.friends.remove(friend)
    return redirect('view_profile', user_id=user_id)

@login_required
def friends_list(request, user_id=None):
    if user_id:
        user = get_object_or_404(CustomUser, id=user_id)
    else:
        user = request.user
    friends = user.friends.all()
    return render(request, 'friends_list.html', {'profile_user': user, 'friends': friends})

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    return render(request, 'task_detail.html', {'task': task})

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    return render(request, 'project_detail.html', {'project': project})


@login_required
def comment_detail(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    return render(request, 'comment_detail.html', {'comment': comment})


@login_required
def issue_detail(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id, user=request.user)
    return render(request, 'issue_detail.html', {'issue': issue})


@login_required
def label_detail(request, label_id):
    label = get_object_or_404(Label, id=label_id, tasks__user=request.user)
    return render(request, 'label_detail.html', {'label': label})


def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'task_list.html', {'tasks': tasks})


def project_list(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', {'projects': projects})


def comment_list(request):
    comments = Comment.objects.filter(parent__isnull=True)
    return render(request, 'comment_list.html', {'comments': comments})


def issue_list(request):
    issues = Issue.objects.all()
    return render(request, 'issue_list.html', {'issues': issues})


def label_list(request):
    labels = Label.objects.all()
    return render(request, 'label_list.html', {'labels': labels})


@login_required
def load_more_comments(request):
    project_id = request.GET.get('project_id')
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 6))

    try:
        project = Project.objects.get(id=project_id)
        comments = project.comments.all().order_by('-created_at')[offset:offset + limit]
        data = {
            'comments': [],
            'has_more': False
        }
        for comment in comments:
            comment_data = {
                'id': comment.id,
                'text': comment.text,
                'created_at': comment.created_at.isoformat(),
                'author': comment.user.email if comment.user else None,
                'replies': [
                    {
                        'id': reply.id,
                        'text': reply.text,
                        'created_at': reply.created_at.isoformat(),
                        'author': reply.user.email if reply.user else None
                    } for reply in comment.replies.all()[:3]
                ]
            }
            data['comments'].append(comment_data)
        if project.comments.count() > offset + limit:
            data['has_more'] = True
        return JsonResponse(data)
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)

@login_required
def load_comment_options(request):
    project_id = request.GET.get('project_id')
    try:
        project = Project.objects.get(id=project_id)
        options = []
        for comment in project.comments.all():
            truncated_text = comment.text[:20] + '...' if len(comment.text) > 20 else comment.text
            options.append(f'<option value="{comment.id}">{truncated_text}</option>')
            for reply in comment.replies.all():
                truncated_reply = reply.text[:20] + '...' if len(reply.text) > 20 else reply.text
                options.append(f'<option value="{reply.id}">↳ {truncated_reply}</option>')
        return JsonResponse({'options': options})
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)