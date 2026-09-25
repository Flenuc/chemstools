from rest_framework import serializers
from .models import Molecule
from rdkit import Chem

class MoleculeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Molecule
        fields = ['id', 'name', 'structure_data', 'format', 'owner', 'created_at', 'updated_at']
        read_only_fields = ['owner']

    def validate_structure_data(self, value):
        """
        Verifica si la estructura SMILES proporcionada es válida usando RDKit.
        """
        if self.initial_data.get('format', 'SMILES').upper() == 'SMILES':
            mol = Chem.MolFromSmiles(value)
            if mol is None:
                raise serializers.ValidationError("La cadena SMILES proporcionada no es válida.")
        return value
