import logging
from base64 import urlsafe_b64encode

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views import generic
from django.db import transaction
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import HttpRequest
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import AbstractUser

from accounts.services.token_service import account_activation_token
from accounts.forms import SignUpForm

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailConfirmationService:
    @staticmethod
    def send_validation_email(view: generic.CreateView, form: SignUpForm) -> bool:
        try:
            with transaction.atomic():
                form.instance.is_active = False
                user = form.save()

                mail_subject = "Email confirmation"

                scheme = view.request.scheme
                domain = get_current_site(view.request).domain
                uid = urlsafe_b64encode(force_bytes(user.pk)).decode()
                token = account_activation_token.make_token(user)
                print(scheme, domain, uid, token)

                url = f"{scheme}://{domain}/accounts/activate/{uid}/{token}/"

                html_content = render_to_string(
                    "registration/emails/account_activation_email.html",
                    context={"url": url, "user": user},
                )

                email = EmailMessage(mail_subject, html_content, to=[user.email])
                email.content_subtype = "html"
                email.send()

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
        return True

    @staticmethod
    def activate_account(request: HttpRequest, user: AbstractUser, token: str) -> bool:
        if not user:
            return False

        if user.is_active:
            messages.info(request, "Your account is already activated.")
            return True

        if account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()

            messages.success(
                request,
                "Thank you for confirming your email. You can now login to your account."
            )
            return True
        return False

    @staticmethod
    def get_user_by_uid(uid: str) -> AbstractUser | None:
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        return user
