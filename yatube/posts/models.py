from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q

User = get_user_model()


class Group(models.Model):
    """Создание таблицы Group."""

    title = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Описание")

    class Meta:
        """Meta class."""

        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        """Получение имени сообщества."""
        return self.title[:15]


class Post(models.Model):
    """Создание таблицы Post."""

    text = models.TextField("Текст поста", help_text="Введите текст поста")
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name="posts",
        blank=True,
        null=True,
        verbose_name="Группа",
        help_text="Группа, к которой будет относиться пост",
    )
    image = models.ImageField("Картинка", upload_to="posts/", blank=True)

    class Meta:
        """Meta class."""

        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-pub_date"]

    def __str__(self):
        """Выводим текст поста."""
        return self.text[:15]


class Comment(models.Model):
    """Создание таблицы Comment."""

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments", null=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments", null=True
    )
    text = models.TextField(
        "Текст комментария", help_text="Введите текст комментария"
    )
    created = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    """Создание таблицы Follow."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following", null=True
    )

    class Meta:
        """Meta класс."""

        verbose_name_plural = "Подписки"
        verbose_name = "Подписка"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_user_author",
            )
        ]  # Надеюсь сейчас правильно :)
