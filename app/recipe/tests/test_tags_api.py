from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.text import APIClient
from core.models import Tag
from recipe.serializers import TagSerializer

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
        self.client=APIClient()
        self.client.force_authenticate(self.user)

    # create sample tags and check they are created successfully
    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        response = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')

        #serialize our objects. There are many of them
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # data base should yield the same result as GET request
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are only for the authenticated user"""
        user2=get_user_model().objects.create_user(
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
