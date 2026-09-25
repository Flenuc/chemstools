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


class AuthSecurityTests(APITestCase):
    def test_register_is_public(self):
        response = self.client.post(
            reverse('auth_register'),
            {'username': 'nuevo', 'email': 'nuevo@example.com', 'password': 'Clave-Segura-123'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_endpoints_require_authentication_by_default(self):
        response = self.client.get('/api/molecules/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_is_throttled(self):
        url = reverse('token_obtain_pair')
        credentials = {'username': 'nadie', 'password': 'incorrecta'}
        statuses = [self.client.post(url, credentials, format='json').status_code for _ in range(11)]

        self.assertTrue(all(code == status.HTTP_401_UNAUTHORIZED for code in statuses[:10]))
        self.assertEqual(statuses[-1], status.HTTP_429_TOO_MANY_REQUESTS)
