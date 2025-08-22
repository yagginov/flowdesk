from django.contrib import admin

from flowdesk.models import WorkspaceMember, Workspace, Board, List, Tag, Task, Comment


@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "workspace",
        "role",
    )


@admin.register(Workspace)
class Workspace(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "created_at",
    )


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "created_at",
    )


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ("name", "board", "position")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "priority",
        "status",
        "deadline",
        "created_by",
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("text", "created_at", "task", "created_by")
