from django.contrib import admin
from django.urls import path
from auth_app.views import register, login_view, logout_view
from taskapp.views import (
    index, about, contact, dashboard,
    create_task, update_task, delete_task, complete_task,
    create_project, update_project, delete_project,
    add_comment, update_comment, delete_comment,
    add_issue, update_issue, delete_issue, close_issue,
    add_label, update_label, delete_label
)

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('dashboard/', dashboard, name='dashboard'),
    path('task/create/', create_task, name='create_task'),
    path('task/<int:task_id>/update/', update_task, name='update_task'),
    path('task/<int:task_id>/delete/', delete_task, name='delete_task'),
    path('task/<int:task_id>/complete/', complete_task, name='complete_task'),
    path('project/create/', create_project, name='create_project'),
    path('project/<int:project_id>/update/', update_project, name='update_project'),
    path('project/<int:project_id>/delete/', delete_project, name='delete_project'),
    path('comment/add/', add_comment, name='add_comment'),
    path('comment/<int:comment_id>/update/', update_comment, name='update_comment'),
    path('comment/<int:comment_id>/delete/', delete_comment, name='delete_comment'),
    path('issue/add/', add_issue, name='add_issue'),
    path('issue/<int:issue_id>/update/', update_issue, name='update_issue'),
    path('issue/<int:issue_id>/delete/', delete_issue, name='delete_issue'),
    path('issue/<int:issue_id>/close/', close_issue, name='close_issue'),
    path('label/add/', add_label, name='add_label'),
    path('label/<int:label_id>/update/', update_label, name='update_label'),
    path('label/<int:label_id>/delete/', delete_label, name='delete_label'),
    path('admin/', admin.site.urls),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
