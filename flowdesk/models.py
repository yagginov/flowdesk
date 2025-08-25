from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class LogerBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

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


class Workspace(LogerBaseModel):
    name = models.CharField(max_length=63)
    description = models.CharField(max_length=511, blank=True)
    members = models.ManyToManyField(
        User, blank=True, through=WorkspaceMember, related_name="workspaces"
    )

    def __str__(self) -> str:
        return self.name


class Board(LogerBaseModel):
    name = models.CharField(max_length=63)
    description = models.CharField(max_length=511, blank=True)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="boards"
    )

    def __str__(self) -> str:
        return self.name


class List(LogerBaseModel):
    name = models.CharField(max_length=63)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="lists")
    position = models.IntegerField()

    class Meta:
        ordering = ("position", )

    def __str__(self) -> str:
        return self.name


class Tag(LogerBaseModel):
    name = models.CharField(max_length=63)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="tags"
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("name", "workspace"),
                name="name_workspace_unique_constraint"
            ),
        )

    def __str__(self) -> str:
        return self.name


class Task(LogerBaseModel):
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
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=15, choices=Priority.choices, default=Priority.LOW)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.TODO)
    deadline = models.DateTimeField(null=True)
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name="tasks")
    tags = models.ManyToManyField(Tag, related_name="tasks", blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_tasks"
    )
    assigned_to = models.ManyToManyField(User, related_name="tasks", blank=True)
    position = models.IntegerField()
    blocking_tasks = models.ManyToManyField("Task", related_name="tasks")

    class Meta:
        ordering = (
            "position",
        )

    def __str__(self) -> str:
        return self.title


class Comment(LogerBaseModel):
    text = models.CharField(max_length=511)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.text[:63]}..."
