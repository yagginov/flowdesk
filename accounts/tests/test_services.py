from unittest.mock import patch, MagicMock
from django.test import TestCase

from accounts.services.email_confirmation_service import EmailConfirmationService
from accounts.services.token_service import account_activation_token


class DummyUser:
    def __init__(self, pk=1, email="test@example.com", is_active=False):
        self.pk = pk
        self.email = email
        self.is_active = is_active

    def save(self):
        self.saved = True

    def __str__(self):
        return "dummyuser"


class DummyForm:
    def __init__(self, user):
        self.instance = user

    def save(self):
        self.instance.saved = True
        return self.instance


class DummyView:
    def __init__(self, user):
        self.request = MagicMock()
        self.request.scheme = "http"
        self.request.user = user
        self.request.FILES = {}
        self.request.POST = {}


class EmailConfirmationServiceTests(TestCase):
    @patch("accounts.services.email_confirmation_service.get_current_site")
    @patch("accounts.services.email_confirmation_service.render_to_string")
    @patch("accounts.services.email_confirmation_service.EmailMessage")
    def test_send_validation_email(self, mock_email, mock_render, mock_site):
        user = DummyUser()
        form = DummyForm(user)
        view = DummyView(user)
        mock_site.return_value.domain = "testserver"
        mock_render.return_value = "<html></html>"
        mock_email.return_value.send.return_value = None
        result = EmailConfirmationService.send_validation_email(view, form)
        self.assertTrue(result)
        self.assertFalse(user.is_active)
        self.assertTrue(hasattr(user, "saved"))
        mock_email.assert_called()
        mock_render.assert_called()

    @patch("accounts.services.email_confirmation_service.messages")
    def test_activate_account_success(self, mock_messages):
        user = DummyUser(is_active=False)
        token = account_activation_token.make_token(user)
        request = MagicMock()
        result = EmailConfirmationService.activate_account(request, user, token)
        self.assertTrue(result)
        self.assertTrue(user.is_active)
        mock_messages.success.assert_called()

    @patch("accounts.services.email_confirmation_service.messages")
    def test_activate_account_already_active(self, mock_messages):
        user = DummyUser(is_active=True)
        token = account_activation_token.make_token(user)
        request = MagicMock()
        result = EmailConfirmationService.activate_account(request, user, token)
        self.assertTrue(result)
        mock_messages.info.assert_called()

    @patch("accounts.services.email_confirmation_service.User.objects.get")
    def test_get_user_by_uid_found(self, mock_get):
        user = DummyUser(pk=123)
        mock_get.return_value = user
        uid = "MTIz"  # base64 for 123
        result = EmailConfirmationService.get_user_by_uid(uid)
        self.assertEqual(result, user)
        mock_get.assert_called()

    @patch(
        "accounts.services.email_confirmation_service.User.objects.get",
        side_effect=Exception,
    )
    def test_get_user_by_uid_not_found(self, mock_get):
        uid = "invalid"
        result = EmailConfirmationService.get_user_by_uid(uid)
        self.assertIsNone(result)


class TokenGeneratorTests(TestCase):
    def test_token_generator_make_and_check(self):
        user = DummyUser(pk=1, is_active=True)
        token = account_activation_token.make_token(user)
        self.assertIsInstance(token, str)
        self.assertTrue(account_activation_token.check_token(user, token))
