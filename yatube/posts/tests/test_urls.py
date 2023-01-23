from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostURLTests(TestCase):
    """Тесты posts/url."""

    @classmethod
    def setUpClass(cls):
        """Фикстуры."""
        super().setUpClass()
        cls.user = User.objects.create(username="Name")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовая пост",
        )
        cls.templates_url_names = {
            "/": "posts/index.html",
            f"/group/{cls.group.slug}/": "posts/group_list.html",
            f"/profile/{cls.user.username}/": "posts/profile.html",
            f"/posts/{cls.post.id}/": "posts/post_detail.html",
            f"/posts/{cls.post.id}/edit/": "posts/create_post.html",
            "/create/": "posts/create_post.html",
        }

    def setUp(self):
        """Фикстуры."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_authorized_client(self):
        """Страница /create/ доступна только авторизированному пользователю."""
        response = self.guest_client.get("/create/")
        self.assertRedirects(response, "/auth/login/?next=%2Fcreate%2F")

    def test_not_author(self):
        """Страница /posts/post_id/edit/ доступна только автору."""
        response = self.guest_client.get(f"/posts/{self.post.id}/edit/")
        self.assertRedirects(
            response, f"/auth/login/?next=/posts/{self.post.id}/edit/"
        )

    def test_author(self):
        """Автор имеет доступ к /posts/post_id/edit/."""
        response = self.authorized_client.get(f"/posts/{self.post.id}/edit/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unknown_page(self):
        """Ошибка при переходе на неизвестную страницу."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")

    def test_follow(self):
        """
        Страница с подписками доступна
        только авторизированному пользователю.
        """
        response = self.guest_client.get(reverse("posts:follow_index"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
