from django.contrib import admin
from .models import Task, Comment, Project, Label, Issue, Notification, Deadline
from auth_app.models import CustomUser


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'deadline', 'completed', 'stage') 
    list_filter = ('completed', 'user') 
    search_fields = ('title', 'description')
    date_hierarchy = 'deadline'  

admin.site.register(Task, TaskAdmin)
admin.site.register(Comment)
admin.site.register(Project)
admin.site.register(Label)
admin.site.register(Issue)
admin.site.register(Notification)
admin.site.register(Deadline)
admin.site.register(CustomUser)

