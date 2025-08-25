from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from versatileimagefield.fields import VersatileImageField


class User(AbstractUser):
    def __str__(self) -> str:
        return f"{self.username}"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    avatar = VersatileImageField(
        "Avatar", upload_to="accounts/profiles/avatars/", blank=True, null=True
    )
    position = models.CharField(max_length=63)

    def __str__(self) -> str:
        return self.position
