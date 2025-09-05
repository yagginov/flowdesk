from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from accounts.models import User
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpViewTests(TestCase):
    @patch(
        "accounts.services.email_confirmation_service.EmailConfirmationService.send_validation_email"
    )
    def test_signup_view_calls_service_and_renders_confirmation(self, mock_send):
        mock_send.return_value = True
        response = self.client.post(reverse("accounts:sign-up"), data={
            "username": "username",
            "email": "test@test.com",
            "password1": "fajsdgae9w8tSAIDpudg",
            "password2": "fajsdgae9w8tSAIDpudg"
        })
        self.assertTemplateUsed(response, "registration/email_confirmation_sent.html")
        mock_send.assert_called()


class ActivateAccountViewTests(TestCase):
    @patch(
        "accounts.services.email_confirmation_service.EmailConfirmationService.get_user_by_uid"
    )
    @patch(
        "accounts.services.email_confirmation_service.EmailConfirmationService.activate_account"
    )
    def test_activate_account_success(self, mock_activate, mock_get_user):
        mock_user = MagicMock(spec=User)
        mock_get_user.return_value = mock_user
        mock_activate.return_value = True
        response = self.client.get(reverse("accounts:activate", args=["uid", "token"]))
        self.assertRedirects(response, reverse("accounts:login"))
        mock_get_user.assert_called()
        mock_activate.assert_called()

    @patch(
        "accounts.services.email_confirmation_service.EmailConfirmationService.get_user_by_uid"
    )
    @patch(
        "accounts.services.email_confirmation_service.EmailConfirmationService.activate_account"
    )
    def test_activate_account_invalid(self, mock_activate, mock_get_user):
        mock_get_user.return_value = None
        mock_activate.return_value = False
        response = self.client.get(reverse("accounts:activate", args=["uid", "token"]))
        self.assertTemplateUsed(response, "registration/activation_invalid.html")


class PreLogoutViewTests(TestCase):
    def test_pre_logout_view_renders_template(self):
        response = self.client.get(reverse("accounts:pre-logout"))
        self.assertTemplateUsed(response, "registration/pre_logged_out.html")


class UserViewsSmokeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

    def test_user_detail_view(self):
        response = self.client.get(reverse("accounts:user-detail", args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/user_detail.html")

    def test_user_update_view(self):
        response = self.client.get(reverse("accounts:user-update"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/user_update.html")

    def test_password_change_view(self):
        response = self.client.get(reverse("accounts:password-change"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_change.html")

    def test_password_change_done_view(self):
        response = self.client.get(reverse("accounts:password-change-done"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_change_done.html")
