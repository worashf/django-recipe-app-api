from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipe import views

router = DefaultRouter()
router.register("recipes", views.RecipeAPIViewSet)


app_name = "recipes"


urlpatterns = [
    path("", include(router.urls)),
]
