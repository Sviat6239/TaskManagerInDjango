from django.db import models
from auth_app.models import CustomUser

class Task(models.Model):
    access = models.ManyToManyField(CustomUser, related_name='shared_tasks', blank=True)
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    stage = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(CustomUser, related_name='tasks', on_delete=models.CASCADE)
    labels = models.ManyToManyField('Label', related_name='task_labels', blank=True)

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return self.title

class Comment(models.Model):
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey('Project', related_name='comments', on_delete=models.CASCADE, null=True, blank=True)  # Добавлено для проектов
    text = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(CustomUser, related_name='comments', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)  # Для ответов на комментарии

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return self.text[:50]

class Issue(models.Model):
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, related_name='issues', on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(CustomUser, related_name='issues', on_delete=models.CASCADE)
    closed = models.BooleanField(default=False)
    labels = models.ManyToManyField('Label', related_name='issue_labels', blank=True)

    class Meta:
        verbose_name = "Issue"
        verbose_name_plural = "Issues"

    def __str__(self):
        return self.text or "Unnamed Issue"

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(CustomUser, related_name='projects', on_delete=models.CASCADE)
    members = models.ManyToManyField(CustomUser, related_name='project_members', blank=True)
    tasks = models.ManyToManyField(Task, related_name='projects', blank=True)
    labels = models.ManyToManyField('Label', related_name='project_labels', blank=True)  # Уже есть, но подтверждаем

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.name

class Deadline(models.Model):
    task = models.ForeignKey(Task, related_name='deadlines', on_delete=models.CASCADE)
    due_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(CustomUser, related_name='deadlines', on_delete=models.CASCADE)
    labels = models.ManyToManyField('Label', related_name='deadline_labels', blank=True)

    class Meta:
        verbose_name = "Deadline"
        verbose_name_plural = "Deadlines"

    def __str__(self):
        return f"Deadline for {self.task}"

class Label(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, null=True, blank=True)
    tasks = models.ManyToManyField('Task', related_name='task_labels', blank=True)
    deadlines = models.ManyToManyField('Deadline', related_name='deadline_labels', blank=True)
    projects = models.ManyToManyField('Project', related_name='project_labels', blank=True)  # Уже есть, подтверждаем

    class Meta:
        verbose_name = "Label"
        verbose_name_plural = "Labels"

    def __str__(self):
        return self.name

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, related_name='notifications', on_delete=models.CASCADE)
    task = models.ForeignKey(Task, related_name='notifications', on_delete=models.CASCADE)
    message = models.TextField(null=True, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    labels = models.ManyToManyField('Label', related_name='notification_labels', blank=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"Notification for {self.user} about {self.task}"