from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientSearch, RecipeFilter
from api.permissions import IsAuthorOrAdminPermission
from api.serializers import (IngredientSerializer,
                             RecipeCreateUpdateSerializer, RecipeSerializer,
                             ShortRecipeSerializer, TagSerializer)
from recipes.models import (Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag, Favorite)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    filter_backends = (IngredientSearch,)
    search_fields = ("^name",)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return RecipeCreateUpdateSerializer

        return RecipeSerializer

    def bace_recipe_action(self, request, pk, model, error):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == "POST":
            if model.objects.filter(user=user, recipe=recipe).exists():
                return HttpResponseBadRequest(f"Рецепт уже в {error}.")
            model.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe,
                context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            if not model.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                return HttpResponseBadRequest(
                    f"Рецепта нет в {error}, либо он уже удален."
                )

            favorite = get_object_or_404(
                model,
                user=user,
                recipe=recipe
            )
            favorite.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=("post", "delete"))
    def favorite(self, request, pk=None):
        return self.bace_recipe_action(request, pk, Favorite, "избраном")

    @action(detail=True, methods=("post", "delete"))
    def shopping_cart(self, request, pk=None):
        return self.bace_recipe_action(
            request,
            pk,
            ShoppingCart,
            "списке покупок"
        )

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(
            user=self.request.user
        ).values_list("recipe__id", flat=True)
        buy_list = (
            RecipeIngredient.objects.filter(recipe__in=shopping_cart)
            .values("ingredient")
            .annotate(count=Sum("amount"))
        )

        buy_list_text = "Список покупок с сайта Foodgram:\n\n"
        for item in buy_list:
            ingredient = Ingredient.objects.get(pk=item["ingredient"])
            amount = item["count"]
            buy_list_text += (
                f"{ingredient.name}, {amount} "
                f"{ingredient.measurement_unit}\n"
            )

        response = HttpResponse(buy_list_text, content_type="text/plain")
        response[
            "Content-Disposition"
        ] = "attachment; filename=shopping-list.txt"

        return response
