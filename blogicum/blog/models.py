"""Классы для работы с SQLite."""

from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone


User = get_user_model()


class PublishedModel(models.Model):
    """Абстрактная модель. Добвляет флаг is_published
    и время создания created_at.
    """

    is_published = models.BooleanField(
        verbose_name='Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(verbose_name='Добавлено',
                                      auto_now_add=True)

    class Meta:
        abstract = True


class Category(PublishedModel):
    """Класс описывающий таблицу Category в БД."""

    title = models.CharField(verbose_name='Заголовок',
                             max_length=settings.MAX_LENGTH_TITLE)
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        verbose_name='Идентификатор',
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, '
            'цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        """Метод используется для получения
        «читаемого» представления объекта.
        """
        return self.title[:settings.PRE_TEXT_LEN]


class Location(PublishedModel):
    """Класс описывающий таблицу Location в БД."""

    name = models.CharField(verbose_name='Название места',
                            max_length=settings.MAX_LENGTH_TITLE)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        """Метод используется для получения
        «читаемого» представления объекта.
        """
        return self.name[:settings.PRE_TEXT_LEN]


class Post(PublishedModel):
    """Класс описывающий таблицу Post в БД."""

    title = models.CharField(verbose_name='Заголовок',
                             max_length=settings.MAX_LENGTH_TITLE)
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
    )
    image = models.ImageField(
        verbose_name='Фото',
        blank=True,
        upload_to='post_images'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ['-pub_date', 'title']

    def __str__(self):
        """Метод используется для получения
        «читаемого» представления объекта.
        """
        return self.title[:settings.PRE_TEXT_LEN]

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={"pk": self.pk})


class Comment(models.Model):
    """Класс описывающий комментарий."""

    text = models.TextField(verbose_name='Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        related_name='authors'
    )

    def __str__(self):
        """Метод используется для получения
        «читаемого» представления объекта.
        """
        return self.text[:settings.PRE_TEXT_LEN]

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)
