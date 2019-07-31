from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@google.com',
            password='pw123'
        )
        # automate login the superuser that we just created
        # useful for testing
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email='test@google.com',
            password='password123',
            name='Test Name'
        )

    def test_users_listed(self):
        """Test that users are listed on user page in admin"""
        # this relative url link is included in admin by default
        url = reverse('admin:core_user_changelist')
        # use test client to get http GET request on the url
        response = self.client.get(url)

        # check that the http response contains specified items
        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        """Test the the user edit page works"""
        # test that the fields are correctly displayed in the user
        # detail edit page in admin
        url = reverse('admin:core_user_change', args=[self.user.id])
        response = self.client.get(url)

        # check if page ok, since status 200 means page is OK
        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
