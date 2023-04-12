from distutils.util import strtobool
from django_filters import rest_framework
from rest_framework.filters import SearchFilter

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


CHOICES_LIST = (("0", "False"), ("1", "True"))


class IngredientSearch(SearchFilter):
    search_param = "name"

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipeFilter(rest_framework.FilterSet):
    is_favorited = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST, method="is_favorited_method"
    )
    is_in_shopping_cart = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST, method="is_in_shopping_cart_method"
    )
    author = rest_framework.NumberFilter(
        field_name="author",
        lookup_expr="exact"
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all()
    )

    def is_favorited_method(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        favorites = Favorite.objects.filter(
            user=self.request.user
        ).values_list("recipe__id", flat=True)
        new_queryset = queryset.filter(id__in=favorites)

        if not strtobool(value):
            return queryset.difference(new_queryset)

        return queryset.filter(id__in=favorites)

    def is_in_shopping_cart_method(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        shopping_cart = ShoppingCart.objects.filter(
            user=self.request.user
        ).values_list("recipe__id", flat=True)
        new_queryset = queryset.filter(id__in=shopping_cart)

        if not strtobool(value):
            return queryset.difference(new_queryset)

        return queryset.filter(id__in=shopping_cart)

    class Meta:
        model = Recipe
        fields = ("author", "tags")
