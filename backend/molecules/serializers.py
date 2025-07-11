from rest_framework import serializers
from .models import Molecule

class MoleculeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Molecule
        fields = ['id', 'name', 'structure_data', 'format', 'owner', 'created_at', 'updated_at']
        read_only_fields = ['owner']
