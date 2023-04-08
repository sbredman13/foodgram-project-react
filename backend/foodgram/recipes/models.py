from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название ингредиента",
        help_text="Название ингредиента",
    )
    measurement_unit = models.CharField(
        max_length=10,
        verbose_name="Единица измерения ингредиента",
        help_text="Единица измерения ингредиента",
    )

    class Meta:
        verbose_name = "ингредиент"
        verbose_name_plural = "Ингредиенты"

        constraints = (
            models.UniqueConstraint(
                fields=("name", "measurement_unit"), name="unique_ingredient"
            ),
        )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название тега",
        help_text="Название тега",
    )
    color = models.CharField(
        max_length=7,
        verbose_name="Цвет для тега",
        help_text="Цвет для тега",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Идентификатор тега",
        help_text="Идентификатор тега",
    )

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта",
        help_text="Название рецепта",
    )
    text = models.TextField(
        verbose_name="Описание рецепта",
        help_text="Описание рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="Игредиенты для рецепта",
        help_text="Игредиенты для рецепта",
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),),
        verbose_name="Время приготовления (в минутах)",
        help_text="Время приготовления (в минутах)",
    )
    image = models.ImageField(
        verbose_name="Изображение для рецепта",
        help_text="Изображение для рецепта",
        upload_to="recipes/",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации рецепта",
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
    )
    tags = models.ManyToManyField(
        Tag,
        through="RecipeTag",
        related_name="recipes",
        verbose_name="Теги рецепта",
        help_text="Теги рецепта",
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT, verbose_name="Ингредиент"
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),), verbose_name="Количество"
    )

    class Meta:
        verbose_name = "ингредиенты"
        verbose_name_plural = "Ингредиенты"

    constraints = (
            models.UniqueConstraint(
                fields=("name", "measurement_unit"), name="unique_ingredient"
            ),
        )
    
    def __str__(self):
        return f"В рецепте {self.recipe} есть ингредиент {self.ingredient}"


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name="Тег")

    class Meta:
        verbose_name = "теги"
        verbose_name_plural = "Теги"

    def __str__(self):
        return f"У рецепта {self.recipe} есть тег {self.tag}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_favorite",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "избранное"
        verbose_name_plural = "Избранное"

        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_favorite_recipe"
            ),
        )

    def __str__(self):
        return f"Рецепт {self.recipe} в избранном у {self.user}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_list",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_shopping_list",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "список покупок"
        verbose_name_plural = "Список покупок"

        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_shopping_list_recipe"
            ),
        )

    def __str__(self):
        return f"Рецепт {self.recipe} в списке покупок у {self.user}"
