from django.urls import path

from flowdesk.views import (
    IndexView,
    WorkspaceDetailView,
    WorkspaceCreateView,
    WorkspaceMembersView,
    BoardDetailView,
    BoardCreateView,
    ListCreateView,
)

app_name = "flowdesk"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path(
        "workspaces/<int:pk>/", WorkspaceDetailView.as_view(), name="workspace-detail"
    ),
    path(
        "workspaces/create/", WorkspaceCreateView.as_view(), name="workspace-create"
    ),
    path(
        "workspaces/<int:pk>/members/", WorkspaceMembersView.as_view(), name="workspace-members"
    ),
    path(
        "workspaces/<int:workspace_pk>/boards/create/", BoardCreateView.as_view(), name="board-create"
    ),
    path(
        "boards/<int:pk>/", BoardDetailView.as_view(), name="board-detail"
    ),
    path(
        "boards/<int:board_pk>/lists/create", ListCreateView.as_view(), name="list-create"
    ),
]
