"""
Suite de pruebas para funcionalidad avanzada de pH.
"""

import json
import tempfile
import os
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.db.models import Min

from ..models import PHCalculationHistory
from ..validators import validate_ph_input, validate_buffer_input, generate_warnings
from ..utils import (
    calculate_ionic_strength,
    calculate_activity_coefficient,
    calculate_buffer_capacity,
    correct_kw_for_temperature,
    comprehensive_ph_calculation
)
from ..export_utils import export_to_csv, export_to_pdf, export_to_json
from ..serializers import AdvancedPHCalculatorSerializer

User = get_user_model()


class TestAdvancedPHValidation(TestCase):
    """Pruebas para validación con cerberus."""
    
    def test_valid_ph_input(self):
        """Prueba validación de entrada válida de pH."""
        data = {
            'calculation_type': 'ph_to_all',
            'input_value': 7.0,
            'input_type': 'ph',
            'temperature': 25.0,
            'ionic_strength': 0.1,
            'include_activity': True,
            'show_steps': True
        }
        
        is_valid, normalized_data, warnings = validate_ph_input(data)
        
        self.assertTrue(is_valid)
        self.assertEqual(normalized_data['input_value'], 7.0)
        self.assertIsInstance(warnings, list)
    
    def test_invalid_ph_range(self):
        """Prueba validación de pH fuera de rango."""
        data = {
            'calculation_type': 'ph_to_all',
            'input_value': 15.0,  # pH inválido
            'input_type': 'ph',
            'temperature': 25.0
        }
        
        is_valid, _, _ = validate_ph_input(data)
        self.assertFalse(is_valid)
    
    def test_negative_concentration(self):
        """Prueba validación de concentración negativa."""
        data = {
            'calculation_type': 'concentration_to_ph',
            'input_value': -0.001,  # Concentración negativa
            'input_type': 'h_concentration',
            'temperature': 25.0
        }
        
        is_valid, _, _ = validate_ph_input(data)
        self.assertFalse(is_valid)
    
    def test_extreme_temperature(self):
        """Prueba validación de temperatura extrema."""
        data = {
            'calculation_type': 'ph_to_all',
            'input_value': 7.0,
            'input_type': 'ph',
            'temperature': 150.0  # Temperatura fuera de rango
        }
        
        is_valid, _, _ = validate_ph_input(data)
        self.assertFalse(is_valid)
    
    def test_buffer_validation(self):
        """Prueba validación de sistemas buffer."""
        data = {
            'buffer_components': [
                {'compound': 'CH3COOH', 'concentration': 0.1, 'pka': 4.76},
                {'compound': 'CH3COONa', 'concentration': 0.1}
            ],
            'temperature': 25.0
        }
        
        is_valid, normalized_data, warnings = validate_buffer_input(data)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(normalized_data['buffer_components']), 2)
        self.assertIsInstance(warnings, list)
    
    def test_warning_generation(self):
        """Prueba generación de warnings."""
        # pH extremo
        data = {'input_value': 0.5, 'input_type': 'ph'}
        warnings = generate_warnings(data)
        self.assertTrue(any('muy ácido' in w.lower() for w in warnings))
        
        # Fuerza iónica alta
        data = {'ionic_strength': 2.0}
        warnings = generate_warnings(data)
        self.assertTrue(any('fuerza iónica alta' in w.lower() for w in warnings))



