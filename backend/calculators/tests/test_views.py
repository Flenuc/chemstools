from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import GlossaryTerm # Importar el modelo

User = get_user_model()

class CalculatorsAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpassword123')
        # FIX: Create glossary terms directly in the test setup
        # to make the test independent of data migrations.
        terms = [
            {"term": "Ácido", "definition": "Una sustancia que puede donar un protón (H+) a otra sustancia."},
            {"term": "Base", "definition": "Una sustancia que puede aceptar un protón (H+)."},
            {"term": "Mol", "definition": "La unidad del SI para la cantidad de sustancia."},
            {"term": "pH", "definition": "Una medida de la acidez o alcalinidad."},
            {"term": "pOH", "definition": "Una medida de la basicidad de una disolución."},
            {"term": "Enlace Covalente", "definition": "Un tipo de enlace químico que implica el intercambio de pares de electrones."},
            {"term": "Enlace Iónico", "definition": "Un tipo de enlace químico que implica atracción electrostática."}
        ]
        for term_data in terms:
            GlossaryTerm.objects.create(term=term_data["term"], definition=term_data["definition"])

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

    # FIX: Move the following tests inside the CalculatorsAPITests class
    def test_solution_calculator_mass_mass(self):
        """
        Test solution calculator with solute and solvent mass.
        """
        url = reverse('solution-calculator')
        data = {'solute_mass': 10, 'solvent_mass': 90}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['percent_mass_mass'], "10.00")

    def test_solution_calculator_mass_volume(self):
        """
        Test solution calculator with solute mass and solution volume.
        """
        url = reverse('solution-calculator')
        data = {'solute_mass': 25, 'solution_volume': 100}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['percent_mass_volume'], "25.00")

    def test_solution_calculator_with_density(self):
        """
        Test solution calculator with density to calculate both percentages.
        """
        url = reverse('solution-calculator')
        data = {'solute_mass': 15, 'solvent_mass': 85, 'solution_volume': 95, 'density': 1.05}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['percent_mass_mass'], "15.00")
        self.assertEqual(response.data['percent_mass_volume'], "15.79")

    def test_solution_calculator_insufficient_data(self):
        """
        Test that an error is returned if not enough data is provided.
        """
        url = reverse('solution-calculator')
        data = {'solute_mass': 10}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_solution_calculator_negative_input(self):
        """
        Test that an error is returned for negative input values.
        """
        url = reverse('solution-calculator')
        data = {'solute_mass': -10, 'solvent_mass': 90}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)