from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from reactions.models import BalancedReaction
from reactions.utils import ChemicalEquationBalancer

class ChemicalEquationBalancerTests(TestCase):
    """
    Tests para la clase ChemicalEquationBalancer
    """
    
    def setUp(self):
        self.balancer = ChemicalEquationBalancer()
    
    def test_parse_compound_simple(self):
        """Test parsing de compuestos simples"""
        result = self.balancer.parse_compound('H2O')
        expected = {'H': 2, 'O': 1}
        self.assertEqual(result, expected)
    
    def test_parse_compound_complex(self):
        """Test parsing de compuestos complejos"""
        result = self.balancer.parse_compound('Ca(OH)2')
        expected = {'Ca': 1, 'O': 2, 'H': 2}
        self.assertEqual(result, expected)
    
    def test_parse_equation(self):
        """Test parsing de ecuaciones"""
        reactants, products = self.balancer.parse_equation('H2 + O2 -> H2O')
        self.assertEqual(reactants, ['H2', 'O2'])
        self.assertEqual(products, ['H2O'])
    
    def test_balance_synthesis_reaction(self):
        """Test balanceo de reacción de síntesis"""
        result = self.balancer.balance_equation('H2 + O2 -> H2O')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['balanced_equation'], '2H2 + O2 -> 2H2O')
        self.assertEqual(result['reaction_type'], 'síntesis')
    
    def test_balance_decomposition_reaction(self):
        """Test balanceo de reacción de descomposición"""
        result = self.balancer.balance_equation('H2O2 -> H2O + O2')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['balanced_equation'], '2H2O2 -> 2H2O + O2')
        self.assertEqual(result['reaction_type'], 'descomposición')
    
    def test_balance_combustion_reaction(self):
        """Test balanceo de reacción de combustión"""
        result = self.balancer.balance_equation('CH4 + O2 -> CO2 + H2O')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['balanced_equation'], 'CH4 + 2O2 -> CO2 + 2H2O')
        self.assertEqual(result['reaction_type'], 'combustión')
    
    def test_determine_reaction_type_synthesis(self):
        """Test determinación de tipo de reacción - síntesis"""
        reaction_type = self.balancer.determine_reaction_type(['H2', 'O2'], ['H2O'])
        self.assertEqual(reaction_type, 'síntesis')
    
    def test_determine_reaction_type_decomposition(self):
        """Test determinación de tipo de reacción - descomposición"""
        reaction_type = self.balancer.determine_reaction_type(['H2O2'], ['H2O', 'O2'])
        self.assertEqual(reaction_type, 'descomposición')
    
    def test_determine_reaction_type_combustion(self):
        """Test determinación de tipo de reacción - combustión"""
        reaction_type = self.balancer.determine_reaction_type(['CH4', 'O2'], ['CO2', 'H2O'])
        self.assertEqual(reaction_type, 'combustión')

class BalanceEquationAPITests(TestCase):
    """
    Tests para el endpoint de balanceo de ecuaciones
    """
    
    def setUp(self):
        self.client = APIClient()
        self.balance_url = reverse('reactions:balance_equation')
        self.health_url = reverse('reactions:health_check')
        self.history_url = reverse('reactions:get_balanced_reactions')
    
    def test_health_check(self):
        """Test del endpoint de health check"""
        response = self.client.get(self.health_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['version'], 'Alpha 2.2.0')
    
    def test_balance_equation_synthesis_success(self):
        """Test exitoso de balanceo - reacción de síntesis"""
        data = {'equation': 'H2 + O2 -> H2O'}
        response = self.client.post(self.balance_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['balanced_equation'], '2H2 + O2 -> 2H2O')
        self.assertEqual(response.data['reaction_type'], 'síntesis')
        self.assertIn('coefficients', response.data)
    
    def test_balance_equation_decomposition_success(self):
        """Test exitoso de balanceo - reacción de descomposición"""
        data = {'equation': 'H2O2 -> H2O + O2'}
        response = self.client.post(self.balance_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['balanced_equation'], '2H2O2 -> 2H2O + O2')
        self.assertEqual(response.data['reaction_type'], 'descomposición')
    
    def test_balance_equation_combustion_success(self):
        """Test exitoso de balanceo - reacción de combustión"""
        data = {'equation': 'CH4 + O2 -> CO2 + H2O'}
        response = self.client.post(self.balance_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['balanced_equation'], 'CH4 + 2O2 -> CO2 + 2H2O')
        self.assertEqual(response.data['reaction_type'], 'combustión')
    
    def test_balance_equation_invalid_format(self):
        """Test con formato de ecuación inválido"""
        data = {'equation': 'H2 + O2'}  # Sin ->
        response = self.client.post(self.balance_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('equation', response.data)
    
    def test_balance_equation_empty_equation(self):
        """Test con ecuación vacía"""
        data = {'equation': ''}
        response = self.client.post(self.balance_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_balance_equation_missing_reactants(self):
        """Test con reactivos faltantes"""
        data = {'equation': ' -> H2O'}
        response = self.client.post(self.balance_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_balance_equation_missing_products(self):
        """Test con productos faltantes"""
        data = {'equation': 'H2 + O2 -> '}
        response = self.client.post(self.balance_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_database_storage(self):
        """Test que las reacciones se guarden en la base de datos"""
        initial_count = BalancedReaction.objects.count()
        
        data = {'equation': 'H2 + O2 -> H2O'}
        response = self.client.post(self.balance_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BalancedReaction.objects.count(), initial_count + 1)
        
        # Verificar que se guardó correctamente
        reaction = BalancedReaction.objects.latest('created_at')
        self.assertEqual(reaction.original_equation, 'H2 + O2 -> H2O')
        self.assertEqual(reaction.balanced_equation, '2H2 + O2 -> 2H2O')
        self.assertEqual(reaction.reaction_type, 'síntesis')
    
    def test_get_balanced_reactions_history(self):
        """Test del endpoint para obtener historial"""
        # Crear algunas reacciones
        BalancedReaction.objects.create(
            original_equation='H2 + O2 -> H2O',
            balanced_equation='2H2 + O2 -> 2H2O',
            coefficients={'test': 'data'},
            reaction_type='síntesis'
        )
        
        response = self.client.get(self.history_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)