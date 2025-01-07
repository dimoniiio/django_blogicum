"""View-функции приложения pages."""
from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPage(TemplateView):
    """Страница 'О проекте'."""

    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    """Страница 'Правила'."""

    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Обработка ошибки 404."""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Обработка ошибки 403."""
    return render(request, 'pages/403csrf.html', status=403)


def server_error_500(request):
    """Обработка ошибки 500."""
    return render(request, 'pages/500.html', status=500)
