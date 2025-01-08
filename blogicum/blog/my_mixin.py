"""Файл с миксинами."""

from django.shortcuts import redirect, reverse
from django.contrib.auth.mixins import UserPassesTestMixin


class OnlyAuthorMixin(UserPassesTestMixin):
    """Миксин, который проверяет, является ли пользователь автором объекта."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        """Перенаправляет на страницу поста при отсутствии прав."""
        obj = self.get_object()
        return redirect(
            reverse('blog:post_detail', kwargs={'post_id': obj.id})
        )


class OnlyUserMixin(UserPassesTestMixin):
    """Класс для проверки пользователя."""

    def test_func(self):
        object = self.get_object()
        return object == self.request.user