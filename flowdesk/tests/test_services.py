import unittest
from unittest.mock import MagicMock, patch

from flowdesk.services import task_graph, workspace_invite


class TestTaskGraphService(unittest.TestCase):
    def make_task(self, pk, title, blockers=None, blocked=None, list_name="List"):
        task = MagicMock()
        task.pk = pk
        task.title = title
        task.list.name = list_name
        task.blocking_tasks.all.return_value = blockers or []
        task.tasks.all.return_value = blocked or []
        return task

    @patch("flowdesk.services.task_graph.reverse", lambda *a, **kw: "/mock-url/")
    def test_build_task_graph_simple(self):
        t1 = self.make_task(1, "Task 1")
        queryset = MagicMock()
        queryset.filter.return_value = [t1]
        result = task_graph.build_task_graph(t1, queryset, 10, 20)
        self.assertIn("nodes", result)
        self.assertIn("edges", result)
        self.assertEqual(result["nodes"][0]["id"], 1)
        self.assertEqual(result["nodes"][0]["group"], "current")
        self.assertEqual(result["edges"], [])

    @patch("flowdesk.services.task_graph.reverse", lambda *a, **kw: "/mock-url/")
    def test_build_task_graph_with_blockers_and_blocked(self):
        t1 = self.make_task(1, "Task 1")
        t2 = self.make_task(2, "Task 2")
        t3 = self.make_task(3, "Task 3")
        t1.blocking_tasks.all.return_value = [t2]
        t1.tasks.all.return_value = [t3]
        t2.blocking_tasks.all.return_value = []
        t2.tasks.all.return_value = []
        t3.blocking_tasks.all.return_value = []
        t3.tasks.all.return_value = []
        queryset = MagicMock()
        queryset.filter.return_value = [t1, t2, t3]
        result = task_graph.build_task_graph(t1, queryset, 10, 20)
        self.assertEqual(len(result["nodes"]), 3)
        self.assertTrue(any(n["group"] == "blockers" for n in result["nodes"]))
        self.assertTrue(any(n["group"] == "blocked" for n in result["nodes"]))
        self.assertTrue(any(e["from"] == 2 and e["to"] == 1 for e in result["edges"]))


class TestWorkspaceInviteService(unittest.TestCase):
    @patch(
        "flowdesk.services.workspace_invite.reverse",
        return_value="/join/42/uidb64/token123",
    )
    @patch(
        "flowdesk.services.workspace_invite.workspace_invite_token.make_token",
        return_value="token123",
    )
    @patch(
        "flowdesk.services.workspace_invite.urlsafe_base64_encode",
        return_value="uidb64",
    )
    def test_generate_invite_link(self, mock_uid, mock_token, mock_reverse):
        request = MagicMock()
        request.build_absolute_uri.side_effect = lambda url: f"http://testserver{url}"
        workspace = MagicMock()
        workspace.pk = 42
        invited_user = MagicMock()
        invited_user.pk = 99
        link = workspace_invite.generate_invite_link(request, workspace, invited_user)
        self.assertEqual(link, "http://testserver/join/42/uidb64/token123")
