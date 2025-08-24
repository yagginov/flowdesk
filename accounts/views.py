from django.contrib.auth import get_user_model
from django.views import generic
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse

from accounts.forms import SignUpForm
from accounts.services.email_confirmation_service import EmailConfirmationService

User = get_user_model()


class SignUpView(generic.CreateView):
    model = User
    form_class = SignUpForm
    template_name = "registration/sign_up.html"

    def form_valid(self, form: SignUpForm) -> HttpResponse:
        if EmailConfirmationService.send_validation_email(self, form):
            return render(self.request, "registration/email_confirmation_sent.html")
        return super().form_invalid(form)


class ActivateAccountView(generic.View):
    def get(self, request: HttpRequest, uid: str, token: str) -> HttpResponse:
        user = EmailConfirmationService.get_user_by_uid(uid)
        if EmailConfirmationService.activate_account(request, user, token):
            return redirect("accounts:login")
        return render(request, "registration/activation_invalid.html")


class PreLogoutView(generic.TemplateView):
    template_name = "registration/pre_logged_out.html"
