from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import CustomUser

class UserProfileViewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword123')
        self.url = reverse('user_profile')

    def test_get_profile_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_authenticated(self):
        # Para simplejwt, la autenticación se hace con un token, no con force_authenticate
        # Aquí simulamos la obtención y uso del token
        login_url = reverse('token_obtain_pair')
        login_response = self.client.post(login_url, {'username': 'testuser', 'password': 'testpassword123'}, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

