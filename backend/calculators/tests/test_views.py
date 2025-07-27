from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class CalculatorsAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpassword123')
        
    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_glossary_list(self):
        url = reverse('glossaryterm-list')
        response = self.client.get(url)
        expected_term_count = 7
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_term_count)
        self.assertEqual(response.data[0]['term'], 'Ácido')

    def test_ph_calculator_with_ph(self):
        url = reverse('ph-calculator')
        data = {'ph': 3}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertAlmostEqual(response.data['poh'], 11.0, places=2)
        self.assertEqual(response.data['h_concentration'], '1.00e-03')

    def test_ph_calculator_with_h_concentration(self):
        url = reverse('ph-calculator')
        data = {'h_concentration': 0.001}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertAlmostEqual(response.data['ph'], 3.0, places=2)
        self.assertAlmostEqual(response.data['poh'], 11.0, places=2)

    def test_ph_calculator_invalid_input(self):
        url = reverse('ph-calculator')
        data = {'invalid_key': 10}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ph_calculator_non_numeric_input(self):
        url = reverse('ph-calculator')
        data = {'ph': 'not-a-number'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)