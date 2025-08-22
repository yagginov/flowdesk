from django.http import HttpRequest, HttpResponse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Max


from flowdesk.models import (
    Board,
    Workspace,
    WorkspaceMember,
    List,
)
from flowdesk.forms import (
    WorkspaceForm,
    BoardForm,
    ListForm
)


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


class WorkspaceCreateView(LoginRequiredMixin, generic.CreateView):
    model = Workspace
    form_class = WorkspaceForm
    success_url = reverse_lazy("flowdesk:index")

    def form_valid(self, form: WorkspaceForm) -> HttpResponse:
        self.object = form.save()

        WorkspaceMember.objects.create(
            user=self.request.user,
            workspace=self.object,
            role=WorkspaceMember.Roles.OWNER,
        )

        return super().form_valid(form)


class BoardCreateView(LoginRequiredMixin, generic.CreateView):
    model = Board
    form_class = BoardForm
    success_url = reverse_lazy("flowdesk:index")

    def form_valid(self, form: BoardForm) -> HttpResponse:
        workspace = get_object_or_404(Workspace, pk=self.kwargs["workspace_pk"])
        form.instance.workspace = workspace
        return super().form_valid(form)


class ListCreateView(LoginRequiredMixin, generic.CreateView):
    model = List
    form_class = ListForm
    success_url = reverse_lazy("flowdesk:index")

    def form_valid(self, form: ListForm) -> HttpResponse:
        board = get_object_or_404(Board, pk=self.kwargs["board_pk"])
        form.instance.board = board

        last_position = board.lists.aggregate(Max("position"))["position__max"]
        form.instance.position = (last_position or 0) + 1
        return super().form_valid(form)
