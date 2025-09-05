import re

from django.forms import ValidationError


class UsernameValidationMixin:
    def clean_username(self):
        username = self.cleaned_data.get("username")

        if (
            username
            and self._meta.model.objects.filter(username__iexact=username).exists()
        ):
            self._update_errors(
                ValidationError(
                    {
                        "username": "This username is already taken. Please choose another one."
                    }
                )
            )

        if len(username) < 2:
            self._update_errors(
                ValidationError(
                    {
                        "username": "Username is too short. Minimum length is 2 characters."
                    }
                )
            )

        if len(username) > 30:
            self._update_errors(
                ValidationError(
                    {
                        "username": "Username is too long. Maximum length is 30 characters."
                    }
                )
            )

        if re.search(r"[A-Z]", username):
            self._update_errors(
                ValidationError(
                    {"username": "Username must not contain uppercase letters."}
                )
            )

        if not re.fullmatch(r"[a-z0-9._]+", username):
            self._update_errors(
                ValidationError(
                    {
                        "username": "Username contains invalid characters. Only lowercase letters, digits, '.' and '_' are allowed."
                    }
                )
            )

        return username
