from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import ShortRecipeSerializer
from recipes.models import Recipe, Favorite


class FavoriteMixin(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    @action(detail=True, methods=("post", "delete"))
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == "POST":
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return HttpResponseBadRequest("Рецепт уже в избранном.")

            Favorite.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe,
                context={"request": request}
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                return HttpResponseBadRequest(
                    "Рецепта нет в избранном, либо он уже удален."
                )

            favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
            favorite.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
