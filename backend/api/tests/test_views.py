from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class HealthCheckTests(APITestCase):
    def test_health_check_returns_200(self):
        """
        Asegura que el endpoint de health check devuelve un estado 200 OK.
        """
        url = reverse('health-check')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'status': 'ok'})