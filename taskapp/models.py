from django.db import models
from  auth_app.models import CustomUser

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    stage = models.IntegerField(default=0)
    deadline = models.DateTimeField()
    user = models.ForeignKey('auth.User', related_name='tasks', on_delete=models.CASCADE)
    access = models.ManyToManyField('auth.User', related_name='shared_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title