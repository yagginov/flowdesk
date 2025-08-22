from django.urls import path

from flowdesk.views import (
    IndexView,
    WorkspaceDetailView,
    WorkspaceMembersView,
    BoardDetailView,
)

app_name = "flowdesk"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path(
        "workspaces/<int:pk>/", WorkspaceDetailView.as_view(), name="workspace-detail"
    ),
    path(
        "workspaces/<int:pk>/members", WorkspaceMembersView.as_view(), name="workspace-members"
    ),
    path(
        "boards/<int:pk>/", BoardDetailView.as_view(), name="board-detail"
    ),
]
