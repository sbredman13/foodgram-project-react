from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.permissions import IsAuthorOrAdminPermission
from api.serializers import (IngredientSerializer,
                             RecipeCreateUpdateSerializer, RecipeSerializer,
                             ShortRecipeSerializer, TagSerializer)
from recipes.models import (Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from api.utils import FavoriteMixin


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)


class RecipeViewSet(FavoriteMixin, viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return RecipeCreateUpdateSerializer

        return RecipeSerializer

    @action(detail=True, methods=("post", "delete"))
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == "POST":
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return HttpResponseBadRequest("Рецепт уже в списке покупок.")

            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe,
                context={"request": request}
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            if not ShoppingCart.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                return HttpResponseBadRequest(
                    "Рецепта нет в списке покупок, либо он уже удален."
                )

            shopping_cart = get_object_or_404(
                ShoppingCart,
                user=user,
                recipe=recipe
            )
            shopping_cart.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
                f"{ingredient.name}, {amount} " f"{ingredient.measurement_unit}\n"
            )

        response = HttpResponse(buy_list_text, content_type="text/plain")
        response["Content-Disposition"] = "attachment; filename=shopping-list.txt"

        return response
