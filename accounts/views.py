from django.contrib.auth import get_user_model
from django.views import generic
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.urls import reverse_lazy

from accounts.forms import SignUpForm, UserUpdateForm, ProfileUpdateForm
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


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = User


class UserUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "accounts/user_update.html"
    form_class = UserUpdateForm
    success_url = reverse_lazy("accounts:user-update")

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["profile_form"] = ProfileUpdateForm(self.request.POST, self.request.FILES, instance=self.request.user.profile)
        else:
            context["profile_form"] = ProfileUpdateForm(instance=self.request.user.profile)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        profile_form = context["profile_form"]
        if profile_form.is_valid():
            profile_form.save()
        return super().form_valid(form)


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:password-change-done")


class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "accounts/password_change_done.html"
