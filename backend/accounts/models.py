from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Subscription(models.Model):  # Follow
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions', verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers', verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('subscriber', 'author')

    def __str__(self):
        return f'{self.subscriber} подписан на {self.author}' 