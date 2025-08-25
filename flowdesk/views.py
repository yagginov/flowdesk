import json

from django.http import HttpRequest, HttpResponse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.db.models import Max, QuerySet

from flowdesk.models import (
    Board,
    Workspace,
    WorkspaceMember,
    List,
    Task,
)
from flowdesk.forms import (
    WorkspaceForm,
    BoardForm,
    ListForm,
    TaskForm,
)


class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = "flowdesk/index.html"


class WorkspaceDetailView(LoginRequiredMixin, generic.DetailView):
    model = Workspace
    queryset = Workspace.objects.prefetch_related("boards")
    template_name = "flowdesk/workspace_detail.html"

    def get_queryset(self) -> QuerySet:
        queryset = Workspace.objects.filter(
            members=self.request.user.pk
        ).prefetch_related(
            "boards"
        )
        return queryset


class WorkspaceMembersView(LoginRequiredMixin, generic.DetailView):
    model = Workspace
    template_name = "flowdesk/workspace_members.html"

    def get_queryset(self) -> QuerySet:
        return Workspace.objects.filter(
            members=self.request.user.pk
        ).prefetch_related(
            "memberships__user__position"
        )


class BoardDetailView(LoginRequiredMixin, generic.DetailView):
    model = Board
    template_name = "flowdesk/board_detail.html"

    def get_queryset(self) -> QuerySet:
        return Board.objects.filter(
            workspace__members=self.request.user.pk
        ).prefetch_related(
            "lists"
        )


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

    def get_success_url(self):
        return reverse("flowdesk:workspace-detail", args=(self.kwargs["workspace_pk"], ))

    def form_valid(self, form: BoardForm) -> HttpResponse:
        workspace = get_object_or_404(Workspace, pk=self.kwargs["workspace_pk"])
        form.instance.workspace = workspace
        return super().form_valid(form)


class ListCreateView(LoginRequiredMixin, generic.CreateView):
    model = List
    form_class = ListForm

    def get_success_url(self):
        return reverse("flowdesk:board-detail", args=(self.kwargs["board_pk"], ))

    def form_valid(self, form: ListForm) -> HttpResponse:
        board = get_object_or_404(Board, pk=self.kwargs["board_pk"])
        form.instance.board = board

        last_position = board.lists.aggregate(Max("position"))["position__max"]
        form.instance.position = (last_position or 0) + 1
        return super().form_valid(form)


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm

    def get_success_url(self):
        list = get_object_or_404(List, pk=self.kwargs["list_pk"])
        return reverse("flowdesk:board-detail", args=(list.board_id, ))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        list_obj = get_object_or_404(List, pk=self.kwargs["list_pk"])
        kwargs["workspace"] = list_obj.board.workspace
        return kwargs

    def form_valid(self, form: TaskForm) -> HttpResponse:
        list = get_object_or_404(List, pk=self.kwargs["list_pk"])
        form.instance.list = list
        form.instance.created_by = self.request.user

        last_position = list.tasks.aggregate(Max("position"))["position__max"]
        form.instance.position = (last_position or 0) + 1
        return super().form_valid(form)


class ListOrderUpdate(LoginRequiredMixin, generic.View):
    def post(self, request, board_id, *args, **kwargs):
        data = json.loads(request.body)
        order = data.get("order", [])

        list_ids = [int(item["id"]) for item in order]
        lists = List.objects.filter(pk__in=list_ids, board_id=board_id)

        positions = {int(item["id"]): item["position"] for item in order}
        for list in lists:
            list.position = positions.get(list.id, list.position)

        List.objects.bulk_update(objs=lists, fields=["position"])

        return HttpResponse(status=204)


class TaskOrderUpdate(LoginRequiredMixin, generic.View):
    def post(self, request, board_id, *args, **kwargs):
        data = json.loads(request.body)
        moves = data.get("moves", [])

        task_ids = [int(item["id"]) for item in moves]
        tasks = Task.objects.filter(pk__in=task_ids, list__board_id=board_id)

        moves_dict = {int(item["id"]): item for item in moves}

        for task in tasks:
            move = moves_dict.get(task.pk)
            if move:
                task.position = move["position"]
                task.list_id = move["list"]

        Task.objects.bulk_update(objs=tasks, fields=["position", "list_id"])

        return HttpResponse(status=204)