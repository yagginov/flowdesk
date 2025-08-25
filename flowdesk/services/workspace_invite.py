from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse


class WorkspaceInviteTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_active}"


workspace_invite_token = WorkspaceInviteTokenGenerator()


def generate_invite_link(request, workspace, invited_user):
    token = workspace_invite_token.make_token(invited_user)
    uid = urlsafe_base64_encode(force_bytes(invited_user.pk))

    link = request.build_absolute_uri(
        reverse("flowdesk:workspace-join", kwargs={
            "workspace_id": workspace.pk,
            "uidb64": uid,
            "token": token,
        })
    )
    return link