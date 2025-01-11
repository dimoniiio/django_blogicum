"""Файл с миксинами."""

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse

from blog.models import Comment, Post


class OnlyAuthorMixin(UserPassesTestMixin):
    """Миксин, который проверяет, является ли пользователь автором объекта."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        """Перенаправляет на страницу поста при отсутствии прав."""
        post_id = self.kwargs.get('post_id')
        return redirect(
            reverse('blog:post_detail', kwargs={'post_id': post_id})
        )


class OnlyUserMixin(UserPassesTestMixin):
    """Класс для проверки пользователя."""

    def test_func(self):
        object = self.get_object()
        return object == self.request.user


class CommentMixin:
    """Класс-миксин комментариев."""

    model = Comment

    def get_success_url(self):
        """Функция перенаправляет на страницу поста,
        к которому относится комментарий
        """
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post_id}
        )

    def get_object(self, queryset=None):
        """Функция берет данные из URL."""
        return get_object_or_404(
            Comment,
            id=self.kwargs.get('comment_id'),
            post_id=self.kwargs.get('post_id')
        )


def get_optimized_posts(manager=Post.objects, filter_published=True,
                        annotate_comments=False):
    """Возвращает оптимизированный кверисет постов
    с возможностью фильтрации и аннотации.
    """
    queryset = manager.select_related('author', 'category', 'location')

    if filter_published:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__date__lte=timezone.localtime(timezone.now()),
        )

    if annotate_comments:
        queryset = queryset.annotate(
            comments_count=Count('comments')
        )

    return queryset.order_by('-pub_date')
