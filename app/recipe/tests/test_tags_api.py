from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag, Recipe
from recipe.serializers import TagSerializer
from decimal import Decimal

# router from the viewset will set the relative url for us
TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the publically available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@google.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    # create sample tags and check they are created successfully
    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        response = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('name')

        # serialize our objects. There are many of them
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # data base should yield the same result as GET request#
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are only for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@google.com',
            'testpass'
        )

        # each user create a tag
        Tag.objects.create(user=user2, name='Taco')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        response = self.client.get(TAGS_URL)
        # make sure user2's objects cannot be accessed by user1
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'Test tag'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        response = self.client.post(TAGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipe(self):
        """Test filtering tags by those assigned to recipes"""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Dinner')
        recipe = Recipe.objects.create(
            title='Eggs',
            time_minutes=10,
            price=Decimal('9.22'),
            user=self.user
        )
        recipe.tags.add(tag1)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_unique_tags(self):
        """Test returned filtering tags are unique"""
        tag = Tag.objects.create(user=self.user, name='breakfast')
        Tag.objects.create(user=self.user, name='Dinner')
        recipe1 = Recipe.objects.create(
            title='Pancake',
            time_minutes=5,
            price=Decimal('2.33'),
            user=self.user
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title='Porridge',
            time_minutes=10,
            price=Decimal('3.11'),
            user=self.user
        )
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
