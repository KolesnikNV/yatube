from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма для Post."""

    class Meta:
        """Meta class."""

        model = Post
        fields = ("text", "group", "image")

    def clean_data(self):
        """Проверяет валидацию."""
        data = self.changed_data["text"]
        if data == "":
            raise forms.ValidationError("Поле надо заполнить")
        return data


class CommentForm(forms.ModelForm):
    """Форма для Comment."""

    class Meta:
        """Meta class."""

        model = Comment
        fields = ("text",)

    def clean_data(self):
        """Проверяет валидацию."""
        data = self.changed_data["text"]
        if data == "":
            raise forms.ValidationError("Поле надо заполнить")
        return data
