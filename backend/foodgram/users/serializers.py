from django.contrib.auth import authenticate
from djoser.conf import settings
from djoser.serializers import TokenCreateSerializer, UserCreateSerializer
from rest_framework import serializers

from api.serializers import CustomUserSerializer, ShortRecipeSerializer
from recipes.models import Recipe
from users.models import Subscriptions, User


class SignupSerializer(UserCreateSerializer):

    is_subscribed = serializers.SerializerMethodField(
        method_name="get_is_subscribed"
    )

    def get_is_subscribed(self, obj):
        user = self.context["request"].user

        if user.is_anonymous:
            return False

        return Subscriptions.objects.filter(user=user, author=obj).exists()

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "id",
            "is_subscribed",
        )


class TokenSerializer(TokenCreateSerializer):

    def validate(self, attrs):
        password = attrs.get("password")
        params = {settings.LOGIN_FIELD: attrs.get(settings.LOGIN_FIELD)}
        self.user = authenticate(
            request=self.context.get("request"), **params, password=password
        )
        if not self.user:
            self.user = User.objects.filter(**params).first()
            if self.user and not self.user.check_password(password):
                self.fail("invalid_credentials")
        if self.user:
            return attrs
        self.fail("invalid_credentials")


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(method_name="get_recipes")
    recipes_count = serializers.SerializerMethodField(
        method_name="get_recipes_count"
    )

    def get_srs(self):
        return ShortRecipeSerializer

    def get_recipes(self, obj):
        author_recipes = Recipe.objects.filter(author=obj)

        if "recipes_limit" in self.context.get("request").GET:
            recipes_limit = self.context.get("request").GET["recipes_limit"]
            author_recipes = author_recipes[: int(recipes_limit)]

        if author_recipes:
            serializer = self.get_srs()(
                author_recipes,
                context={"request": self.context.get("request")},
                many=True,
            )
            return serializer.data

        return []

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
