from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()

POST_LIMIT = 10


def paginator(request, posts):
    """Паджинатор."""
    paginator = Paginator(posts, POST_LIMIT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return {
        "paginator": paginator,
        "page_number": page_number,
        "page_obj": page_obj,
    }


@cache_page(20)
def index(request):
    """Генерирует index.html."""
    template = "posts/index.html"
    posts = Post.objects.all().order_by("-pub_date")
    context = paginator(request, posts)
    return render(request, template, context)


def group_posts(request, slug):
    """Генерирует group_list.html."""
    template = "posts/group_list.html"
    group = get_object_or_404(Group, slug=slug)
    context = {
        "group": group,
    }
    context.update(paginator(request, group.posts.all()))
    return render(request, template, context)


def profile(request, username):
    """Генерирует profile.html."""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    posts_count = post_list.count()
    following = request.user.is_authenticated
    if following:
        following = author.following.filter(user=request.user).exists()
    context = {
        "author": author,
        "posts": post_list,
        "posts_count": posts_count,
        "following": following,
    }
    context.update(
        paginator(
            request,
            Post.objects.all().order_by("-pub_date").filter(author=author),
        )
    )
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    """Генерирует post_detail.html."""
    posts = get_object_or_404(Post, id=post_id)
    author = posts.author
    comments = posts.comments.all
    form = CommentForm()
    posts_count = Post.objects.filter(author=author).count()
    context = {
        "posts": posts,
        "posts_count": posts_count,
        "comments": comments,
        "form": form,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    """Генерирует post_create.html."""
    if request.method == "POST":
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:profile", request.user)
        return render(request, "posts/create_post.html", {"form": form})
    form = PostForm()
    return render(request, "posts/create_post.html", {"form": form})


@login_required
def post_edit(request, post_id):
    """Генерирует post_edit.html."""
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if request.user != post.author:
        return redirect("posts:post_detail", post.id)
    if form.is_valid():
        post = form.save()
        post.author = request.user
        post.save()
        return redirect("posts:post_detail", post.id)
    return render(
        request,
        "posts/create_post.html",
        {"form": form, "post": post, "is_edit": is_edit},
    )


@login_required
def add_comment(request, post_id):
    """Генерирует ."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    """Генерирует страницу подписок."""
    follower = Follow.objects.filter(user=request.user).values_list(
        "author_id", flat=True
    )
    posts = Post.objects.filter(author_id__in=follower)
    context = paginator(request, posts)
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    """Возможность подписаться."""
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("posts:follow_index")


@login_required
def profile_unfollow(request, username):
    """Возможность отписаться."""
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect("posts:follow_index")