class TestChemistryUtils(TestCase):
    """Pruebas para funciones químicas."""
    
    def test_ionic_strength_calculation(self):
        """Prueba cálculo de fuerza iónica."""
        concentrations = [0.1, 0.1, 0.05]  # NaCl + CaCl2
        charges = [1, -1, 2]  # Na+, Cl-, Ca2+
        
        ionic_strength = calculate_ionic_strength(concentrations, charges)
        expected = 0.5 * (0.1*1**2 + 0.1*(-1)**2 + 0.05*2**2)
        
        self.assertAlmostEqual(ionic_strength, expected, places=4)
    
    def test_activity_coefficient(self):
        """Prueba cálculo de coeficientes de actividad."""
        # Fuerza iónica baja
        gamma = calculate_activity_coefficient(0.01, 1, 25.0, 'H+')
        self.assertLess(gamma, 1.0)  # Coeficiente debe ser < 1
        self.assertGreater(gamma, 0.5)  # Pero no demasiado bajo
        
        # Fuerza iónica cero
        gamma_zero = calculate_activity_coefficient(0.0, 1, 25.0)
        self.assertEqual(gamma_zero, 1.0)
        
        # Ion divalente
        gamma_ca = calculate_activity_coefficient(0.1, 2, 25.0, 'Ca+2')
        gamma_na = calculate_activity_coefficient(0.1, 1, 25.0, 'Na+')
        self.assertLess(gamma_ca, gamma_na)  # Divalente más afectado
    
    def test_buffer_capacity(self):
        """Prueba cálculo de capacidad buffer."""
        buffer_components = [
            {'pka': 4.76, 'concentration': 0.1}  # Acetato
        ]
        
        # En el pKa, la capacidad debe ser máxima
        capacity_at_pka = calculate_buffer_capacity(4.76, buffer_components)
        capacity_away_from_pka = calculate_buffer_capacity(7.0, buffer_components)
        
        self.assertGreater(capacity_at_pka, capacity_away_from_pka)
        self.assertGreater(capacity_at_pka, 0)
    
    def test_kw_temperature_correction(self):
        """Prueba corrección de Kw por temperatura."""
        kw_25 = correct_kw_for_temperature(25.0)
        kw_0 = correct_kw_for_temperature(0.0)
        kw_100 = correct_kw_for_temperature(100.0)
        
        self.assertAlmostEqual(kw_25, 1.008e-14, places=16)
        self.assertLess(kw_0, kw_25)  # Kw menor a temperatura baja
        self.assertGreater(kw_100, kw_25)  # Kw mayor a temperatura alta
        
        # Prueba interpolación
        kw_50 = correct_kw_for_temperature(50.0)
        self.assertGreater(kw_50, kw_25)
        self.assertLess(kw_50, kw_100)
    
    def test_comprehensive_calculation(self):
        """Prueba cálculo comprehensivo."""
        input_data = {
            'calculation_type': 'ph_to_all',
            'input_value': 7.0,
            'input_type': 'ph',
            'temperature': 25.0,
            'ionic_strength': 0.1,
            'include_activity': True
        }
        
        results = comprehensive_ph_calculation(input_data)
        
        # Verificar campos requeridos
        required_fields = ['ph', 'poh', 'h_concentration', 'oh_concentration']
        for field in required_fields:
            self.assertIn(field, results)
        
        # Verificar relaciones químicas
        self.assertAlmostEqual(results['ph'] + results['poh'], 14.0, places=1)
        self.assertAlmostEqual(
            results['h_concentration'] * results['oh_concentration'],
            results['corrected_kw'],
            places=15
        )


class TestAdvancedPHCalculator(APITestCase):
    """Pruebas para la view principal de cálculo avanzado."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('advanced-ph-calculator')
    
    def test_simple_ph_calculation(self):
        """Prueba cálculo simple de pH."""
        data = {
            'calculation_type': 'ph_to_all',
            'input_value': 3.0,
            'input_type': 'ph',
            'temperature': 25.0,
            'show_steps': True
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        results = response.data['results']
        self.assertAlmostEqual(results['ph'], 3.0, places=2)
        self.assertAlmostEqual(results['poh'], 11.0, places=1)
        self.assertAlmostEqual(results['h_concentration'], 1e-3, places=5)
        
        # Verificar que se guardó en historial
        self.assertTrue(
            PHCalculationHistory.objects.filter(user=self.user).exists()
        )
    
    def test_activity_correction(self):
        """Prueba corrección por actividad."""
        data = {
            'calculation_type': 'activity_correction',
            'input_value': 7.0,
            'input_type': 'ph',
            'ionic_strength': 0.5,
            'include_activity': True,
            'temperature': 25.0
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)