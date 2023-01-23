from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Contact

User = get_user_model()


class CreationForm(UserCreationForm):
    """Форма для взаимодействия с пользователем."""

    class Meta(UserCreationForm.Meta):
        """Meta класс."""

        model = User
        fields = ("first_name", "last_name", "username", "email")


class ContactForm(forms.ModelForm):
    """Форма."""

    class Meta:
        """Meta класс."""

        model = Contact
        fields = ("name", "email", "subject", "body")

    def clean_subject(self):
        """Проверяет валидацию формы."""
        data = self.cleaned_data["subject"]
        if "спасибо" not in data.lower():
            raise forms.ValidationError(
                "Вы обязательно должны нас поблагодарить!"
            )
        return data
