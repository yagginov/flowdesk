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
    Tag,
)
from flowdesk.forms import (
    WorkspaceForm,
    BoardForm,
    ListForm,
    TaskForm,
    TagForm,
)
from flowdesk.mixins import WorkspaceAccessMixin


class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = "flowdesk/index.html"


class WorkspaceDetailView(LoginRequiredMixin, WorkspaceAccessMixin, generic.DetailView):
    model = Workspace
    template_name = "flowdesk/workspace_detail.html"

    def get_queryset(self) -> QuerySet:
        return Workspace.objects.prefetch_related("boards")


class WorkspaceMembersView(LoginRequiredMixin, WorkspaceAccessMixin, generic.DetailView):
    model = Workspace
    template_name = "flowdesk/workspace_members.html"

    def get_queryset(self) -> QuerySet:
        return Workspace.objects.prefetch_related("memberships__user__profile")


class WorkspaceTagsView(LoginRequiredMixin, WorkspaceAccessMixin, generic.DetailView):
    model = Workspace
    template_name = "flowdesk/workspace_tags.html"

    def get_queryset(self) -> QuerySet:
        return Workspace.objects.prefetch_related("tags")


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


class BoardDetailView(LoginRequiredMixin, WorkspaceAccessMixin, generic.DetailView):
    model = Board

    def get_queryset(self) -> QuerySet:
        return Board.objects.prefetch_related("lists__tasks").select_related("workspace")


class BoardCreateView(LoginRequiredMixin, WorkspaceAccessMixin, generic.CreateView):
    model = Board
    form_class = BoardForm

    def get_success_url(self):
        return reverse("flowdesk:workspace-detail", args=(self.workspace.pk,))

    def form_valid(self, form: BoardForm) -> HttpResponse:
        form.instance.workspace = self.workspace
        return super().form_valid(form)


class BoardUpdateView(LoginRequiredMixin, WorkspaceAccessMixin, generic.UpdateView):
    model = Board
    form_class = BoardForm

    def get_success_url(self):
        return reverse("flowdesk:workspace-detail", args=(self.workspace.pk,))


class BoardDeleteView(LoginRequiredMixin, WorkspaceAccessMixin, generic.DeleteView):
    model = Board

    def get_success_url(self):
        return reverse("flowdesk:workspace-detail", args=(self.workspace.pk,))


class ListCreateView(LoginRequiredMixin, WorkspaceAccessMixin, generic.CreateView):
    model = List
    form_class = ListForm

    def get_success_url(self):
        return reverse(
            "flowdesk:board-detail", args=(
                self.workspace.pk,
                self.board.pk,
            )
        )

    def form_valid(self, form: ListForm) -> HttpResponse:
        form.instance.board = self.board
        last_position = self.board.lists.aggregate(Max("position"))["position__max"]
        form.instance.position = (last_position or 0) + 1
        return super().form_valid(form)


class ListUpdateView(LoginRequiredMixin, WorkspaceAccessMixin, generic.UpdateView):
    model = List
    form_class = ListForm

    def get_success_url(self):
        return reverse(
            "flowdesk:board-detail", args=(
                self.workspace.pk,
                self.board.pk,
            )
        )


class ListDeleteView(LoginRequiredMixin, WorkspaceAccessMixin, generic.DeleteView):
    model = List

    def get_success_url(self):
        return reverse(
            "flowdesk:board-detail", args=(
                self.workspace.pk,
                self.board.pk,
            )
        )


class ListOrderUpdate(LoginRequiredMixin, WorkspaceAccessMixin, generic.View):
    def post(self, request, board_pk, *args, **kwargs):
        data = json.loads(request.body)
        order = data.get("order", [])

        list_ids = [int(item["id"]) for item in order]
        lists = List.objects.filter(pk__in=list_ids, board_id=board_pk)
        positions = {int(item["id"]): item["position"] for item in order}

        for lst in lists:
            lst.position = positions.get(lst.id, lst.position)

        List.objects.bulk_update(objs=lists, fields=["position"])
        return HttpResponse(status=204)


class TaskDetailView(LoginRequiredMixin, WorkspaceAccessMixin, generic.DetailView):
    model = Task
    queryset = Task.objects.prefetch_related("blocking_tasks")


class TaskCreateView(LoginRequiredMixin, WorkspaceAccessMixin, generic.CreateView):
    model = Task
    form_class = TaskForm

    def get_success_url(self):
        return reverse(
            "flowdesk:board-detail", args=(
                self.workspace.pk,
                self.board.pk,
            )
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["board"] = self.board
        kwargs["workspace"] = self.workspace
        return kwargs

    def form_valid(self, form: TaskForm) -> HttpResponse:
        form.instance.list = self.list
        form.instance.created_by = self.request.user
        last_position = self.list.tasks.aggregate(Max("position"))["position__max"]
        form.instance.position = (last_position or 0) + 1
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, WorkspaceAccessMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm

    def get_success_url(self):
        return reverse(
            "flowdesk:board-detail", args=(
                self.workspace.pk,
                self.board.pk,
            )
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["board"] = self.board
        kwargs["workspace"] = self.workspace
        return kwargs


class TaskDeleteView(LoginRequiredMixin, WorkspaceAccessMixin, generic.DeleteView):
    model = Task

    def get_success_url(self):
        return reverse(
            "flowdesk:board-detail", args=(
                self.workspace.pk,
                self.board.pk,
            )
        )


class TaskOrderUpdate(LoginRequiredMixin, WorkspaceAccessMixin, generic.View):
    def post(self, request, board_pk, *args, **kwargs):
        data = json.loads(request.body)
        moves = data.get("moves", [])

        task_ids = [int(item["id"]) for item in moves]
        tasks = Task.objects.filter(pk__in=task_ids, list__board_id=board_pk)
        moves_dict = {int(item["id"]): item for item in moves}

        for task in tasks:
            move = moves_dict.get(task.pk)
            if move:
                task.position = move["position"]
                task.list_id = move["list"]

        Task.objects.bulk_update(objs=tasks, fields=["position", "list_id"])
        return HttpResponse(status=204)


class TagCreateView(LoginRequiredMixin, WorkspaceAccessMixin, generic.CreateView):
    model = Tag
    form_class = TagForm

    def get_success_url(self):
        return reverse(
            "flowdesk:workspace-tags",
            args=(
                self.workspace.pk,
            )
        )

    def form_valid(self, form: TagForm) -> HttpResponse:
        form.instance.workspace = self.workspace
        return super().form_valid(form)


class TagUpdateView(LoginRequiredMixin, WorkspaceAccessMixin, generic.UpdateView):
    model = Tag
    form_class = TagForm

    def get_success_url(self):
        return reverse(
            "flowdesk:workspace-tags",
            args=(
                self.workspace.pk,
            )
        )


class TagDeleteView(LoginRequiredMixin, WorkspaceAccessMixin, generic.DeleteView):
    model = Tag

    def get_success_url(self):
        return reverse(
            "flowdesk:workspace-tags",
            args=(
                self.workspace.pk,
            )
        )
