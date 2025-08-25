from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from flowdesk.models import Workspace, Board, List, Task, Tag


from flowdesk.models import WorkspaceMember

class RoleRequiredMixin:
    required_role = None
    workspace_attr = "workspace"

    def dispatch(self, request, *args, **kwargs):
        workspace = getattr(self, self.workspace_attr, None)
        if not workspace:
            raise PermissionDenied("Workspace not found for role check.")
        try:
            member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
        except WorkspaceMember.DoesNotExist:
            raise PermissionDenied("You are not a member of this workspace.")
        if not self.has_required_role(member.role):
            raise PermissionDenied(f"You must have at least {self.required_role} role to perform this action.")
        return super().dispatch(request, *args, **kwargs)

    def has_required_role(self, user_role):
        hierarchy = [
            WorkspaceMember.Roles.GUEST,
            WorkspaceMember.Roles.USER,
            WorkspaceMember.Roles.ADMIN,
            WorkspaceMember.Roles.OWNER,
        ]
        required_idx = hierarchy.index(self.required_role)
        user_idx = hierarchy.index(user_role)
        return user_idx >= required_idx


class OwnerRequiredMixin(RoleRequiredMixin):
    required_role = WorkspaceMember.Roles.OWNER


class AdminRequiredMixin(RoleRequiredMixin):
    required_role = WorkspaceMember.Roles.ADMIN


class UserRequiredMixin(RoleRequiredMixin):
    required_role = WorkspaceMember.Roles.USER


class GuestRequiredMixin(RoleRequiredMixin):
    required_role = WorkspaceMember.Roles.GUEST


class WorkspaceAccessMixin:
    workspace_lookup_url_kwarg = "workspace_pk"

    def dispatch(self, request, *args, **kwargs):
        workspace_pk = kwargs.get(self.workspace_lookup_url_kwarg) or kwargs.get("pk")
        workspace = get_object_or_404(Workspace, pk=workspace_pk)

        if not workspace.members.filter(pk=request.user.pk).exists():
            raise PermissionDenied("You do not have access to this workspace")

        if "board_pk" in kwargs:
            board = get_object_or_404(Board, pk=kwargs["board_pk"])
            self.board = board
            if board.workspace_id != workspace.pk:
                raise PermissionDenied("This board does not belong to the workspace")

        if "list_pk" in kwargs:
            lst = get_object_or_404(List, pk=kwargs["list_pk"])
            self.list = lst
            if lst.board.workspace_id != workspace.pk:
                raise PermissionDenied("This list does not belong to the workspace")

        if "task_pk" in kwargs:
            task = get_object_or_404(Task, pk=kwargs["task_pk"])
            self.task = task
            if task.list.board.workspace_id != workspace.pk:
                raise PermissionDenied("This task does not belong to the workspace")

        if "pk" in kwargs and self.model in [Board, List, Task, Tag]:
            obj = get_object_or_404(self.model, pk=kwargs["pk"])
            related_ws = (
                obj.workspace_id
                if isinstance(obj, (Board, Tag))
                else (
                    obj.board.workspace_id
                    if isinstance(obj, List)
                    else obj.list.board.workspace_id if isinstance(obj, Task) else None
                )
            )
            if related_ws and related_ws != workspace.pk:
                raise PermissionDenied("This object does not belong to the workspace")

        self.workspace = workspace
        return super().dispatch(request, *args, **kwargs)
