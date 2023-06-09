from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, serializers
from djoser.serializers import UserSerializer

from api.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscriptions, User


class CustomUserSerializer(UserSerializer):

    is_subscribed = serializers.SerializerMethodField(
        method_name="get_is_subscribed"
    )

    def get_is_subscribed(self, obj):
        user = self.context["request"].user

        if user.is_anonymous:
            return False

        return Subscriptions.objects.filter(user=user, author=obj).exists()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit",)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id", read_only=True)
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit",
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class CreateUpdateRecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1, message="Количество ингредиента должно быть 1 или более."
            ),
        )
    )

    class Meta:
        model = Ingredient
        fields = ("id", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(
        method_name="get_is_favorited"
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name="get_is_in_shopping_cart"
    )

    def get_ingredients(self, obj):
        return RecipeIngredientsSerializer(
            RecipeIngredient.objects.filter(recipe=obj).all(),
            many=True,
        ).data

    def get_is_favorited(self, obj):
        user = self.context["request"].user

        if user.is_anonymous:
            return False

        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user

        if user.is_anonymous:
            return False

        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()

    class Meta:
        model = Recipe
        exclude = ("pub_date",)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = CreateUpdateRecipeIngredientsSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1, message="Время приготовления должно быть 1 или более."
            ),
        )
    )

    def validate_tags(self, value):
        if not value:
            raise exceptions.ValidationError(
                "Нужно добавить хотя бы один тег."
            )

        return value

    def validate_ingredients(self, value):
        if not value:
            raise exceptions.ValidationError(
                "Нужно добавить хотя бы один ингредиент."
            )

        ingredients = [item["id"] for item in value]
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                raise exceptions.ValidationError(
                    "У рецепта не может быть два одинаковых ингредиента."
                )

        return value

    def add_ingredients(self, recipe, ingredients):
        ex_ids = RecipeIngredient.objects.filter(
            recipe=recipe,
            ingredient_id__in=[i['id'] for i in ingredients]
        ).values_list('ingredient_id', flat=True)
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, pk=ingredient["id"]),
                amount=ingredient["amount"]
            ) for ingredient in ingredients if ingredient['id'] not in ex_ids
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

        for ingredient in ingredients:
            if ingredient['id'] in ex_ids:
                amount = ingredient["amount"]
                ingredient = get_object_or_404(Ingredient, pk=ingredient["id"])

                RecipeIngredient.objects.filter(
                    recipe=recipe,
                    ingredient=ingredient
                ).update(amount=amount)

    def create(self, validated_data):
        author = self.context.get("request").user
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)

        self.add_ingredients(recipe, ingredients)

        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.set(tags)

        ingredients = validated_data.pop("ingredients", None)
        if ingredients is not None:
            instance.ingredients.clear()

            self.add_ingredients(recipe, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance, context={"request": self.context.get("request")}
        )

        return serializer.data

    class Meta:
        model = Recipe
        exclude = ("pub_date",)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
