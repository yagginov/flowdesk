from django.db import models
from django.contrib.auth.models import AbstractUser


class Position(models.Model):
    name = models.CharField(max_length=63)

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    position = models.ForeignKey(
        Position, on_delete=models.CASCADE, related_name="users"
    )

    def __str__(self) -> str:
        return f"{self.username} - {self.position}"
