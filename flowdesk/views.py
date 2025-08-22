from django.http import HttpRequest, HttpResponse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404


from flowdesk.models import Board, Workspace, List


class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = "flowdesk/index.html"


class WorkspaceDetailView(LoginRequiredMixin, generic.DetailView):
    model = Workspace
    queryset = Workspace.objects.prefetch_related("boards")
    template_name = "flowdesk/workspace_detail.html"


class WorkspaceMembersView(LoginRequiredMixin, generic.DetailView):
    model = Workspace
    queryset = Workspace.objects.prefetch_related(
        "memberships__user__position"
    )
    template_name = "flowdesk/workspace_members.html"


class BoardDetailView(LoginRequiredMixin, generic.DetailView):
    model = Board
    queryset = Board.objects.prefetch_related("lists")
    template_name = "flowdesk/board_detail.html"
