from django.http import HttpRequest

from flowdesk.models import Workspace


def user_workspaces(request: HttpRequest) -> dict:
    if request.user.is_authenticated:
        return {"user_workspaces": Workspace.objects.filter(members=request.user)}
    return {"user_workspaces": []}
