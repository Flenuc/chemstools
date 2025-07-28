from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import GlossaryTerm
from .serializers import GlossaryTermSerializer
import math

class GlossaryTermViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint para acceder al glosario de términos químicos.
    
    - **GET**: Devuelve una lista de todos los términos y sus definiciones.
    
    La respuesta de este endpoint está cacheada por 24 horas para un rendimiento óptimo.
    """
    queryset = GlossaryTerm.objects.all()
    serializer_class = GlossaryTermSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    @method_decorator(cache_page(60 * 60 * 24))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class pHCalculatorView(APIView):
    """
    Realiza cálculos de pH, pOH, [H+] y [OH-].
    
    - **POST**: Acepta un JSON con una de las cuatro claves (`ph`, `poh`, `h_concentration`, `oh_concentration`) 
      y devuelve un objeto con los cuatro valores calculados.
      
      Ejemplo de entrada: `{"ph": 7}`
      Ejemplo de salida: `{"ph": 7.0, "poh": 7.0, "h_concentration": "1.00e-07", "oh_concentration": "1.00e-07"}`
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # ... (la lógica existente es suficientemente clara y no requiere refactorización)
        data = request.data
        h_concentration = None
        poh = None

        try:
            if 'ph' in data:
                value = float(data['ph'])
                h_concentration = 10**(-value)
                oh_concentration = 1e-14 / h_concentration
                poh = -math.log10(oh_concentration)
            elif 'poh' in data:
                value = float(data['poh'])
                poh = value
                oh_concentration = 10**(-value)
                h_concentration = 1e-14 / oh_concentration
            elif 'h_concentration' in data:
                value = float(data['h_concentration'])
                h_concentration = value
                oh_concentration = 1e-14 / h_concentration
                poh = -math.log10(oh_concentration)
            elif 'oh_concentration' in data:
                value = float(data['oh_concentration'])
                oh_concentration = value
                h_concentration = 1e-14 / oh_concentration
                poh = -math.log10(oh_concentration)
            else:
                return Response({"error": "No se proporcionó ningún valor de entrada."}, status=status.HTTP_400_BAD_REQUEST)

            if h_concentration is None or poh is None:
                 raise ValueError("Error de cálculo interno.")

            ph_val = -math.log10(h_concentration)

            return Response({
                "ph": ph_val,
                "poh": poh,
                "h_concentration": f"{h_concentration:.2e}",
                "oh_concentration": f"{1e-14 / h_concentration:.2e}"
            })
        except (ValueError, TypeError):
            return Response({"error": "Valor de entrada inválido. Por favor, proporcione un número válido."}, status=status.HTTP_400_BAD_REQUEST)


class SolutionCalculatorView(APIView):
    """
    Calcula el porcentaje masa/masa y masa/volumen de una disolución.

    - **POST**: Acepta un JSON con al menos dos de las siguientes claves:
        - `solute_mass` (g)
        - `solvent_mass` (g)
        - `solution_volume` (mL)
    - Opcionalmente, puede recibir `density` (g/mL) para derivar un porcentaje a partir del otro.

    Ejemplo de entrada: `{"solute_mass": 10, "solvent_mass": 90}`
    Ejemplo de salida: `{"percent_mass_mass": "10.00", "percent_mass_volume": "No calculable"}`
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # ... (la lógica existente es suficientemente clara y no requiere refactorización)
        data = request.data
        try:
            solute_mass = data.get('solute_mass')
            solvent_mass = data.get('solvent_mass')
            solution_volume = data.get('solution_volume')
            density = data.get('density')

            solute_mass = float(solute_mass) if solute_mass is not None else None
            solvent_mass = float(solvent_mass) if solvent_mass is not None else None
            solution_volume = float(solution_volume) if solution_volume is not None else None
            density = float(density) if density is not None else None

            if solute_mass is not None and solute_mass < 0: raise ValueError("La masa del soluto no puede ser negativa.")
            if solvent_mass is not None and solvent_mass < 0: raise ValueError("La masa del disolvente no puede ser negativa.")
            if solution_volume is not None and solution_volume <= 0: raise ValueError("El volumen de la disolución debe ser positivo.")
            if density is not None and density <= 0: raise ValueError("La densidad debe ser positiva.")

            solution_mass = None
            if solute_mass is not None and solvent_mass is not None:
                solution_mass = solute_mass + solvent_mass

            percent_mass_mass = None
            if solute_mass is not None and solution_mass is not None:
                if solution_mass == 0: raise ValueError("La masa de la disolución no puede ser cero.")
                percent_mass_mass = (solute_mass / solution_mass) * 100
            
            percent_mass_volume = None
            if solute_mass is not None and solution_volume is not None:
                percent_mass_volume = (solute_mass / solution_volume) * 100

            if percent_mass_mass is None and percent_mass_volume is not None and density is not None:
                 percent_mass_mass = (percent_mass_volume / density)

            if percent_mass_volume is None and percent_mass_mass is not None and density is not None:
                percent_mass_volume = (percent_mass_mass * density)

            if percent_mass_mass is None and percent_mass_volume is None:
                return Response({"error": "Datos insuficientes para el cálculo."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "percent_mass_mass": f"{percent_mass_mass:.2f}" if percent_mass_mass is not None else "No calculable",
                "percent_mass_volume": f"{percent_mass_volume:.2f}" if percent_mass_volume is not None else "No calculable",
            })
        except (ValueError, TypeError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)