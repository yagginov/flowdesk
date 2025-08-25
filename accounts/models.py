from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    def __str__(self) -> str:
        return f"{self.username}"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    avatar = models.ImageField(
        null=True, blank=True, upload_to="accounts/profiles/avatars/"
    )
    position = models.CharField(max_length=63)

    def __str__(self) -> str:
        return self.position
