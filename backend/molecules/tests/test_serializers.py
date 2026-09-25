from django.test import TestCase
from rest_framework.exceptions import ValidationError
from molecules.serializers import MoleculeSerializer

class MoleculeSerializerTest(TestCase):
    def test_valid_smiles(self):
        data = {'name': 'Water', 'structure_data': 'O', 'format': 'SMILES'}
        serializer = MoleculeSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_invalid_smiles(self):
        data = {'name': 'Invalid', 'structure_data': 'InvalidSMILES', 'format': 'SMILES'}
        serializer = MoleculeSerializer(data=data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn('La cadena SMILES proporcionada no es válida', str(context.exception))