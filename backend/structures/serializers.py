from rest_framework import serializers
from .models import MolecularStructure


class LewisStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = MolecularStructure
        fields = ['id', 'formula', 'mol_data', 'lewis_data', 'created_at']
        read_only_fields = ['id', 'created_at']


class FormulaInputSerializer(serializers.Serializer):
    formula = serializers.CharField(
        max_length=100,
        help_text="Molecular formula (e.g., H2O, CH4, NH3)"
    )
    
    def validate_formula(self, value):
        """Basic validation for molecular formula format"""
        import re
        if not re.match(r'^[A-Z][a-z]?(\d*[A-Z][a-z]?\d*)*$', value):
            raise serializers.ValidationError(
                "Invalid molecular formula format. Use format like H2O, CH4, etc."
            )
        return value