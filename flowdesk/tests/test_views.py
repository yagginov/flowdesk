from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from flowdesk.models import Workspace, WorkspaceMember
from unittest.mock import patch

User = get_user_model()


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="u", password="p")
        self.workspace = Workspace.objects.create(name="WS", description="D")
        WorkspaceMember.objects.create(
            user=self.user, workspace=self.workspace, role=WorkspaceMember.Roles.OWNER
        )
        self.client.login(username="u", password="p")

    def test_workspace_members_view_get(self):
        url = reverse("flowdesk:workspace-members", args=(self.workspace.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_workspace_members_view_post(self):
        url = reverse("flowdesk:workspace-members", args=(self.workspace.pk,))
        data = {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "1",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-id": str(self.workspace.memberships.first().id),
            "form-0-role": WorkspaceMember.Roles.USER,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.workspace.memberships.first().refresh_from_db()
        self.assertEqual(
            self.workspace.memberships.first().role, WorkspaceMember.Roles.USER
        )

    @patch("flowdesk.views.generate_invite_link", return_value="http://test/invite")
    def test_workspace_invite_view(self, mock_invite):
        url = reverse("flowdesk:workspace-invite", args=(self.workspace.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("http://test/invite", response.content.decode())

    @patch("flowdesk.views.workspace_invite_token.check_token", return_value=True)
    @patch("flowdesk.views.urlsafe_base64_decode", return_value=b"1")
    def test_workspace_join_view(self, mock_decode, mock_check):
        url = reverse(
            "flowdesk:workspace-join",
            kwargs={"pk": self.workspace.pk, "uidb64": "uid", "token": "tok"},
        )
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_tag_create_view(self):
        # get
        url = reverse("flowdesk:tag-create", args=(self.workspace.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # post
        data = {"name": "bug", "workspace": str(self.workspace.id)}
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        tag = self.workspace.tags.first()
        self.assertEqual(tag.name, "bug")

        self.assertEqual(response.status_code, 200)
        tags = self.workspace.tags.all()
        self.assertEqual(tags.count(), 1)
