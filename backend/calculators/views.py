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
    Un ViewSet de solo lectura para ver los términos del glosario.
    El listado está cacheado por 24 horas para mejorar el rendimiento.
    """
    queryset = GlossaryTerm.objects.all().order_by('term')
    serializer_class = GlossaryTermSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    @method_decorator(cache_page(60 * 60 * 24)) # Cache por 24 horas
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class pHCalculatorView(APIView):
    """
    Calcula los valores de pH, pOH, [H+] y [OH-] a partir de un valor de entrada.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
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
                return Response({"error": "No input value provided."}, status=status.HTTP_400_BAD_REQUEST)

            if h_concentration is None or poh is None:
                 raise ValueError("Internal calculation error")

            ph_val = -math.log10(h_concentration)

            return Response({
                "ph": ph_val,
                "poh": poh,
                "h_concentration": f"{h_concentration:.2e}",
                "oh_concentration": f"{1e-14 / h_concentration:.2e}"
            })
        except (ValueError, TypeError):
            return Response({"error": "Invalid input value."}, status=status.HTTP_400_BAD_REQUEST)

class SolutionCalculatorView(APIView):
    """
    Calcula propiedades de una disolución como % m/m y % m/v.
    Requiere al menos dos de los siguientes valores:
    - solute_mass (masa del soluto)
    - solvent_mass (masa del disolvente)
    - solution_volume (volumen de la disolución)
    - density (densidad de la disolución, opcional pero necesaria para ciertos cálculos)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            solute_mass = data.get('solute_mass')
            solvent_mass = data.get('solvent_mass')
            solution_volume = data.get('solution_volume')
            density = data.get('density')

            # Convertir a float, manejando valores None
            solute_mass = float(solute_mass) if solute_mass is not None else None
            solvent_mass = float(solvent_mass) if solvent_mass is not None else None
            solution_volume = float(solution_volume) if solution_volume is not None else None
            density = float(density) if density is not None else None

            if solute_mass is not None and solute_mass < 0:
                raise ValueError("La masa del soluto no puede ser negativa.")
            if solvent_mass is not None and solvent_mass < 0:
                raise ValueError("La masa del disolvente no puede ser negativa.")
            if solution_volume is not None and solution_volume <= 0:
                raise ValueError("El volumen de la disolución debe ser positivo.")
            if density is not None and density <= 0:
                raise ValueError("La densidad debe ser positiva.")

            solution_mass = None
            if solute_mass is not None and solvent_mass is not None:
                solution_mass = solute_mass + solvent_mass

            # Calcular % m/m
            percent_mass_mass = None
            if solute_mass is not None and solution_mass is not None:
                if solution_mass == 0:
                    raise ValueError("La masa de la disolución no puede ser cero.")
                percent_mass_mass = (solute_mass / solution_mass) * 100
            
            # Calcular % m/v
            percent_mass_volume = None
            if solute_mass is not None and solution_volume is not None:
                percent_mass_volume = (solute_mass / solution_volume) * 100

            # Intentar derivar valores faltantes si es posible
            if percent_mass_mass is None and percent_mass_volume is not None and density is not None:
                 # Derivar %m/m a partir de %m/v y densidad
                 # %m/v = (masa soluto / vol dis) * 100 -> masa soluto = (%m/v * vol dis) / 100
                 # densidad = masa dis / vol dis -> masa dis = densidad * vol dis
                 # %m/m = (masa soluto / masa dis) * 100
                 percent_mass_mass = (percent_mass_volume / density)

            if percent_mass_volume is None and percent_mass_mass is not None and density is not None:
                # Derivar %m/v a partir de %m/m y densidad
                percent_mass_volume = (percent_mass_mass * density)


            if percent_mass_mass is None and percent_mass_volume is None:
                return Response({
                    "error": "Datos insuficientes para el cálculo. Proporcione al menos masa de soluto y disolvente, o masa de soluto y volumen de disolución."
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "percent_mass_mass": f"{percent_mass_mass:.2f}" if percent_mass_mass is not None else "No calculable",
                "percent_mass_volume": f"{percent_mass_volume:.2f}" if percent_mass_volume is not None else "No calculable",
            })

        except (ValueError, TypeError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)