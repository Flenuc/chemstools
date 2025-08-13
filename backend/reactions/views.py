from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import BalanceEquationSerializer, BalancedReactionSerializer
from .models import BalancedReaction
from .utils import ChemicalEquationBalancer

@api_view(['POST'])
def balance_equation(request):
    """
    Balancear ecuaciones químicas automáticamente.
    
    Este endpoint procesa una ecuación química no balanceada y devuelve la ecuación
    balanceada con los coeficientes estequiométricos correctos. Utiliza SymPy para
    resolver el sistema de ecuaciones lineales y determinar los coeficientes mínimos.
    
    **Método:** POST
    **URL:** /api/reactions/balance-equation/
    
    **Parámetros del body (JSON):**
    - equation (str, requerido): Ecuación química no balanceada
      Formato: "reactivo1 + reactivo2 -> producto1 + producto2"
      Ejemplo: "H2 + O2 -> H2O", "Fe + O2 -> Fe2O3"
    
    **Respuesta exitosa (200):**
    ```json
    {
        "success": true,
        "original_equation": "H2 + O2 -> H2O",
        "balanced_equation": "2H2 + O2 -> 2H2O",
        "coefficients": {
            "reactants": {"H2": 2, "O2": 1},
            "products": {"H2O": 2}
        },
        "reaction_type": "synthesis",
        "id": 1
    }
    ```
    
    **Tipos de reacción detectados:**
    - synthesis: Síntesis o combinación
    - decomposition: Descomposición
    - combustion: Combustión
    - substitution: Sustitución o desplazamiento
    - unknown: No clasificada
    
    **Errores posibles:**
    - 400: Ecuación inválida o no balanceable
    - 400: Formato de ecuación incorrecto (falta '->' o compuestos inválidos)
    
    **Notas:**
    - Soporta compuestos con paréntesis: Ca(OH)2, Al2(SO4)3
    - Las ecuaciones balanceadas se guardan en la base de datos para historial
    - Los coeficientes se normalizan al mínimo común divisor
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
    Obtener historial de reacciones químicas balanceadas.
    
    Devuelve las últimas 50 ecuaciones químicas que han sido balanceadas
    y almacenadas en el sistema, ordenadas por fecha de creación descendente.
    
    **Método:** GET
    **URL:** /api/reactions/balanced-reactions/
    
    **Respuesta exitosa (200):**
    ```json
    [
        {
            "id": 1,
            "original_equation": "H2 + O2 -> H2O",
            "balanced_equation": "2H2 + O2 -> 2H2O",
            "coefficients": {
                "reactants": {"H2": 2, "O2": 1},
                "products": {"H2O": 2}
            },
            "reaction_type": "synthesis",
            "created_at": "2025-08-11T20:00:00Z"
        },
        {
            "id": 2,
            "original_equation": "CH4 + O2 -> CO2 + H2O",
            "balanced_equation": "CH4 + 2O2 -> CO2 + 2H2O",
            "coefficients": {
                "reactants": {"CH4": 1, "O2": 2},
                "products": {"CO2": 1, "H2O": 2}
            },
            "reaction_type": "combustion",
            "created_at": "2025-08-11T19:55:00Z"
        }
    ]
    ```
    
    **Notas:**
    - Máximo 50 reacciones por petición
    - No requiere autenticación
    - Útil para mostrar ejemplos y referencias
    """
    reactions = BalancedReaction.objects.all()[:50]  # Últimas 50
    serializer = BalancedReactionSerializer(reactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def health_check(request):
    """
    Verificar el estado de salud de la API de reacciones.
    
    Endpoint simple para verificar que el servicio de reacciones químicas
    está funcionando correctamente. Útil para monitoreo y debugging.
    
    **Método:** GET
    **URL:** /api/reactions/health/
    
    **Respuesta exitosa (200):**
    ```json
    {
        "status": "ok",
        "message": "Reactions API is working correctly",
        "version": "Alpha 2.3.0"
    }
    ```
    
    **Notas:**
    - No requiere autenticación
    - Respuesta rápida para verificación de disponibilidad
    """
    return Response({
        'status': 'ok',
        'message': 'Reactions API is working correctly',
        'version': 'Alpha 2.3.0'
    }, status=status.HTTP_200_OK)
