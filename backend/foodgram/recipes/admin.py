from django.contrib import admin
from django.db.models import Count
from recipes.models import Ingredient, Recipe, Tag


class RecipeIngredientInLine(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


class RecipeTagInLine(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "favorite_count",
    )
    list_filter = (
        "author",
        "tags",
        "name",
    )
    inlines = (RecipeIngredientInLine, RecipeTagInLine)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(favorite_count=Count("in_favorite"))

    @staticmethod
    def favorite_count(obj):
        return obj.favorite_count


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
    list_filter = ("name",)
