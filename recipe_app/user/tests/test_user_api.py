from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('users:create')
CREATE_TOKEN_URL = reverse('users:token')
ME_URL = reverse("users:me")


def create_user(**params):
    """Create and return user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test public user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_is_successful(self):
        payload = {
            "email": "worash.test@example.com",
            "password": "Worash@test",
            "name": "Worash test"
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    # ... (other test methods)

    def test_retrieve_user_unauthorized(self):
        """Test retrieve user needs authentication"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """Test API requests that need authentication"""

    def setUp(self):
        self.user = create_user(email="test@example.com",
                                password="Test@example", name="Test User Name")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # ... (other test methods)

    def test_update_user_profile(self):
        """Test update user profile for logged-in user"""
        payload = {"name": "Worash Abocherugn", "password": "Worash@123***"}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
