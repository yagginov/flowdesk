from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class WorkspaceMember(models.Model):
    class Roles(models.IntegerChoices):
        OWNER = 1, "Owner"
        ADMIN = 2, "Admin"
        USER = 3, "User"
        GUEST = 4, "Guest"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workspace = models.ForeignKey("Workspace", on_delete=models.CASCADE)
    role = models.IntegerField(choices=Roles, default=Roles.GUEST)


class Workspace(models.Model):
    name = models.CharField(max_length=63)
    description = models.CharField(max_length=511)
    members = models.ManyToManyField(
        User, blank=True, through=WorkspaceMember, related_name="workspaces"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Board(models.Model):
    name = models.CharField(max_length=63)
    description = models.CharField(max_length=511)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="boards"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class List(models.Model):
    name = models.CharField(max_length=63)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="lists")
    position = models.IntegerField()

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=63)

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    class Priority(models.IntegerChoices):
        LOW = 1, "Low"
        MEDIUM = 2, "Medium"
        HIGH = 3, "High"
        URGENT = 4, "Urgent"
        CRITICAL = 5, "Critical"

    title = models.CharField(max_length=63)
    description = models.TextField()
    priority = models.IntegerField(choices=Priority, default=Priority.LOW)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True)
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name="tasks")
    tags = models.ManyToManyField(Tag, related_name="tasks")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_tasks"
    )
    members = models.ManyToManyField(User, related_name="tasks")

    class Meta:
        ordering = (
            "-priority",
            "deadline",
            "title",
        )

    def __str__(self) -> str:
        return f"{self.title} - {self.description[:25]}..."


class Comment(models.Model):
    text = models.CharField(max_length=511)
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )

    def __str__(self) -> str:
        return "{self.text[:63]...}"
