from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .utils import page_pagination
from .models import Post, Group, User, Follow
from .constants import NUMBER_OF_POSTS_ON_PAGE
from .forms import PostForm, CommentForm


@cache_page(20, key_prefix='index_page')
def index(request):
    """Рендер главной страницы со списком всех постов."""

    template = 'posts/index.html'
    posts = Post.objects.select_related('group')
    page_obj = page_pagination(request, posts, NUMBER_OF_POSTS_ON_PAGE)

    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


def group_posts(request, slug):
    """Рендер страницы со списком постов сообщества."""

    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = page_pagination(request, posts, NUMBER_OF_POSTS_ON_PAGE)

    context = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def profile(request, username):
    """Рендер страницы профиля пользователя."""

    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = page_pagination(request, posts, NUMBER_OF_POSTS_ON_PAGE)
    following = author.following.exists()

    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Рендер страницы с информацией о посте."""

    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }

    return render(request, 'posts/post_detail.html', context)


@login_required()
def create_post(request):
    """Рендер страницы с формой для создания нового поста."""

    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )

    if form.is_valid():
        post = form.save(commit=False)
        post.author_id = request.user.id
        post.save()
        return redirect(reverse('posts:profile', args=[request.user.username]))

    is_edit = False
    context = {
        'form': form,
        'is_edit': is_edit,
    }

    return render(request, 'posts/create_or_update_post.html', context)


@login_required()
def post_edit(request, post_id):
    """Рендер страницы с формой для редактирования поста."""

    post = get_object_or_404(Post, id=post_id)
    post_detail_url = reverse('posts:post_detail', args=[post_id])

    if post.author_id != request.user.id:
        return redirect(post_detail_url)

    form = PostForm(
        request.POST or None,
        instance=post,
        files=request.FILES or None,
        initial={
            'text': post.text,
            'group': post.group
        })

    if form.is_valid():
        form.save()
        return redirect(post_detail_url)

    is_edit = True
    context = {
        'form': form,
        'post_id': post_id,
        'is_edit': is_edit,
    }

    return render(request, 'posts/create_or_update_post.html', context)


@login_required
def add_comment(request, post_id):
    """Рендер страницы с формой для добавления комментария."""

    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Рендер страницы с постами избранных авторов."""

    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = page_pagination(request, posts, NUMBER_OF_POSTS_ON_PAGE)
    context = {'page_obj': page_obj}

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Оформление подписки на автора."""

    author = get_object_or_404(User, username=username)
    if not (author.following.exists() or author == request.user):
        follow = Follow(
            user=request.user,
            author=get_object_or_404(User, username=username)
        )
        follow.save()

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора."""

    author = get_object_or_404(User, username=username)
    if author.following.exists():
        Follow.objects.filter(user=request.user, author=author).delete()

    return redirect('posts:profile', username=username)
