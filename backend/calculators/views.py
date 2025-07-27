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
    queryset = GlossaryTerm.objects.all()
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