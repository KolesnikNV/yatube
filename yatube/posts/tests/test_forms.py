from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    """Тестирование модели Post."""

    @classmethod
    def setUpClass(cls):
        """Фикстуры."""
        super().setUpClass()
        cls.user = User.objects.create_user(username="Name")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        image_png = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="image.png", content=image_png, content_type="image/png"
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
            image=uploaded,
        )
        cls.form = PostForm()

    def setUp(self):
        """Фикстуры."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        tasks_count = Post.objects.count()
        form_data = {"text": "Тестовый пост4", "image": "uploaded"}
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:profile",
                kwargs={
                    "username": self.user.username,
                },
            ),
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(Post.objects.filter(text="Тестовый пост4").exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit(self):
        """Валидная форма изменяет запись в Post."""
        self.post = Post.objects.create(
            author=self.user,
            text="Тестовый текст",
        )
        tasks_count = Post.objects.count()
        form_data = {"text": "Тестовый текст2"}
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=({self.post.id})),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:post_detail",
                kwargs={
                    "post_id": self.post.id,
                },
            ),
        )
        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertTrue(Post.objects.filter(text="Тестовый текст2").exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_comment_edit(self):
        """Валидная форма создает комментарий."""
        form_data = {"text": "Тестовый комментарий"}
        comments_count = Comment.objects.count()
        r_1 = self.authorized_client.post(
            reverse("posts:add_comment", args=({self.post.id})),
            data=form_data,
        )
        r_2 = self.guest_client.post(
            reverse("posts:add_comment", args=({self.post.id})),
            data=form_data,
        )
        self.assertRedirects(
            r_1,
            reverse("posts:post_detail", kwargs={"post_id": self.post.id}),
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(text="Тестовый комментарий").exists()
        )
        self.assertEqual(r_2.status_code, HTTPStatus.FOUND)
