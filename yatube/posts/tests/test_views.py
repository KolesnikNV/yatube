from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post

User = get_user_model()
TEST_OF_POST: int = 13


class PostPagesTests(TestCase):
    """Тесты posts/views."""

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
        cls.comment = Comment.objects.create(
            author=cls.user, text="Тестовый комментарий"
        )

    def setUp(self):
        """Фикстуры."""
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list",
                kwargs={
                    "slug": self.group.slug,
                },
            ): "posts/group_list.html",
            reverse(
                "posts:profile",
                kwargs={
                    "username": self.user.username,
                },
            ): "posts/profile.html",
            reverse(
                "posts:post_detail",
                kwargs={
                    "post_id": self.post.id,
                },
            ): "posts/post_detail.html",
            reverse("posts:post_create"): "posts/create_post.html",
            reverse(
                "posts:post_edit",
                kwargs={
                    "post_id": self.post.id,
                },
            ): "posts/create_post.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_paginator(self):
        """Отображение по 10 постов на страницу."""
        bulk_post = []
        for i in range(TEST_OF_POST):
            bulk_post.append(
                Post(
                    text=f"Тестовый пост {i}",
                    group=self.group,
                    author=self.user,
                )
            )
        Post.objects.bulk_create(bulk_post)

        response_index = self.guest_client.get(reverse("posts:index")).context[
            "page_obj"
        ]
        response_group = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
        ).context["page_obj"]
        response_profile = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": self.user.username})
        ).context["page_obj"]
        response_all = [response_index, response_group, response_profile]
        for response in response_all:
            self.assertQuerysetEqual(
                Post.objects.all()[:10], map(repr, response)
            )

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse("posts:index"))
        post_object = response.context["page_obj"][0]
        object_data = {
            post_object.text: self.post.text,
            post_object.author: self.user,
            post_object.group: self.group,
            post_object.image: self.post.image,
        }
        for obj, data in object_data.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, data)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                "posts:group_list",
                kwargs={
                    "slug": self.group.slug,
                },
            )
        )
        post_object = response.context["page_obj"][0]
        object_data = {
            post_object.text: self.post.text,
            post_object.author: self.user,
            post_object.group: self.group,
            post_object.image: self.post.image,
        }
        for obj, data in object_data.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, data)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": self.user.username})
        )
        post_object = response.context.get("page_obj")[0]
        object_data = {
            post_object.text: self.post.text,
            post_object.group: self.post.group,
            post_object.author: self.post.author,
            post_object.image: self.post.image,
        }
        for obj, data in object_data.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, data)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", args=(self.post.id,))
        )
        self.assertEqual(response.context["posts"], self.post)

    def test_create_page_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                "posts:post_edit",
                kwargs={
                    "post_id": self.post.id,
                },
            )
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_in_correct_group(self):
        """Пост не попал в группу, для которой не был предназначен."""
        form_fields = {
            reverse(
                "posts:group_list", kwargs={"slug": self.group.slug}
            ): Post.objects.exclude(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context["page_obj"]
                self.assertNotIn(expected, form_field)

    def test_post_in_correct_pages(self):
        """Пост отображается на всех необходимых страницах."""
        post = Post.objects.create(
            text="Тестовый текст3", author=self.user, group=self.group
        )

        response_index = self.authorized_client.get(
            reverse("posts:index")
        ).context["page_obj"]
        response_group = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
        ).context["page_obj"]
        response_profile = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": self.user.username})
        ).context["page_obj"]
        response_all = [response_index, response_group, response_profile]
        for response in response_all:
            self.assertIn(post, response)

    def test_comment_only_authorized_client(self):
        """Комментарии доступны авторизированному пользователю."""
        comments_count = Comment.objects.count()
        form_data = {"text": "Тестовый комментарий"}
        response = self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.id}),
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(text="Тестовый комментарий").exists()
        )

    def test_cache_in_index(self):
        """Проверка кеширования index.html."""
        response = self.guest_client.get(reverse("posts:index"))
        r_1 = response.content
        Post.objects.get(id=1).delete()
        response2 = self.guest_client.get(reverse("posts:index"))
        r_2 = response2.content
        self.assertEqual(r_1, r_2)
        cache.clear()
        response3 = self.guest_client.get(reverse("posts:index"))
        r_3 = response3.content
        self.assertNotEqual(r_1, r_3)

    def test_follow_page(self):
        """Проверка подписки на автора поста."""
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertEqual(len(response.context["page_obj"]), 0)
        Follow.objects.get_or_create(user=self.user, author=self.post.author)
        r_2 = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertEqual(len(r_2.context["page_obj"]), 1)
        self.assertIn(self.post, r_2.context["page_obj"])

    def test_follow_in_base_user(self):
        """Проверка что пост не появился в подписке у другого пользователя."""
        base_user = User.objects.create(username="Unfollower")
        self.authorized_client.force_login(base_user)
        r_2 = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertNotIn(self.post, r_2.context["page_obj"])

    def test_unfollow(self):
        """Проверка отписки от автора поста."""
        Follow.objects.all().delete()
        r_3 = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertEqual(len(r_3.context["page_obj"]), 0)
