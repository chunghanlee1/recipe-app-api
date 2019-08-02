from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# Make test client that we can use to make request and check response
from rest_framework.test import APIClient
from rest_framework import status

# A constant value will be in all Caps in Django convention
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')

def create_user(**params):
    return get_user_model.objects.create_user(**params)


# Public means unauthenticated visitor. Private is authenticated
class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()
    
    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'test@google.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        # send post request to creation link
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password'])
        # make sure password not returned to user for security reasons
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        """Test creating a user that already exists"""
        payload = {'email': 'test@google.com', 'password': 'testpass'}
        # create user beforehand
        create_user(**payload)
        # try to create user again
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password must bemore than 5 characters"""
        payload = {'email': 'test@google.com', 'password': 'test'}
        response=self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {'email': 'test@google.com', 'password': 'testpass'}
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)
        # check that the token exists when we login
        self.assertIn('token', response.data) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid credentials(self):
        """Test that token token is not created if invalid credentials are given"""
        create_user(email='test@google.com', password='testpass')
        payload = {'email': 'test@google.com', 'password': 'wrongpass'} 
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created for non-existant user"""
        payload = {'email': 'test@google.com', 'password': 'testpass'} 
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that valid email and password are required"""
        response = self.client.post(TOKEN_URL, {'email':'wrongemail', 'password': ''})
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentcation is required for users"""
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


ME_URL = reverse('user:me')


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@google.com',
            password='testpass',
            name='Private Test User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })
    
    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the ME_URL"""
        response = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_400_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'new name', 'password': 'newpassword'}
        response = self.client.patch(ME_URL, payload)
        # refresh db to update stored values
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)