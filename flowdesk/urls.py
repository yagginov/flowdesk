from django.urls import path

from flowdesk.views import (
    IndexView,
    WorkspaceDetailView,
    WorkspaceCreateView,
    WorkspaceMembersView,
    WorkspaceTagsView,
    TagCreateView,
    TagUpdateView,
    TagDeleteView,
    BoardDetailView,
    BoardCreateView,
    ListCreateView,
    TaskCreateView,
    TaskDetailView,
    ListOrderUpdate,
    TaskOrderUpdate,
)

app_name = "flowdesk"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path(
        "workspaces/<int:pk>/", WorkspaceDetailView.as_view(), name="workspace-detail"
    ),
    path("workspaces/create/", WorkspaceCreateView.as_view(), name="workspace-create"),
    path(
        "workspaces/<int:pk>/members/",
        WorkspaceMembersView.as_view(),
        name="workspace-members",
    ),
    path(
        "workspaces/<int:pk>/tags/",
        WorkspaceTagsView.as_view(),
        name="workspace-tags",
    ),
    path(
        "workspaces/<int:workspace_pk>/tags/create/",
        TagCreateView.as_view(),
        name="tag-create",
    ),
    path(
        "workspaces/<int:workspace_pk>tags/<int:pk>/update/",
        TagUpdateView.as_view(),
        name="tag-update",
    ),
    path(
        "workspaces/<int:workspace_pk>tags/<int:pk>/delete/",
        TagDeleteView.as_view(),
        name="tag-delete",
    ),
    path(
        "workspaces/<int:workspace_pk>/boards/create/",
        BoardCreateView.as_view(),
        name="board-create",
    ),
    path("workspaces/<int:workspace_pk>/boards/<int:pk>/", BoardDetailView.as_view(), name="board-detail"),
    path(
        "workspaces/<int:workspace_pk>/boards/<int:board_pk>/lists/create/",
        ListCreateView.as_view(),
        name="list-create",
    ),
    path(
        "workspaces/<int:workspace_pk>/boards/<int:board_pk>/lists/<int:list_pk>/tasks/create/",
        TaskCreateView.as_view(),
        name="task-create",
    ),
    path(
        "workspaces/<int:workspace_pk>/boards/<int:board_pk>/lists/<int:list_pk>/tasks/<int:pk>/",
        TaskDetailView.as_view(),
        name="task-detail",
    ),
    path(
        "workspaces/<int:workspace_pk>/boards/<int:board_pk>/lists/order/",
        ListOrderUpdate.as_view(),
        name="update-list-order",
    ),
    path(
        "workspaces/<int:workspace_pk>/boards/<int:board_pk>/tasks/order/",
        TaskOrderUpdate.as_view(),
        name="update-task-order",
    ),
]
