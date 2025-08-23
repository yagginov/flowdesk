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
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from accounts.forms import SignUpForm
from accounts.services.token_service import account_activation_token

logger = logging.getLogger(__name__)
User = get_user_model()


class SignUpView(generic.CreateView):
    model = User
    form_class = SignUpForm
    template_name = "registration/sign_up.html"

    def form_valid(self, form: SignUpForm) -> HttpResponse:
        try:
            with transaction.atomic():
                form.instance.is_active = False
                user = form.save()

                mail_subject = "Email confirmation"

                scheme = self.request.scheme
                domain = get_current_site(self.request).domain
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
            return super().form_invalid(form)

        return render(self.request, "registration/email_confirmation_sent.html")


class ActivateAccountView(generic.View):
    def get(self, request: HttpRequest, uid: str, token: str) -> HttpResponse:
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user:
            if user.is_active:
                messages.info(request, "Your account is already activated.")
                return redirect("accounts:login")

            if account_activation_token.check_token(user, token):
                user.is_active = True
                user.save()

                messages.success(
                    request,
                    "Thank you for confirming your email. You can now login to your account."
                )
                return redirect("accounts:login")

        return render(request, "registration/activation_invalid.html")


class PreLogoutView(generic.TemplateView):
    template_name = "registration/pre_logged_out.html"
