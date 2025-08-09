import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from ..models import MolecularStructure
from ..utils import LewisStructureGenerator


class TestLewisStructureGenerator(TestCase):
    """Test the Lewis structure generation utility"""
    
    def test_parse_formula_simple(self):
        """Test parsing simple molecular formulas"""
        result = LewisStructureGenerator.parse_formula("H2O")
        expected = {'H': 2, 'O': 1}
        self.assertEqual(result, expected)
    
    def test_parse_formula_complex(self):
        """Test parsing complex molecular formulas"""
        result = LewisStructureGenerator.parse_formula("C2H6")
        expected = {'C': 2, 'H': 6}
        self.assertEqual(result, expected)
    
    def test_get_valence_electrons_water(self):
        """Test valence electron calculation for water"""
        atom_counts = {'H': 2, 'O': 1}
        result = LewisStructureGenerator.get_valence_electrons(atom_counts)
        expected = 8  # 2*1 + 1*6 = 8
        self.assertEqual(result, expected)
    
    def test_get_valence_electrons_methane(self):
        """Test valence electron calculation for methane"""
        atom_counts = {'C': 1, 'H': 4}
        result = LewisStructureGenerator.get_valence_electrons(atom_counts)
        expected = 8  # 1*4 + 4*1 = 8
        self.assertEqual(result, expected)
    
    def test_generate_lewis_structure_water(self):
        """Test generating Lewis structure for water"""
        try:
            result = LewisStructureGenerator.generate_lewis_structure("H2O")
            
            self.assertTrue(result['success'], f"Error: {result.get('error', 'Unknown')}")
            self.assertIsNotNone(result['mol_data'])
            self.assertIsNotNone(result['lewis_data'])
            
            lewis_data = result['lewis_data']
            self.assertEqual(lewis_data['formula'], "H2O")
            self.assertEqual(lewis_data['total_valence_electrons'], 8)
            self.assertEqual(lewis_data['atom_counts'], {'H': 2, 'O': 1})
        except Exception as e:
            self.fail(f"Failed to generate Lewis structure for water: {e}")
    
    def test_generate_lewis_structure_methane(self):
        """Test generating Lewis structure for methane"""
        try:
            result = LewisStructureGenerator.generate_lewis_structure("CH4")
            
            self.assertTrue(result['success'], f"Error: {result.get('error', 'Unknown')}")
            self.assertIsNotNone(result['mol_data'])
            self.assertIsNotNone(result['lewis_data'])
            
            lewis_data = result['lewis_data']
            self.assertEqual(lewis_data['formula'], "CH4")
            self.assertEqual(lewis_data['total_valence_electrons'], 8)
        except Exception as e:
            self.fail(f"Failed to generate Lewis structure for methane: {e}")
    
    def test_generate_lewis_structure_ammonia(self):
        """Test generating Lewis structure for ammonia"""
        try:
            result = LewisStructureGenerator.generate_lewis_structure("NH3")
            
            self.assertTrue(result['success'], f"Error: {result.get('error', 'Unknown')}")
            lewis_data = result['lewis_data']
            self.assertEqual(lewis_data['formula'], "NH3")
            self.assertEqual(lewis_data['total_valence_electrons'], 8)
        except Exception as e:
            self.fail(f"Failed to generate Lewis structure for ammonia: {e}")
    
    def test_generate_lewis_structure_invalid_formula(self):
        """Test error handling for invalid formulas"""
        result = LewisStructureGenerator.generate_lewis_structure("XYZ123")
        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error'])


class TestLewisStructureAPI(TestCase):
    """Test the Lewis structure API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.generate_url = reverse('structures:generate_lewis')
        self.list_url = reverse('structures:list_structures')
    
    def test_generate_lewis_structure_post_valid(self):
        """Test POST request with valid formula"""
        data = {'formula': 'H2O'}
        response = self.client.post(self.generate_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('formula', response.data)
        self.assertIn('mol_data', response.data)
        self.assertIn('lewis_data', response.data)
        self.assertEqual(response.data['formula'], 'H2O')
    
    def test_generate_lewis_structure_post_invalid(self):
        """Test POST request with invalid formula"""
        data = {'formula': 'InvalidFormula123'}
        response = self.client.post(self.generate_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_generate_lewis_structure_missing_formula(self):
        """Test POST request without formula"""
        data = {}
        response = self.client.post(self.generate_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_generate_lewis_structure_duplicate(self):
        """Test generating same structure twice (should return existing)"""
        data = {'formula': 'CH4'}
        
        # First request
        response1 = self.client.post(self.generate_url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second request should return existing
        response2 = self.client.post(self.generate_url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data['id'], response2.data['id'])
    
    def test_list_structures(self):
        """Test listing structures"""
        # Create some structures first
        MolecularStructure.objects.create(
            formula="H2O",
            mol_data="mock_mol_data",
            lewis_data={"formula": "H2O", "test": True}
        )
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
    
    def test_get_structure_by_id(self):
        """Test getting structure by ID"""
        structure = MolecularStructure.objects.create(
            formula="NH3",
            mol_data="mock_mol_data",
            lewis_data={"formula": "NH3", "test": True}
        )
        
        url = reverse('structures:get_structure', args=[structure.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['formula'], 'NH3')
    
    def test_get_structure_not_found(self):
        """Test getting non-existent structure"""
        url = reverse('structures:get_structure', args=[99999])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@pytest.mark.django_db
class TestMolecularStructureModel:
    """Test the MolecularStructure model"""
    
    def test_create_structure(self):
        """Test creating a molecular structure"""
        structure = MolecularStructure.objects.create(
            formula="CO2",
            mol_data="test_mol_data",
            lewis_data={"formula": "CO2", "atoms": 3}
        )
        
        assert structure.formula == "CO2"
        assert structure.mol_data == "test_mol_data"
        assert structure.lewis_data["formula"] == "CO2"
        assert str(structure) == "Lewis Structure: CO2"
    
    def test_unique_formula_constraint(self):
        """Test that formula must be unique"""
        MolecularStructure.objects.create(
            formula="H2O",
            mol_data="test1",
            lewis_data={"test": 1}
        )
        
        with pytest.raises(Exception):  # IntegrityError
            MolecularStructure.objects.create(
                formula="H2O",
                mol_data="test2",
                lewis_data={"test": 2}
            )


# Pytest configuration for running specific tests
def pytest_configure():
    """Configure pytest settings"""
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'rest_framework',
                'structures',
            ],
            SECRET_KEY='test-secret-key',
        )
        django.setup()