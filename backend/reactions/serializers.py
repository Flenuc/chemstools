from rest_framework import serializers
from .models import BalancedReaction

class BalanceEquationSerializer(serializers.Serializer):
    """
    Serializador para balancear ecuaciones químicas
    """
    equation = serializers.CharField(
        max_length=500,
        help_text="Ecuación química no balanceada (ej: H2 + O2 -> H2O)"
    )
    
    def validate_equation(self, value):
        """
        Validar que la ecuación tenga el formato correcto
        """
        if '->' not in value:
            raise serializers.ValidationError(
                "La ecuación debe contener '->' para separar reactivos y productos"
            )
        
        parts = value.split('->')
        if len(parts) != 2:
            raise serializers.ValidationError(
                "La ecuación debe tener exactamente un '->' separando reactivos y productos"
            )
        
        reactants, products = parts
        if not reactants.strip() or not products.strip():
            raise serializers.ValidationError(
                "Tanto reactivos como productos deben estar presentes"
            )
        
        return value.strip()

class BalancedReactionSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo BalancedReaction
    """
    class Meta:
        model = BalancedReaction
        fields = '__all__'
        read_only_fields = ('created_at',)