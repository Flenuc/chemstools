from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import BalanceEquationSerializer, BalancedReactionSerializer
from .models import BalancedReaction
from .utils import ChemicalEquationBalancer

@api_view(['POST'])
def balance_equation(request):
    """
    Endpoint para balancear ecuaciones químicas
    
    POST /api/reactions/balance-equation/
    Body: {"equation": "H2 + O2 -> H2O"}
    """
    serializer = BalanceEquationSerializer(data=request.data)
    
    if serializer.is_valid():
        equation = serializer.validated_data['equation']
        
        # Balancear la ecuación usando SymPy
        result = ChemicalEquationBalancer.balance_equation(equation)
        
        if result['success']:
            # Guardar en la base de datos (opcional)
            try:
                balanced_reaction = BalancedReaction.objects.create(
                    original_equation=result['original_equation'],
                    balanced_equation=result['balanced_equation'],
                    coefficients=result['coefficients'],
                    reaction_type=result['reaction_type']
                )
                result['id'] = balanced_reaction.id
            except Exception as e:
                # Si falla el guardado, continuar con la respuesta
                result['db_save_error'] = str(e)
            
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_balanced_reactions(request):
    """
    Endpoint para obtener el historial de reacciones balanceadas
    
    GET /api/reactions/balanced-reactions/
    """
    reactions = BalancedReaction.objects.all()[:50]  # Últimas 50
    serializer = BalancedReactionSerializer(reactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def health_check(request):
    """
    Endpoint para verificar que la API funciona correctamente
    
    GET /api/reactions/health/
    """
    return Response({
        'status': 'ok',
        'message': 'Reactions API is working correctly',
        'version': 'Alpha 2.2.0'
    }, status=status.HTTP_200_OK)