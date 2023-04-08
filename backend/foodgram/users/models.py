from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):

    username = models.CharField(
        unique=True,
        max_length=150,
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+$",
                message="Недопустимые символы в имени",
            )
        ],
    )
    email = models.EmailField(
        unique=True,
        blank=False, null=False,
        max_length=254
    )
    password = models.CharField(
        max_length=150,
        blank=True
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribes",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "подписка"
        verbose_name_plural = "Подписки"

        constraints = (
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="no_self_subscribe"
            ),
            models.UniqueConstraint(
                fields=("user", "author"), name="unique_subscription"
            ),
        )

    def __str__(self):
        return f"Подписка {self.user} на {self.author}"
