from django import forms
from django.contrib.auth import get_user_model

from flowdesk.models import Workspace, Board, List, Task, Tag

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
    assigned_to = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
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

    def __init__(self, *args, workspace=None, board=None, **kwargs):
        super().__init__(*args, **kwargs)
        if workspace:
            self.fields["assigned_to"].queryset = workspace.members.all()
            self.fields["tags"].queryset = workspace.tags.all()
        if board:
            self.fields["blocking_tasks"].queryset = Task.objects.filter(
                list__board=board
            )


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ("name",)
