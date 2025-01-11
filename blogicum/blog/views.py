"""View-функции приложения blog.
venws.index -- главная страница.
venws.post_detail -- страница с одним постом.
venws.category_posts -- страница категории.
"""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from blog.models import Category, Post, User
from .forms import CommentForm, PostForm, UserForm
from .utils import (
    CommentMixin,
    OnlyAuthorMixin,
    OnlyUserMixin,
    get_optimized_posts,
)


class UserCreateView(CreateView):
    """Класс регистрации нового пользователя."""

    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста."""

    model = Post
    form_class = PostForm
    success_url = reverse_lazy('blog:profile')

    def form_valid(self, form):
        """Автоматическое заполнение поля author при валидации поста."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Функция для перенаправления на страницу пользователя."""
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostDetailView(DetailView):
    """Класс выводящий один пост."""

    model = Post
    context_object_name = 'post'
    template_name = 'blog/post_detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        """Функция проверяет право доступа к неопубликованному посту."""
        queryset = get_optimized_posts(filter_published=False)
        obj = get_object_or_404(queryset, pk=self.kwargs.get('post_id'))
        if obj.author != self.request.user:
            obj = get_object_or_404(
                get_optimized_posts(),
                pk=self.kwargs.get('post_id'),
            )
        return obj

    def get_context_data(self, **kwargs):
        """Функция вывода комментариев к посту."""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostsListView(ListView):
    """Список всех постов."""

    model = Post
    paginate_by = settings.LIMIT_POSTS

    def get_queryset(self):
        """Функция вывода постов."""
        return get_optimized_posts(annotate_comments=True)


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """Класс редактирования поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        """Функция для перенаправления на страницу поста."""
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.object.id})


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """Класс удаление поста."""

    model = Post
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        """Метод добавления контекста."""
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class ProfileDetailView(ListView):
    """Профиль пользователя с пагинацией постов."""

    model = User
    context_object_name = 'posts'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'auth/user_detail.html'  # Укажите путь к вашему шаблону
    paginate_by = settings.LIMIT_POSTS

    def get_username(self):
        """Метод возвращает объект User."""
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_queryset(self):
        """Получаем QuerySet для списка постов"""
        user = self.get_username()
        flag_filter_published = self.request.user != user
        return get_optimized_posts(
            user.posts,
            filter_published=flag_filter_published,
            annotate_comments=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_username()
        return context


class ProfileUpdateView(OnlyUserMixin, UpdateView):
    """Класс редактирования профиля."""

    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_success_url(self):
        """Функция для перенаправления на страницу пользователя."""
        send_mail(
            subject='Обновление данных',
            message='Вы обновили данные в своём профиле',
            from_email='admin@mail.ru',
            recipient_list=['to@example.ru'],
            fail_silently=True
        )
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.object.username}
        )


class CommentUpdateView(CommentMixin, OnlyAuthorMixin, UpdateView):
    """Класс редактирования комментария."""

    form_class = CommentForm


class CommentDeleteView(CommentMixin, OnlyAuthorMixin, DeleteView):
    """Класс удаления комментария."""

    template_name = 'blog/comment_form.html'


class CategoryListView(ListView):
    """Все посты одной категории."""

    model = Post
    template_name = 'blog/category_list.html'  # Путь к шаблону
    context_object_name = 'posts'
    paginate_by = settings.LIMIT_POSTS

    def get_category(self):
        """Метод возвращает объект Category."""
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        """Метод возвращает список элементов для представления."""
        return get_optimized_posts(
            self.get_category().posts,
            annotate_comments=True
        )

    def get_context_data(self, **kwargs):
        """Метод используется для добавления дополнительных данных в контекст,
        который будет передан в шаблон.
        """
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


@login_required
def add_comment(request, post_id):
    """Функция добовления комментария."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)
