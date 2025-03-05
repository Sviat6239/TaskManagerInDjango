from django.contrib import admin
from .models import Task, Comment, Project, Label, Issue, Notification, Deadline

admin.site.register(Task)
admin.site.register(Comment)
admin.site.register(Project)
admin.site.register(Label)
admin.site.register(Issue)
admin.site.register(Notification)
admin.site.register(Deadline)