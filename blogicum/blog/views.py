"""View-функции приложения blog.
venws.index -- главная страница.
venws.post_detail -- страница с одним постом.
venws.category_posts -- страница категории.
"""

from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from blog.models import Category, Comment, Post, User
from .forms import CommentForm, PostForm, UserForm


LIMIT_POSTS: int = 10


class OnlyAuthorMixin(UserPassesTestMixin):
    """Класс для проверки авторства."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class OnlyUserMixin(UserPassesTestMixin):
    """Класс для проверки пользователя."""

    def test_func(self):
        object = self.get_object()
        return object == self.request.user


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
        obj = super().get_object(queryset=queryset)
        if not obj.is_published and obj.author != self.request.user:
            raise Http404("Post is not published or you are not the author")
        return obj

    def get_context_data(self, **kwargs):
        """Функция вывода комментариев к посту."""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comment.select_related('author')
        )
        return context


class PostsListView(ListView):
    """Список всех постов."""

    model = Post
    paginate_by = LIMIT_POSTS

    def get_queryset(self):
        """Функция вывода постов."""
        return super().get_queryset().filter(
            is_published=True,
            category__is_published=True,
            pub_date__date__lte=timezone.localtime(timezone.now())
        )


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """Класс редактирования поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        """Функция перехвата исключений."""
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            post = self.get_object()
            return redirect(reverse(
                'blog:post_detail', kwargs={'post_id': post.id}
            ))

    def get_success_url(self):
        """Функция для перенаправления на страницу поста."""
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.id})


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """Класс удаление поста."""

    model = Post
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'


class ProfileDetailView(DetailView):
    """Профиль пользователя."""

    model = User
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        """Функция получения всех постов пользователя."""
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        post_list = Post.objects.filter(
            author=user
        )  # Получаем список всех постов пользователя
        paginator = Paginator(post_list, LIMIT_POSTS)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class ProfileCreateView(LoginRequiredMixin, CreateView):
    """Регистрация нового пользователя."""

    model = User
    form_class = UserForm


class ProfileUpdateView(OnlyUserMixin, UpdateView):
    """Класс редактирования профиля."""

    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_success_url(self):
        """Функция для перенаправления на страницу пользователя."""
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.object.username}
        )

    send_mail(
        subject='Обновление данных',
        message='Вы обновили данные в своём профиле',
        from_email='admin@mail.ru',
        recipient_list=['to@example.ru'],
        fail_silently=True
    )


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    """Класс редактирования комментария."""

    model = Comment
    form_class = CommentForm
    success_url = reverse_lazy('post_detail')

    def get_object(self, queryset=None):
        """Функция берет данные из URL."""
        return get_object_or_404(
            Comment,
            id=self.kwargs.get('comment_id'),
            post_id=self.kwargs.get('post_id')
        )

    def form_valid(self, form):
        """Функция перенаправляет на страницу поста,
        к которому относится комментарий
        """
        self.object = form.save()
        return redirect('blog:post_detail', post_id=self.object.post_id)


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    """Класс удаления комментария."""

    model = Comment
    template_name = 'blog/comment_form.html'

    def get_success_url(self):
        """Функция получаем ID поста, к которому принадлежит комментарий."""
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.post_id}
        )

    def get_object(self, queryset=None):
        """Метод получения объекта, чтобы использовать comment_id"""
        comment_id = self.kwargs.get('comment_id')
        return get_object_or_404(Comment, id=comment_id)

    def delete(self, request, *args, **kwargs):
        """Метод удаления комментария."""
        self.object = self.get_object()
        self.object.delete()  # Удаляем комментарий
        return redirect(self.get_success_url())


class CategoryListView(ListView):
    """Все посты одной категории."""

    model = Post
    template_name = 'blog/category_list.html'  # Путь к шаблону
    context_object_name = 'posts'
    paginate_by = LIMIT_POSTS

    def get_queryset(self):
        """Метод возвращает список элементов для представления."""
        self.category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'],
            is_published=True
        )
        return Post.objects.select_related(
            'author',
            'category',
            'location',
        ).filter(
            category=self.category,
            is_published=True,
            pub_date__date__lte=timezone.localtime(timezone.now())
        )

    def get_context_data(self, **kwargs):
        """Метод используется для добавления дополнительных данных в контекст,
        который будет передан в шаблон.
        """
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


@login_required
def simple_view(request):
    """Функция проверки доступа"""
    return HttpResponse('Страница для залогиненных пользователей!')


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
