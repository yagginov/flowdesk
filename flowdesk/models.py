from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class WorkspaceMember(models.Model):
    class Roles(models.TextChoices):
        OWNER = "OWNER", "Owner"
        ADMIN = "ADMIN", "Admin"
        USER = "USER", "User"
        GUEST = "GUEST", "Guest"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="workspace_memberships"
    )
    workspace = models.ForeignKey(
        "Workspace",
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    role = models.CharField(max_length=15, choices=Roles.choices, default=Roles.GUEST)


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

    class Meta:
        ordering = ("position", )
        constraints = (
            models.UniqueConstraint(
                fields=("board", "position"), name="unique_list_position_per_board"
            ),
        )

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=63)

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        URGENT = "URGENT", "Urgent"
        CRITICAL = "CRITICAL", "Critical"

    class Status(models.TextChoices):
        TODO = "TODO", "To Do"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        BLOCKED = "BLOCKED", "Blocked"
        REVIEW = "REVIEW", "In Review"
        DONE = "DONE", "Done"
        ARCHIVED = "ARCHIVED", "Archived"

    title = models.CharField(max_length=63)
    description = models.TextField()
    priority = models.CharField(max_length=15, choices=Priority.choices, default=Priority.LOW)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.TODO)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True)
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name="tasks")
    tags = models.ManyToManyField(Tag, related_name="tasks")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_tasks"
    )
    members = models.ManyToManyField(User, related_name="tasks")
    position = models.IntegerField()

    class Meta:
        ordering = (
            "-priority",
            "deadline",
            "title",
        )

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    text = models.CharField(max_length=511)
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.text[:63]}..."
