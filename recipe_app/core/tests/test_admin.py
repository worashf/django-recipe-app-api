from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class AdminSiteTest(TestCase):

    def setUp(self):  # setup important test data
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin2@uppert.com",
            password="Admin2@123"
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="testuser7@example.com",
            password="TestUser@123",
            name="Test User7"
        )

    def test_users_list(self):
        # Test that users are listed on the page
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        url = reverse("admin:core_user_add")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
