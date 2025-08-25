import json

from django.http import HttpRequest, HttpResponse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.db.models import Max, QuerySet
from django.db import IntegrityError
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model

from flowdesk.models import (
    Workspace,
    WorkspaceMember,
    Tag,
    Board,
    List,
    Task,
    Comment,
)
from flowdesk.forms import (
    WorkspaceForm,
    BoardForm,
    ListForm,
    TaskForm,
    TagForm,
    CommentForm,
    WorkspaceMemberFormSet
)
from flowdesk.mixins import WorkspaceAccessMixin, AdminRequiredMixin, UserRequiredMixin
from flowdesk.services.workspace_invite import generate_invite_link, workspace_invite_token

User = get_user_model()


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

    def get_queryset(self):
        return Workspace.objects.prefetch_related("memberships__user__profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace = self.get_object()
        context['formset'] = WorkspaceMemberFormSet(queryset=workspace.memberships.all())
        return context

    def post(self, request, *args, **kwargs):
        workspace = self.get_object()
        formset = WorkspaceMemberFormSet(request.POST, queryset=workspace.memberships.all())

        if formset.is_valid():
            formset.save()
            messages.success(request, "Roles updated successfully.")
        else:
            messages.error(request, "There was a problem updating roles.")

        return redirect("flowdesk:workspace-members", pk=workspace.id)


class WorkspaceInviteView(LoginRequiredMixin, generic.DetailView):
    model = Workspace
    template_name = "flowdesk/invite_link.html"
    pk_url_kwarg = "workspace_id"
    context_object_name = "workspace"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace = self.get_object()

        if not workspace.memberships.filter(
            user=self.request.user,
            role__in=[WorkspaceMember.Roles.OWNER, WorkspaceMember.Roles.ADMIN],
        ).exists():
            messages.error(
                self.request, "You do not have permission to generate invites."
            )
            context["invite_link"] = None
        else:
            context["invite_link"] = generate_invite_link(
                self.request, workspace, self.request.user
            )
        return context


class WorkspaceJoinView(LoginRequiredMixin, generic.RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        workspace_id = kwargs.get("workspace_id")
        uidb64 = kwargs.get("uidb64")
        token = kwargs.get("token")

        workspace = get_object_or_404(Workspace, pk=workspace_id)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            inviter = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            inviter = None

        if inviter and workspace_invite_token.check_token(inviter, token):
            membership, created = WorkspaceMember.objects.get_or_create(
                user=self.request.user,
                workspace=workspace,
                defaults={"role": WorkspaceMember.Roles.GUEST},
            )
            if created:
                messages.success(
                    self.request, f"You have joined {workspace.name} as Guest."
                )
            else:
                messages.info(
                    self.request, f"You are already a member of {workspace.name}."
                )
            return reverse("flowdesk:workspace-members", kwargs={"pk": workspace.id})

        messages.error(self.request, "Invalid or expired invitation link.")
        return reverse("flowdesk:index")


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


class WorkspaceUpdateView(LoginRequiredMixin, WorkspaceAccessMixin, AdminRequiredMixin, generic.UpdateView):
    model = Workspace
    form_class = WorkspaceForm
    success_url = reverse_lazy("flowdesk:index")


class WorkspaceDeleteView(LoginRequiredMixin, WorkspaceAccessMixin, AdminRequiredMixin, generic.DeleteView):
    model = Workspace
    success_url = reverse_lazy("flowdesk:index")


class TagCreateView(LoginRequiredMixin, WorkspaceAccessMixin, AdminRequiredMixin, generic.CreateView):
    model = Tag
    form_class = TagForm

    def get_success_url(self):
        return reverse("flowdesk:workspace-tags", args=(self.workspace.pk,))

    def form_valid(self, form: TagForm) -> HttpResponse:
        form.instance.workspace = self.workspace
        try:
            return super().form_valid(form)
        except IntegrityError:
            messages.warning(
                self.request,
                f"Tag '{form.instance.name}' already exists in this workspace.",
            )
            return HttpResponseRedirect(self.get_success_url())


class TagUpdateView(LoginRequiredMixin, WorkspaceAccessMixin, AdminRequiredMixin, generic.UpdateView):
    model = Tag
    form_class = TagForm

    def get_success_url(self):
        return reverse("flowdesk:workspace-tags", args=(self.workspace.pk,))


class TagDeleteView(LoginRequiredMixin, WorkspaceAccessMixin, AdminRequiredMixin, generic.DeleteView):
    model = Tag

    def get_success_url(self):
        return reverse("flowdesk:workspace-tags", args=(self.workspace.pk,))


class BoardDetailView(LoginRequiredMixin, WorkspaceAccessMixin, generic.DetailView):
    model = Board

    def get_queryset(self) -> QuerySet:
        return Board.objects.prefetch_related("lists__tasks").select_related(
            "workspace"
        )


class BoardCreateView(LoginRequiredMixin, WorkspaceAccessMixin, AdminRequiredMixin, generic.CreateView):
    model = Board
    form_class = BoardForm

    def get_success_url(self):
        return reverse("flowdesk:workspace-detail", args=(self.workspace.pk,))

    def form_valid(self, form: BoardForm) -> HttpResponse:
        form.instance.workspace = self.workspace
        return super().form_valid(form)


class BoardUpdateView(LoginRequiredMixin, WorkspaceAccessMixin, AdminRequiredMixin, generic.UpdateView):
    model = Board
    form_class = BoardForm

    def get_success_url(self):
        return reverse("flowdesk:workspace-detail", args=(self.workspace.pk,))


class BoardDeleteView(LoginRequiredMixin, WorkspaceAccessMixin, AdminRequiredMixin, generic.DeleteView):
    model = Board

    def get_success_url(self):
        return reverse("flowdesk:workspace-detail", args=(self.workspace.pk,))


class ListCreateView(LoginRequiredMixin, WorkspaceAccessMixin, AdminRequiredMixin, generic.CreateView):
    model = List
    form_class = ListForm

    def get_success_url(self):
        return reverse(
            "flowdesk:board-detail",
            args=(
                self.workspace.pk,
                self.board.pk,
            ),
        )

    def form_valid(self, form: ListForm) -> HttpResponse:
        form.instance.board = self.board
        last_position = self.board.lists.aggregate(Max("position"))["position__max"]
        form.instance.position = (last_position or 0) + 1
        return super().form_valid(form)


class ListUpdateView(LoginRequiredMixin, WorkspaceAccessMixin, AdminRequiredMixin, generic.UpdateView):
    model = List
    form_class = ListForm

    def get_success_url(self):
        return reverse(
            "flowdesk:board-detail",
            args=(
                self.workspace.pk,
                self.board.pk,
            ),
        )


class ListDeleteView(LoginRequiredMixin, WorkspaceAccessMixin, AdminRequiredMixin, generic.DeleteView):
    model = List

    def get_success_url(self):
        return reverse(
            "flowdesk:board-detail",
            args=(
                self.workspace.pk,
                self.board.pk,
            ),
        )


class ListOrderUpdate(LoginRequiredMixin, WorkspaceAccessMixin, AdminRequiredMixin, generic.View):
    def post(self, request: HttpRequest, board_pk: int, *args, **kwargs):
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
    context_object_name = "task"
    template_name = "flowdesk/task_detail.html"

    def get_queryset(self):
        return Task.objects.select_related("list", "created_by").prefetch_related(
            "tags",
            "assigned_to",
            "blocking_tasks",
            "comments__created_by",
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["comment_form"] = CommentForm()
        return context


class TaskCreateView(LoginRequiredMixin, WorkspaceAccessMixin, UserRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm

    def get_success_url(self):
        return reverse(
            "flowdesk:board-detail",
            args=(
                self.workspace.pk,
                self.board.pk,
            ),
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


class TaskUpdateView(LoginRequiredMixin, WorkspaceAccessMixin, UserRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm

    def get_success_url(self):
        return reverse(
            "flowdesk:task-detail",
            args=(
                self.workspace.pk,
                self.board.pk,
                self.list.pk,
                self.object.pk,
            ),
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["board"] = self.board
        kwargs["workspace"] = self.workspace
        kwargs["task"] = self.object
        return kwargs


class TaskDeleteView(LoginRequiredMixin, WorkspaceAccessMixin, UserRequiredMixin, generic.DeleteView):
    model = Task

    def get_success_url(self):
        return reverse(
            "flowdesk:board-detail",
            args=(
                self.workspace.pk,
                self.board.pk,
            ),
        )


class TaskOrderUpdate(LoginRequiredMixin, WorkspaceAccessMixin, UserRequiredMixin, generic.View):
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


class CommentCreateView(LoginRequiredMixin, WorkspaceAccessMixin, UserRequiredMixin, generic.CreateView):
    model = Comment
    form_class = CommentForm

    def get_success_url(self):
        return reverse(
            "flowdesk:task-detail",
            args=(
                self.workspace.pk,
                self.board.pk,
                self.list.pk,
                self.task.pk,
            ),
        )

    def form_valid(self, form: CommentForm):
        form.instance.created_by = self.request.user
        form.instance.task = self.task
        return super().form_valid(form)
