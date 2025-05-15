from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

class User(AbstractUser):
    email = models.EmailField(
        'Email',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

    def __str__(self):
        return self.username

User = get_user_model()

class Subscription(models.Model):  # Follow
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions', verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='account_authors',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('subscriber', 'author')

    def __str__(self):
        return f'{self.subscriber} подписан на {self.author}' 