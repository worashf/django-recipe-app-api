from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from decimal import Decimal

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import (
     RecipeSerializer,
     RecipeDetailSerializer)

RECIPE_URL = reverse("recipes:recipe-list")


def recipe_detail_url(recipe_id):
    """ Create  and return recipe detail url. """
    return reverse("recipe:recipe-detail", args=[recipe_id])


def create_recipe(user, **params):
    """Create and return sample recipe."""
    defaults = {
        "title": "Noodle recipe",
        "price": Decimal("10.5"),
        "time_minutes": 30,
        "description": "Sample description",
        "link": "https://samplerecipe.com"
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Authentication is required to list recipe."""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="worash.test@example.com",
            password="Testworash@123"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieve list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test recipe list is limited to the authenticated user."""
        other_user = get_user_model().objects.create_user(
            email="otheruser@example.com",
            password="Testworash@123"
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user).order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail. """
        recipe = create_recipe(user=self.user)
        url = recipe_detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_recipe(self):
        """ Test creating a recipe. """

        recipe_payload = {
            "title": "Chease recipe",
            "price": Decimal("5.6"),
            "time_minutes": 60
        }

        res = self.client.post(RECIPE_URL, recipe_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])

        for k, v in recipe_payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(self.user, recipe.user)

    def test_partial_update(self):
        """Test partial update of a recipe."""
        original_link = "https://example.com/recipe.pdf"
        recipe = create_recipe(
             user=self.user,
             title="Sample recipe title",
             link=original_link,
             )
        payload = {"title": "New recipe title"}
        url = recipe_detail_url(recipe.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of a recipe."""
        recipe = create_recipe(
            title="Sample recipe title",
            user=self.user,
            link="https://example.com/recipe.pdf",
            description="Sample recipe description.",
        )

        payload = {
            "title": "New recipe title",
            "link": "https://example.com/new-recipe.pdf",
            "description": "New recipe description",
            "time_minutes": 10,
            "price": Decimal("2.50"),
        }

        url = recipe_detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe_successful(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(user=self.user)

        url = recipe_detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error."""

        new_user = get_user_model().objects.create_user(
            email="worash@example.com",
            password="Testworash@123"
        )
        recipe = create_recipe(user=new_user)

        url = recipe_detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
