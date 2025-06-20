# 📝 Приложение `blog` — система блогов и отзывов

Приложение `blog` реализует функционал публикации постов, просмотра их деталей, добавления комментариев, управления профилем пользователя и категориями. Предусмотрены права доступа, пагинация, кэширование и оптимизация запросов к базе данных.

## 🔧 Основные возможности

- **Создание, редактирование и удаление постов** (только автором)
- **Добавление и удаление комментариев**
- **Регистрация и управление профилем пользователя**
- **Категории постов**
- **Просмотр профиля с пагинацией постов**
- **Права доступа: только автор может редактировать/удалять контент**

## 🌐 Основные URL и представления

| Страница | Представление | Описание |
|---------|---------------|----------|
| `/` | `PostsListView` | Главная страница с последними постами |
| `/posts/<post_id>/` | `PostDetailView` | Детальная страница поста |
| `/posts/create/` | `PostCreateView` | Создание нового поста |
| `/posts/<post_id>/edit/` | `PostUpdateView` | Редактирование поста |
| `/posts/<post_id>/delete/` | `PostDeleteView` | Удаление поста |
| `/profile/<username>/` | `ProfileDetailView` | Профиль пользователя |
| `/profile/edit/` | `ProfileUpdateView` | Редактирование профиля |
| `/category/<slug>/` | `CategoryListView` | Посты по категории |
| `/posts/<post_id>/comment/` | `add_comment` | Добавление комментария |
| `/posts/<post_id>/comments/<comment_id>/edit/` | `CommentUpdateView` | Редактирование комментария |
| `/posts/<post_id>/comments/<comment_id>/delete/` | `CommentDeleteView` | Удаление комментария |
| `/auth/registration/` | `UserCreateView` | Регистрация нового пользователя |

## 👤 Пользователи и права доступа

- Только **авторизованные пользователи** могут:
  - создавать посты и комментарии
  - редактировать и удалять свой контент
- Только **автор поста или комментария** может:
  - редактировать или удалять их
- Незарегистрированные пользователи могут просматривать публичные посты

## 🛠️ Используемые технологии

- **Python**
- **Django**
- **PostgreSQL / SQLite**
- **HTML / CSS / шаблоны Django**


## 📦 Зависимости

Убедитесь, что установлены следующие зависимости:

```bash
pip install django
pip install python-dotenv  # если используются переменные окружения
```


## 📬 Email-уведомления

После изменения профиля пользователь получает email-уведомление. Настройте параметры почты в `settings.py`:


## 📈 Производительность

- Использованы **оптимизированные QuerySet** через `utils.get_optimized_posts`
- Применяется **пагинация** (LIMIT_POSTS из settings)
- Для повышения производительности используется **кэширование**

## ✅ Тестирование

Написаны unit-тесты для проверки работы всех представлений, форм и бизнес-логики.

---
## Если у вас есть вопросы или предложения, свяжитесь с нами: 

Email: [Дмитрий Иванов](dimoniiio@yandex.ru) 

GitHub: [dimoniiio](https://github.com/dimoniiio)
