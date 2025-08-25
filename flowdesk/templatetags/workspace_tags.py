from django import template
from flowdesk.models import WorkspaceMember

register = template.Library()

@register.simple_tag
def has_workspace_role(user, workspace, *roles):
    if not user.is_authenticated:
        return False
    membership = WorkspaceMember.objects.filter(user=user, workspace=workspace).first()
    if not membership:
        return False
    return membership.role in roles
