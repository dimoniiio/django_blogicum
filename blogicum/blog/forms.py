from django import forms
from django.core.exceptions import ValidationError
# Импорт функции для отправки почты.
from django.core.mail import send_mail

# Импортируем класс модели Birthday.
from .models import Post, User, Comment


class PostForm(forms.ModelForm):
    """Класс форма модели Post."""

    class Meta:
        """Класс Meta формы PostForm."""

        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class UserForm(forms.ModelForm):
    """Класс форма модели User."""

    class Meta:
        """Класс Meta формы UserForm."""

        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CommentForm(forms.ModelForm):
    """Класс форма модели Comment."""

    class Meta:
        """Класс Meta формы CommentForm."""

        model = Comment
        fields = ('text',)
