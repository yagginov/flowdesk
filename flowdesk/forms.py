from django import forms

from flowdesk.models import Workspace, Board, List


class WorkspaceForm(forms.ModelForm):
    class Meta:
        model = Workspace
        fields = ("name", "description", )


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ("name", "description", )


class ListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ("name", )
