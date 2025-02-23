"""
URL configuration for TaskManager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from auth_app.views import register, login_view, logout_view
from taskapp.views import (
    index, about, contact,
    dashboard, create_task, update_task, delete_task,
    create_project, update_project, delete_project,
    add_comment, update_comment, delete_comment,
    add_issue, update_issue, delete_issue,
    add_label, update_label, delete_label,
    close_issue, reopen_issue,
    create_deadline, update_deadline, delete_deadline, close_deadline, reopen_deadline
)
urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('dashboard/', dashboard, name='dashboard'),

    # Task
    path('dashboard/create_task/', create_task, name='create_task'),
    path('dashboard/task/<int:task_id>/update/', update_task, name='update_task'),
    path('dashboard/task/<int:task_id>/delete/', delete_task, name='delete_task'),

    # Project
    path('dashboard/create_project/', create_project, name='create_project'),
    path('dashboard/project/<int:project_id>/update/', update_project, name='update_project'),
    path('dashboard/project/<int:project_id>/delete/', delete_project, name='delete_project'),

    # Comment
    path('dashboard/add_comment/', add_comment, name='add_comment'),
    path('dashboard/comment/<int:comment_id>/update/', update_comment, name='update_comment'),
    path('dashboard/comment/<int:comment_id>/delete/', delete_comment, name='delete_comment'),

    # Issue
    path('dashboard/add_issue/', add_issue, name='add_issue'),
    path('dashboard/issue/<int:issue_id>/update/', update_issue, name='update_issue'),
    path('dashboard/issue/<int:issue_id>/delete/', delete_issue, name='delete_issue'),
    path('dashboard/issue/<int:issue_id>/close/', close_issue, name='close_issue'),
    path('dashboard/issue/<int:issue_id>/reopen/', reopen_issue, name='reopen_issue'),

    # Label
    path('dashboard/add_label/', add_label, name='add_label'),
    path('dashboard/label/<int:label_id>/update/', update_label, name='update_label'),
    path('dashboard/label/<int:label_id>/delete/', delete_label, name='delete_label'),

    # Deadline
    path('dashboard/create_deadline/', create_deadline, name='create_deadline'),
    path('dashboard/deadline/<int:deadline_id>/update/', update_deadline, name='update_deadline'),
    path('dashboard/deadline/<int:deadline_id>/delete/', delete_deadline, name='delete_deadline'),
    path('dashboard/deadline/<int:deadline_id>/close/', close_deadline, name='close_deadline'),
    path('dashboard/deadline/<int:deadline_id>/reopen/', reopen_deadline, name='reopen_deadline'),

    path('admin/', admin.site.urls),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
