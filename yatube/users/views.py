from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import ContactForm, CreationForm


class SignUp(CreateView):
    """Регистрация пользователя."""

    form_class = CreationForm
    success_url = reverse_lazy("users:login")
    template_name = "users/signup.html"


class PasswordChange(CreateView):
    """Смена пароля."""

    for_class = CreationForm
    success_url = reverse_lazy("posts:index")
    template_name = "users/password_change_form.html"


class PasswordChangeDone(CreateView):
    """Успешная смена пароля."""

    for_class = CreationForm
    success_url = reverse_lazy("posts:index")
    template_name = "users/password_change_done.html"


class PasswordReset(CreateView):
    """Сброс пароля."""

    for_class = CreationForm
    success_url = reverse_lazy("users/password_reset_form.html")
    template_name = "users/password_reset_done.html"


class PasswordResetDone(CreateView):
    """Письмо на почту."""

    for_class = CreationForm
    success_url = reverse_lazy("posts:index")
    template_name = "users/password_reset_done.html"


class PasswordResetConfirmView(CreateView):
    """Новый пароль."""

    for_class = CreationForm
    success_url = reverse_lazy("posts:index")
    template_name = "users/password_reset_confirm.html"


class PasswordResetCompleteView(CreateView):
    """Успешный сброс пароля."""

    for_class = CreationForm
    success_url = reverse_lazy("posts:index")
    template_name = "users/password_reset_complete.html"


def user_contact(request):
    """Что-то из теории."""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/thank-you/")
        return render(request, "contact.html", {"form": form})
    form = ContactForm()
    return render(request, "contact.html", {"form": form})
