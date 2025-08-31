"""
Suite de pruebas para el sistema de análisis de sistemas químicos.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import uuid

from systems_analysis.models import (
    ChemicalSubstance, SystemAnalysis, SystemComponent, SeparationMethod
)
from systems_analysis.engines import SystemAnalyzer, ComponentData
from systems_analysis.separation_algorithms import (
    TamizacionAlgorithm, MagneticSeparationAlgorithm, evaluate_all_methods
)

User = get_user_model()


class TestSystemAnalyzer(TestCase):
    """Pruebas para el motor de análisis."""
    
    def setUp(self):
        self.analyzer = SystemAnalyzer()
    
    def test_analyze_simple_mixture(self):
        """Prueba análisis de mezcla simple."""
        components = [
            ComponentData('arena', 0.7, 2000, 'solid'),  # Changed from 500nm to 2000nm (>1μm)
            ComponentData('agua', 0.3, None, 'liquid')
        ]
        
        result = self.analyzer.analyze_mixture(components)
        
        self.assertEqual(result.system_type, 'heterogeneous')
        self.assertEqual(len(result.phases), 2)
        self.assertGreater(result.overall_separability, 0.5)
    
    def test_detect_phases(self):
        """Prueba detección de fases."""
        components = [
            ComponentData('hierro', 0.3, 100, 'solid'),
            ComponentData('arena', 0.4, 500, 'solid'),
            ComponentData('agua', 0.3, None, 'liquid')
        ]
        
        phases = self.analyzer.detect_phases(components)
        
        self.assertEqual(len(phases), 2)  # Sólido y líquido
        solid_phase = next(p for p in phases if p.phase_type == 'solid')
        self.assertEqual(len(solid_phase.components), 2)
        self.assertAlmostEqual(solid_phase.total_fraction, 0.7, places=2)
    
    def test_classify_homogeneity(self):
        """Prueba clasificación de homogeneidad."""
        # Sistema homogéneo
        components = [ComponentData('agua', 1.0, None, 'liquid')]
        phases = self.analyzer.detect_phases(components)
        self.assertEqual(
            self.analyzer.classify_system_homogeneity(phases),
            'homogeneous'
        )
        
        # Sistema heterogéneo
        components = [
            ComponentData('arena', 0.5, 2000, 'solid'),  # Changed from 500nm to 2000nm (>1μm)
            ComponentData('agua', 0.5, None, 'liquid')
        ]
        phases = self.analyzer.detect_phases(components)
        self.assertEqual(
            self.analyzer.classify_system_homogeneity(phases),
            'heterogeneous'
        )
    
    def test_suggest_separation_methods(self):
        """Prueba sugerencia de métodos."""
        properties = {
            'magnetic_components': ['hierro'],
            'size_range': {'min': 10, 'max': 1000},
            'phases_present': {'solid', 'liquid'},
            'soluble_components': ['sal']
        }
        phases = []
        
        suggestions = self.analyzer.suggest_separation_methods(properties, phases)
        
        self.assertGreater(len(suggestions), 0)
        # Debe sugerir separación magnética
        magnetic_method = next(
            (s for s in suggestions if s.method == 'magnetic_separation'),
            None
        )
        self.assertIsNotNone(magnetic_method)
        self.assertGreater(magnetic_method.efficiency, 0.9)


class TestSeparationAlgorithms(TestCase):
    """Pruebas para algoritmos de separación."""
    
    def test_tamizacion_algorithm(self):
        """Prueba algoritmo de tamización."""
        algo = TamizacionAlgorithm()
        
        components = [
            {'particle_size': 100},
            {'particle_size': 2000}
        ]
        
        self.assertTrue(algo.is_applicable(components, {}))
        efficiency = algo.calculate_efficiency(components, {})
        self.assertGreater(efficiency, 0.9)
        
        time = algo.estimate_time(1000, {})  # 1 kg
        self.assertEqual(time, 0.5)
    
    def test_magnetic_separation_algorithm(self):
        """Prueba algoritmo de separación magnética."""
        algo = MagneticSeparationAlgorithm()
        
        components = [
            {'magnetic_susceptibility': 0.1},  # Ferromagnético
            {'magnetic_susceptibility': 0}
        ]
        
        self.assertTrue(algo.is_applicable(components, {}))
        efficiency = algo.calculate_efficiency(components, {})
        self.assertGreater(efficiency, 0.95)
    
    def test_evaluate_all_methods(self):
        """Prueba evaluación de todos los métodos."""
        components = [
            {
                'particle_size': 100,
                'density': 7.8,
                'magnetic_susceptibility': 0.1,
                'phase': 'solid',
                'mass': 500
            },
            {
                'particle_size': 2000,
                'density': 2.5,
                'magnetic_susceptibility': 0,
                'phase': 'solid',
                'mass': 500
            }
        ]
        
        results = evaluate_all_methods(components)
        
        self.assertGreater(len(results), 0)
        # Debe incluir tamización y separación magnética
        method_names = [r['method'] for r in results]
        self.assertIn('tamizacion', method_names)
        self.assertIn('magnetic_separation', method_names)


class TestSystemAnalysisAPI(TestCase):
    """Pruebas para los endpoints de la API."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Crear sustancias de prueba
        self.iron = ChemicalSubstance.objects.create(
            name='Hierro',
            formula='Fe',
            molecular_weight=55.845,
            density=7.874,
            magnetic_susceptibility=0.22,
            phase_at_stp='solid',
            chemical_category='metal'
        )
        
        self.sand = ChemicalSubstance.objects.create(
            name='Arena',
            formula='SiO2',
            molecular_weight=60.08,
            density=2.65,
            phase_at_stp='solid',
            chemical_category='mineral',
            particle_size_range={'min': 100, 'max': 2000}
        )
        
        self.water = ChemicalSubstance.objects.create(
            name='Agua',
            formula='H2O',
            molecular_weight=18.015,
            density=1.0,
            phase_at_stp='liquid',
            chemical_category='inorganic'
        )
    
    def test_analyze_system_endpoint(self):
        """Prueba el endpoint de análisis de sistema."""
        data = {
            'name': 'Mezcla de prueba',
            'components': [
                {
                    'substance_id': str(self.iron.id),
                    'mass_fraction': 0.3,
                    'particle_size': 100
                },
                {
                    'substance_id': str(self.sand.id),
                    'mass_fraction': 0.5,
                    'particle_size': 500
                },
                {
                    'substance_id': str(self.water.id),
                    'mass_fraction': 0.2
                }
            ],
            'total_mass': 1000,
            'analysis_conditions': {
                'temperature': 25,
                'pressure': 1
            }
        }
        
        response = self.client.post('/api/systems/analyze/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('analysis_id', response.data)
        self.assertIn('results', response.data)
        
        results = response.data['results']
        self.assertIn('system_type', results)
        self.assertIn('recommended_methods', results)
        self.assertGreater(len(results['recommended_methods']), 0)
    
    def test_separation_methods_endpoint(self):
        """Prueba el endpoint de métodos de separación."""
        # Crear método de prueba
        SeparationMethod.objects.create(
            name='Tamización',
            method_type='mechanical',
            description='Test',
            principle='Test',
            complexity_level='basic',
            cost_factor=1
        )
        
        response = self.client.get('/api/systems/separation-methods/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertGreater(len(response.data['methods']), 0)
    
    def test_generate_separation_flow(self):
        """Prueba generación de diagrama de flujo."""
        # Primero crear un análisis
        analysis = SystemAnalysis.objects.create(
            user=self.user,
            name='Test Analysis',
            total_mass=1000,
            system_type='heterogeneous',
            analysis_data={
                'recommended_methods': [
                    {
                        'method': 'magnetic_separation',
                        'target': ['hierro'],
                        'efficiency': 0.98,
                        'difficulty': 'basic'
                    },
                    {
                        'method': 'filtration',
                        'target': ['arena'],
                        'efficiency': 0.99,
                        'difficulty': 'basic'
                    }
                ]
            }
        )
        
        data = {
            'analysis_id': str(analysis.id),
            'selected_methods': ['magnetic_separation', 'filtration']
        }
        
        response = self.client.post(
            '/api/systems/generate-separation-flow/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('process_id', response.data)
        self.assertIn('separation_flow', response.data)
        
        flow = response.data['separation_flow']
        self.assertIn('steps', flow)
        self.assertGreater(len(flow['steps']), 0)
        self.assertIn('overall_efficiency', flow)
    
    def test_substance_properties_endpoint(self):
        """Prueba obtención de propiedades de sustancia."""
        response = self.client.get(
            f'/api/systems/substance-properties/{self.iron.id}/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['substance']['name'], 'Hierro')
        self.assertIn('separation_properties', response.data['substance'])
    
    def test_substance_search_endpoint(self):
        """Prueba búsqueda de sustancias."""
        response = self.client.get(
            '/api/systems/substances/search/',
            {'phase': 'solid', 'magnetic': True}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertGreater(response.data['count'], 0)
        
        # Debe encontrar el hierro
        substances = response.data['substances']
        iron_found = any(s['name'] == 'Hierro' for s in substances)
        self.assertTrue(iron_found)
    
    def test_analysis_history(self):
        """Prueba historial de análisis."""
        # Clear any existing analyses for this user to ensure test isolation
        SystemAnalysis.objects.filter(user=self.user).delete()
        
        # Crear algunos análisis
        for i in range(3):
            SystemAnalysis.objects.create(
                user=self.user,
                name=f'Analysis {i}',
                total_mass=1000,
                system_type='heterogeneous' if i % 2 == 0 else 'homogeneous'
            )
        
        response = self.client.get('/api/systems/analysis-history/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # The response is paginated, check the results key
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 3)
        self.assertEqual(response.data['count'], 3)
    
    def test_analysis_stats(self):
        """Prueba estadísticas de análisis."""
        # Crear análisis con datos
        for i in range(2):
            SystemAnalysis.objects.create(
                user=self.user,
                name=f'Analysis {i}',
                total_mass=1000,
                system_type='heterogeneous',
                analysis_data={
                    'complexity_level': 'basic',
                    'overall_separability': 0.8
                }
            )
        
        response = self.client.get('/api/systems/analysis-history/stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_analyses'], 2)
        self.assertAlmostEqual(response.data['average_separability'], 0.8, places=2)