from django.db import models
from auth_app.models import CustomUser

class Task(models.Model):
    access = models.ManyToManyField(CustomUser, related_name='shared_tasks', help_text="Users with access to the task")
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True, help_text="Attach a file")
    completed = models.BooleanField(default=False, help_text="Mark as completed")
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(help_text="Enter the task deadline")
    description = models.TextField(help_text="Enter the task description")
    stage = models.PositiveIntegerField(default=0, help_text="Enter the task stage")
    title = models.CharField(max_length=100, help_text="Enter the task title")
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(CustomUser, related_name='tasks', on_delete=models.CASCADE, help_text="Task owner")

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return self.title

class Comment(models.Model):
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True, help_text="Attach a file")
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE, help_text="Related task")
    text = models.TextField(help_text="Enter the comment text")
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(CustomUser, related_name='comments', on_delete=models.CASCADE, help_text="Comment author")

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return self.text

class Issue(models.Model):
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True, help_text="Attach a file")
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, related_name='issues', on_delete=models.CASCADE, help_text="Related task")
    text = models.TextField(help_text="Enter the issue description")
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(CustomUser, related_name='issues', on_delete=models.CASCADE, help_text="Issue reporter")

    class Meta:
        verbose_name = "Issue"
        verbose_name_plural = "Issues"

    def __str__(self):
        return self.text

class Project(models.Model):
    name = models.CharField(max_length=100, help_text="Enter the project name")
    description = models.TextField(help_text="Enter the project description", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(CustomUser, related_name='projects', on_delete=models.CASCADE, help_text="Project owner")
    members = models.ManyToManyField(CustomUser, related_name='project_members', help_text="Project members")
    tasks = models.ManyToManyField(Task, related_name='projects', help_text="Tasks in this project")

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.name

class Label(models.Model):
    name = models.CharField(max_length=50, help_text="Enter the label name")
    color = models.CharField(max_length=7, help_text="Enter the label color in HEX format", null=True, blank=True)
    tasks = models.ManyToManyField(Task, related_name='labels', help_text="Tasks with this label")

    class Meta:
        verbose_name = "Label"
        verbose_name_plural = "Labels"

    def __str__(self):
        return self.name

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, related_name='notifications', on_delete=models.CASCADE, help_text="Notification recipient")
    task = models.ForeignKey(Task, related_name='notifications', on_delete=models.CASCADE, help_text="Related task")
    message = models.TextField(help_text="Notification message")
    read = models.BooleanField(default=False, help_text="Mark as read")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"Notification for {self.user} about {self.task}"

class Deadline(models.Model):
    title = models.CharField(max_length=100, help_text="Enter the deadline title")
    due_date = models.DateTimeField(help_text="Enter the deadline due date")
    is_completed = models.BooleanField(default=False, help_text="Mark as completed")
    task = models.ForeignKey(
        Task, 
        related_name='deadlines', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        help_text="Related task (optional)"
    )
    owner = models.ForeignKey(
        CustomUser, 
        related_name='deadlines', 
        on_delete=models.CASCADE, 
        help_text="Deadline owner"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(
        null=True, 
        blank=True, 
        help_text="Enter the deadline description (optional)"
    )

    class Meta:
        verbose_name = "Deadline"
        verbose_name_plural = "Deadlines"
        ordering = ['due_date'] 

    def __str__(self):
        return f"{self.title} (Due: {self.due_date})"

    def is_overdue(self):
        from django.utils import timezone
        return not self.is_completed and self.due_date < timezone.now()