from django.urls import include, path
from djoser.views import TokenDestroyView
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import get_tokens_for_user, UserViewSet


router_v1 = DefaultRouter()

router_v1.register(r"tags", TagViewSet, basename="tags")
router_v1.register(r"ingredients", IngredientViewSet, basename="ingredients")
router_v1.register(r"recipes", RecipeViewSet, basename="recipes")
router_v1.register(r"users", UserViewSet, basename="users")


urlpatterns = [
    path("api/users/set_password/", UserViewSet, name="set_password"),
    #path("auth/token/login/", get_tokens_for_user, name="login"),
    path('auth/', include('djoser.urls.authtoken')),
    path("", include(router_v1.urls),),
    path("auth/token/logout/", TokenDestroyView.as_view(), name="logout"),
]
