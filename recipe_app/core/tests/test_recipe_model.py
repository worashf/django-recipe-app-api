from django.contrib.auth import get_user_model
from django.test import TestCase
from decimal import Decimal
from core import models


class RecipeModelTests(TestCase):

    def test_create_recipe(self):
        """Test creating recipe is successful."""
        user = get_user_model().objects.create_user(
            email="recipe.test@example.com",
            password="Recipe@test"
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title="Doro wot recipe",
            time_minutes=5,
            price=Decimal("5.5"),
            description="Sample doro wot recipe description"
        )
        self.assertEqual(str(recipe), recipe.title)
