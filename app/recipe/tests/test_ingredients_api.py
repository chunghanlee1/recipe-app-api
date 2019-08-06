from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer
from decimal import Decimal


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Test the publically available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """Test private ingredients API"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@google.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """Test retrieve a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited(self):
        """Test that only ingredients created by the user are returned"""
        user2 = get_user_model().objects.create_user(
            'test@hotmail.com',
            'testpassss'
        )

        Ingredient.objects.create(user=user2, name='Fish')
        ingredient = Ingredient.objects.create(user=self.user, name='Meat')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def create_ingredient_successful(self):
        """Test create ingredients successful"""
        payload = {'name': 'Cabbage'}
        self.client.post(INGREDIENTS_URL, payload)
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating invalid ingredients list"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes"""
        ingredient1 = Ingredient.objects.create(
            user=self.user, name='Apples'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user, name='Turkey'
        )
        recipe = Recipe.objects.create(
            title='Apple crumble',
            time_minutes=5,
            price=10,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_unique_assigned_ingredient_retrieved(self):
        """Test filtering ingredients assigned returns unique values"""
        ingredient = Ingredient.objects.create(
            user=self.user, name='eggs'
        )
        Ingredient.objects.create(user=self.user, name='cheese')
        recipe1 = Recipe.objects.create(
            title='Eggs Ben',
            time_minutes=10,
            price=Decimal('22.11'),
            user=self.user
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title='Tikka',
            time_minutes=20,
            price=Decimal('9.01'),
            user=self.user
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
