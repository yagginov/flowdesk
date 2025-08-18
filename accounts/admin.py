from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User, Position


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("position", )


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("name", )
