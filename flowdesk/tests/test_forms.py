from django.test import TestCase
from django.utils import timezone

from flowdesk.forms import (
    WorkspaceForm,
    BoardForm,
    ListForm,
    TaskForm,
    TagForm,
    CommentForm,
    WorkspaceMemberForm,
    WorkspaceMemberFormSet,
)
from flowdesk.models import Workspace, Board, List, Task, Tag, Comment, WorkspaceMember
from django.contrib.auth import get_user_model

User = get_user_model()


class TestWorkspaceForm(TestCase):
    def test_valid_data(self):
        form = WorkspaceForm(data={"name": "Test Workspace", "description": "Desc"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "Test Workspace")

    def test_missing_name(self):
        form = WorkspaceForm(data={"description": "Desc"})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)


class TestBoardForm(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="WS", description="D")

    def test_valid_data(self):
        form = BoardForm(data={"name": "Board", "description": "Desc"})
        self.assertTrue(form.is_valid())
        board = form.save(commit=False)
        board.workspace = self.workspace
        board.save()
        self.assertEqual(board.name, "Board")

    def test_missing_name(self):
        form = BoardForm(data={"description": "Desc"})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)


class TestListForm(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="WS", description="D")
        self.board = Board.objects.create(
            name="Board", description="Desc", workspace=self.workspace
        )

    def test_valid_data(self):
        form = ListForm(data={"name": "List"})
        self.assertTrue(form.is_valid())
        lst = form.save(commit=False)
        lst.board = self.board
        lst.position = 1
        lst.save()
        self.assertEqual(lst.name, "List")

    def test_missing_name(self):
        form = ListForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)


class TestTaskForm(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="p")
        self.workspace = Workspace.objects.create(name="WS", description="D")
        WorkspaceMember.objects.create(
            user=self.user, workspace=self.workspace, role=WorkspaceMember.Roles.USER
        )
        self.board = Board.objects.create(
            name="Board", description="Desc", workspace=self.workspace
        )
        self.lst = List.objects.create(name="List", board=self.board, position=1)
        self.tag = Tag.objects.create(name="Tag", workspace=self.workspace)

    def test_valid_data(self):
        data = {
            "title": "Task",
            "description": "Desc",
            "priority": Task.Priority.LOW,
            "status": Task.Status.TODO,
            "deadline": "2025-09-02T12:00",
            "tags": [self.tag.pk],
            "assigned_to": [self.user.pk],
        }
        form = TaskForm(data=data, workspace=self.workspace, board=self.board)
        self.assertTrue(form.is_valid())
        task = form.save(commit=False)
        task.list = self.lst
        task.created_by = self.user
        task.position = 1
        task.save()
        form.save_m2m()
        self.assertEqual(task.title, "Task")
        self.assertIn(self.tag, task.tags.all())
        self.assertIn(self.user, task.assigned_to.all())

    def test_missing_title(self):
        data = {
            "description": "Desc",
            "priority": Task.Priority.LOW,
            "status": Task.Status.TODO,
        }
        form = TaskForm(data=data, workspace=self.workspace, board=self.board)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)


class TestTagForm(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="WS", description="D")

    def test_valid_data(self):
        form = TagForm(data={"name": "Tag"})
        self.assertTrue(form.is_valid())
        tag = form.save(commit=False)
        tag.workspace = self.workspace
        tag.save()
        self.assertEqual(tag.name, "Tag")

    def test_missing_name(self):
        form = TagForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)


class TestCommentForm(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="p")
        self.workspace = Workspace.objects.create(name="WS", description="D")
        self.board = Board.objects.create(
            name="Board", description="Desc", workspace=self.workspace
        )
        self.lst = List.objects.create(name="List", board=self.board, position=1)
        self.task = Task.objects.create(
            title="Task",
            description="Desc",
            priority=Task.Priority.LOW,
            status=Task.Status.TODO,
            deadline=timezone.now(),
            list=self.lst,
            created_by=self.user,
            position=1,
        )

    def test_valid_data(self):
        form = CommentForm(data={"text": "Comment text"})
        self.assertTrue(form.is_valid())
        comment = form.save(commit=False)
        comment.task = self.task
        comment.created_by = self.user
        comment.save()
        self.assertEqual(comment.text, "Comment text")

    def test_missing_text(self):
        form = CommentForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("text", form.errors)


class TestWorkspaceMemberForm(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="p")
        self.workspace = Workspace.objects.create(name="WS", description="D")
        self.member = WorkspaceMember.objects.create(
            user=self.user, workspace=self.workspace, role=WorkspaceMember.Roles.USER
        )

    def test_valid_data(self):
        form = WorkspaceMemberForm(
            data={"role": WorkspaceMember.Roles.USER}, instance=self.member
        )
        self.assertTrue(form.is_valid())
        member = form.save()
        self.assertEqual(member.role, WorkspaceMember.Roles.USER)

    def test_invalid_role(self):
        form = WorkspaceMemberForm(data={"role": "INVALID"}, instance=self.member)
        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors)


class TestWorkspaceMemberFormSet(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="u1", password="p")
        self.user2 = User.objects.create_user(username="u2", password="p")
        self.workspace = Workspace.objects.create(name="WS", description="D")
        self.member1 = WorkspaceMember.objects.create(
            user=self.user1, workspace=self.workspace, role=WorkspaceMember.Roles.USER
        )
        self.member2 = WorkspaceMember.objects.create(
            user=self.user2, workspace=self.workspace, role=WorkspaceMember.Roles.ADMIN
        )

    def test_formset_valid(self):
        data = {
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "2",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-id": str(self.member1.id),
            "form-0-role": WorkspaceMember.Roles.ADMIN,
            "form-1-id": str(self.member2.id),
            "form-1-role": WorkspaceMember.Roles.USER,
        }
        formset = WorkspaceMemberFormSet(
            data, queryset=WorkspaceMember.objects.filter(workspace=self.workspace)
        )
        self.assertTrue(formset.is_valid())
        instances = formset.save()
        roles = [m.role for m in instances]
        self.assertIn(WorkspaceMember.Roles.ADMIN, roles)
        self.assertIn(WorkspaceMember.Roles.USER, roles)

    def test_formset_invalid(self):
        data = {
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "2",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-id": str(self.member1.id),
            "form-0-role": "INVALID",
            "form-1-id": str(self.member2.id),
            "form-1-role": WorkspaceMember.Roles.USER,
        }
        formset = WorkspaceMemberFormSet(
            data, queryset=WorkspaceMember.objects.filter(workspace=self.workspace)
        )
        self.assertFalse(formset.is_valid())
        self.assertIn("role", formset.forms[0].errors)
