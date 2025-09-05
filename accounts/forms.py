import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError

from accounts.models import Profile
from accounts.mixins import UsernameValidationMixin

User = get_user_model()


class SignUpForm(UsernameValidationMixin, UserCreationForm):
    email = forms.EmailField(required=True, label="Email address")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            "email",
            "first_name",
            "last_name",
        )


class UserUpdateForm(UsernameValidationMixin, forms.ModelForm):
    email = forms.EmailField(required=True, label="Email address")

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")


class ProfileUpdateForm(forms.ModelForm):
    avatar = forms.ImageField(required=False, label="Profile Photo")

    class Meta:
        model = Profile
        fields = ("avatar", "position")
