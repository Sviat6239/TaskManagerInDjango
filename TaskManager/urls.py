from django.contrib import admin
from django.urls import path, include
from taskapp.views import (  
    index, about, contact, dashboard, create_task, update_task, delete_task,
    complete_task, create_project, update_project, delete_project, add_comment,
    update_comment, delete_comment, add_issue, update_issue, delete_issue,
    close_issue, add_label, update_label, delete_label, create_invitation,
    share_profile, view_profile, add_friend, remove_friend,
    friends_list, accept_friend_invitation, task_detail, project_detail, comment_detail, issue_detail, label_detail
)
from auth_app.views import login_view, register, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('dashboard/', dashboard, name='dashboard'),
    path('create-task/', create_task, name='create_task'),
    path('update-task/<int:task_id>/', update_task, name='update_task'),
    path('delete-task/<int:task_id>/', delete_task, name='delete_task'),
    path('complete-task/<int:task_id>/', complete_task, name='complete_task'),
    path('create-project/', create_project, name='create_project'),
    path('update-project/<int:project_id>/', update_project, name='update_project'),
    path('delete-project/<int:project_id>/', delete_project, name='delete_project'),
    path('add-comment/', add_comment, name='add_comment'),
    path('update-comment/<int:comment_id>/', update_comment, name='update_comment'),
    path('delete-comment/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('add-issue/', add_issue, name='add_issue'),
    path('update-issue/<int:issue_id>/', update_issue, name='update_issue'),
    path('delete-issue/<int:issue_id>/', delete_issue, name='delete_issue'),
    path('close-issue/<int:issue_id>/', close_issue, name='close_issue'),
    path('add-label/', add_label, name='add_label'),
    path('update-label/<int:label_id>/', update_label, name='update_label'),
    path('delete-label/<int:label_id>/', delete_label, name='delete_label'),
    path('invite/', create_invitation, name='create_invitation'),
    path('share-profile/', share_profile, name='share_profile'),
    path('profile/<int:user_id>/', view_profile, name='view_profile'),
    path('add-friend/<int:user_id>/', add_friend, name='add_friend'),
    path('remove-friend/<int:user_id>/', remove_friend, name='remove_friend'),
    path('friends/', friends_list, name='friends_list'),
    path('friends/<int:user_id>/', friends_list, name='friends_list_other'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('accept-friend/<int:invitation_id>/', accept_friend_invitation, name='accept_friend_invitation'),

    path('task/<int:task_id>/', task_detail, name='task_detail'),
    path('project/<int:project_id>/', project_detail, name='project_detail'),
    path('comment/<int:comment_id>/', comment_detail, name='comment_detail'),
    path('issue/<int:issue_id>/', issue_detail, name='issue_detail'),
    path('label/<int:label_id>/', label_detail, name='label_detail'),
]