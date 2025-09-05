from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.models import Profile

User = get_user_model()


class TestUserCreatedSignal(TestCase):
    def test_profile_created(self):
        user = User.objects.create_user(username="user", password="p")
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_only_one_profile_created(self):
        user = User.objects.create_user(username="user", password="p")
        user.save()
        user.save()
        self.assertEqual(Profile.objects.filter(user=user).count(), 1)
