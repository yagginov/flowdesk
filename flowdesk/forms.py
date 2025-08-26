from django import forms
from django.contrib.auth import get_user_model
from django.forms import modelformset_factory

from flowdesk.models import Workspace, Board, List, Task, Tag, Comment, WorkspaceMember

User = get_user_model()


class WorkspaceForm(forms.ModelForm):
    class Meta:
        model = Workspace
        fields = (
            "name",
            "description",
        )


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = (
            "name",
            "description",
        )


class ListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ("name",)


class TaskForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
    )
    deadline = forms.DateTimeField(
        required=False, widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )

    class Meta:
        model = Task
        fields = (
            "title",
            "description",
            "priority",
            "status",
            "deadline",
            "tags",
            "assigned_to",
            "blocking_tasks",
        )

    def __init__(self, *args, workspace=None, board=None, task=None, **kwargs):
        super().__init__(*args, **kwargs)
        if workspace:
            self.fields["assigned_to"].queryset = workspace.members.all()
            self.fields["tags"].queryset = workspace.tags.all()
        if board:
            queryset = Task.objects.filter(list__board=board)
            if task:
                queryset = queryset.exclude(pk=task.pk)
            self.fields["blocking_tasks"].queryset = queryset


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ("name",)


class CommentForm(forms.ModelForm):
    text = forms.CharField(
        label="Write your comment:",
        widget=forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
    )

    class Meta:
        model = Comment
        fields = ("text",)


class WorkspaceMemberForm(forms.ModelForm):
    class Meta:
        model = WorkspaceMember
        fields = ("role",)
        widgets = {"role": forms.Select(attrs={"class": "form-select"})}


WorkspaceMemberFormSet = modelformset_factory(
    WorkspaceMember, form=WorkspaceMemberForm, extra=0
)
