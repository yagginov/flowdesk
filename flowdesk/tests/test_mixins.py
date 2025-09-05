from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from flowdesk.models import Workspace, WorkspaceMember, Board, List, Task
from unittest.mock import patch

User = get_user_model()


class TestMixins(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username="owner", password="p")
        self.admin = User.objects.create_user(username="admin", password="p")
        self.user = User.objects.create_user(username="user", password="p")
        self.guest = User.objects.create_user(username="guest", password="p")
        self.outsider = User.objects.create_user(username="outsider", password="p")

        self.workspace = Workspace.objects.create(name="WS", description="D")
        WorkspaceMember.objects.create(
            user=self.owner, workspace=self.workspace, role=WorkspaceMember.Roles.OWNER
        )
        WorkspaceMember.objects.create(
            user=self.admin, workspace=self.workspace, role=WorkspaceMember.Roles.ADMIN
        )
        WorkspaceMember.objects.create(
            user=self.user, workspace=self.workspace, role=WorkspaceMember.Roles.USER
        )
        WorkspaceMember.objects.create(
            user=self.guest, workspace=self.workspace, role=WorkspaceMember.Roles.GUEST
        )

        self.board = Board.objects.create(
            name="B", description="D", workspace=self.workspace
        )
        self.list = List.objects.create(name="L", position=1, board=self.board)
        self.task = Task.objects.create(
            title="T",
            description="D",
            list=self.list,
            created_by=self.owner,
            position=1,
        )

    def test_index_access(self):
        self.client.login(username=self.user.username, password="p")
        url = reverse("flowdesk:index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.logout()
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

    def test_workspace_detail_access(self):
        url = reverse("flowdesk:workspace-detail", kwargs={"pk": self.workspace.pk})
        for user in [self.owner, self.admin, self.user, self.guest]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        self.client.login(username=self.outsider.username, password="p")
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

    def test_workspace_members_access(self):
        url = reverse("flowdesk:workspace-members", kwargs={"pk": self.workspace.pk})
        for user in [self.owner, self.admin, self.user, self.guest]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        self.client.login(username=self.outsider.username, password="p")
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

    def test_workspace_update_access(self):
        # Only owner and admin
        url = reverse("flowdesk:workspace-update", kwargs={"pk": self.workspace.pk})
        for user in [self.owner, self.admin]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        for user in [self.user, self.guest, self.outsider]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 200)

    def test_workspace_delete_access(self):
        # Only owner
        self.client.login(username=self.owner.username, password="p")
        url = reverse("flowdesk:workspace-delete", kwargs={"pk": self.workspace.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        for user in [self.admin, self.user, self.guest, self.outsider]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 200)

    def test_board_detail_access(self):
        # only outsider has no access
        url = reverse(
            "flowdesk:board-detail",
            kwargs={"workspace_pk": self.workspace.pk, "pk": self.board.pk},
        )
        for user in [self.owner, self.admin, self.user, self.guest]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        self.client.login(username=self.outsider.username, password="p")
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

    def test_board_create_access(self):
        # Only owner and admin
        url = reverse(
            "flowdesk:board-create", kwargs={"workspace_pk": self.workspace.pk}
        )
        for user in [self.owner, self.admin]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        for user in [self.user, self.guest, self.outsider]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 200)

    def test_board_update_access(self):
        # Only owner and admin
        url = reverse(
            "flowdesk:board-update",
            kwargs={"workspace_pk": self.workspace.pk, "pk": self.board.pk},
        )
        for user in [self.owner, self.admin]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        for user in [self.user, self.guest, self.outsider]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 200)

    def test_board_delete_access(self):
        # Only owner and admin
        url = reverse(
            "flowdesk:board-delete",
            kwargs={"workspace_pk": self.workspace.pk, "pk": self.board.pk},
        )
        for user in [self.owner, self.admin]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        for user in [self.user, self.guest, self.outsider]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 200)

    def test_list_create_access(self):
        # Only owner and admin
        url = reverse(
            "flowdesk:list-create",
            kwargs={"workspace_pk": self.workspace.pk, "board_pk": self.board.pk},
        )
        for user in [self.owner, self.admin]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        for user in [self.user, self.guest, self.outsider]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 200)

    def test_list_update_access(self):
        # Only owner and admin
        url = reverse(
            "flowdesk:list-update",
            kwargs={
                "workspace_pk": self.workspace.pk,
                "board_pk": self.board.pk,
                "pk": self.list.pk,
            },
        )
        for user in [self.owner, self.admin]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        for user in [self.user, self.guest, self.outsider]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 200)

    def test_list_delete_access(self):
        # Only owner and admin
        url = reverse(
            "flowdesk:list-delete",
            kwargs={
                "workspace_pk": self.workspace.pk,
                "board_pk": self.board.pk,
                "pk": self.list.pk,
            },
        )
        for user in [self.owner, self.admin]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        for user in [self.user, self.guest, self.outsider]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 200)

    def test_task_detail_access(self):
        url = reverse(
            "flowdesk:task-detail",
            kwargs={
                "workspace_pk": self.workspace.pk,
                "board_pk": self.board.pk,
                "list_pk": self.list.pk,
                "pk": self.task.pk,
            },
        )
        for user in [self.owner, self.admin, self.user, self.guest]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        self.client.login(username=self.outsider.username, password="p")
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

    def test_task_create_access(self):
        # Only owner, admin, user
        url = reverse(
            "flowdesk:task-create",
            kwargs={
                "workspace_pk": self.workspace.pk,
                "board_pk": self.board.pk,
                "list_pk": self.list.pk,
            },
        )
        for user in [self.owner, self.admin, self.user]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302])

        for user in [self.guest, self.outsider]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 200)

    def test_task_update_access(self):
        # Only owner, admin, user
        url = reverse(
            "flowdesk:task-update",
            kwargs={
                "workspace_pk": self.workspace.pk,
                "board_pk": self.board.pk,
                "list_pk": self.list.pk,
                "pk": self.task.pk,
            },
        )
        for user in [self.owner, self.admin, self.user]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        for user in [self.guest, self.outsider]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 200)

    def test_task_delete_access(self):
        # Only owner, admin, user
        url = reverse(
            "flowdesk:task-delete",
            kwargs={
                "workspace_pk": self.workspace.pk,
                "board_pk": self.board.pk,
                "list_pk": self.list.pk,
                "pk": self.task.pk,
            },
        )
        for user in [self.owner, self.admin, self.user]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        for user in [self.guest, self.outsider]:
            self.client.login(username=user.username, password="p")
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 200)
