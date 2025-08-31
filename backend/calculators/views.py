import math
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Q, F
from .models import GlossaryTerm, ChemicalPreset, BufferSystem
from .serializers import (
    GlossaryTermSerializer, 
    ChemicalPresetSerializer, 
    BufferSystemSerializer, 
    BufferSuggestionSerializer
)

import logging

logger = logging.getLogger(__name__)

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
        
"""
Views para presets químicos y sistemas buffer.
"""

class ChemicalPresetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar presets químicos predefinidos.
    """
    serializer_class = ChemicalPresetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Devuelve solo los presets activos."""
        queryset = ChemicalPreset.objects.filter(is_active=True)
        
        # Filtrar por categoría si se especifica
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filtrar por tipo de cálculo
        calc_type = self.request.query_params.get('calculation_type')
        if calc_type:
            queryset = queryset.filter(calculation_type=calc_type)
        
        # Filtrar por nivel de dificultad
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Búsqueda por texto
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(chemical_formula__icontains=search) |
                Q(tags__contains=search)
            )
        
        return queryset.order_by('category', 'name')
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """
        Marca un preset como usado e incrementa su contador.
        """
        preset = self.get_object()
        preset.increment_usage()
        
        return Response({
            'success': True,
            'message': f'Preset {preset.name} marcado como usado',
            'calculation_input': preset.get_calculation_input()
        })
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Devuelve los presets más utilizados.
        """
        limit = int(request.query_params.get('limit', 10))
        popular_presets = ChemicalPreset.objects.filter(
            is_active=True
        ).order_by('-usage_count')[:limit]
        
        serializer = self.get_serializer(popular_presets, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        Devuelve las categorías disponibles con conteo.
        """
        categories = []
        for code, name in ChemicalPreset.PRESET_CATEGORIES:
            count = ChemicalPreset.objects.filter(
                category=code,
                is_active=True
            ).count()
            if count > 0:
                categories.append({
                    'code': code,
                    'name': name,
                    'count': count
                })
        
        return Response(categories)


class BufferSystemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para sistemas buffer predefinidos.
    """
    serializer_class = BufferSystemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Devuelve sistemas buffer activos."""
        queryset = BufferSystem.objects.filter(is_active=True)
        
        # Filtrar por rango de pH
        min_ph = self.request.query_params.get('min_ph')
        max_ph = self.request.query_params.get('max_ph')
        
        if min_ph:
            queryset = queryset.filter(effective_ph_max__gte=float(min_ph))
        if max_ph:
            queryset = queryset.filter(effective_ph_min__lte=float(max_ph))
        
        # Búsqueda
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(acid_formula__icontains=search) |
                Q(base_formula__icontains=search)
            )
        
        return queryset.order_by('pka')
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """
        Marca un sistema buffer como usado.
        """
        buffer_system = self.get_object()
        buffer_system.usage_count = F('usage_count') + 1
        buffer_system.save(update_fields=['usage_count'])
        
        return Response({
            'success': True,
            'message': f'Sistema buffer {buffer_system.name} marcado como usado'
        })


class BufferSuggestionView(APIView):
    """
    View para obtener sugerencias de sistemas buffer para un pH objetivo.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Sugiere sistemas buffer adecuados para un pH objetivo.
        
        Query params:
        - target_ph: pH objetivo (requerido)
        - limit: Número máximo de sugerencias (default: 5)
        """
        target_ph = request.query_params.get('target_ph')
        if not target_ph:
            return Response({
                'error': 'Se requiere el parámetro target_ph'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_ph = float(target_ph)
            if not 0 <= target_ph <= 14:
                raise ValueError("pH fuera de rango")
        except ValueError:
            return Response({
                'error': 'target_ph debe ser un número entre 0 y 14'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        limit = int(request.query_params.get('limit', 5))
        
        # Obtener todos los sistemas buffer activos
        all_buffers = BufferSystem.objects.filter(is_active=True)
        
        # Calcular puntuaciones y ordenar
        buffer_suggestions = []
        for buffer_system in all_buffers:
            score = buffer_system.get_suitability_score(target_ph)
            if score > 0:
                buffer_suggestions.append({
                    'buffer_system': buffer_system,
                    'suitability_score': score,
                    'distance_from_pka': abs(target_ph - buffer_system.pka)
                })
        
        # Ordenar por puntuación (descendente)
        buffer_suggestions.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        # Limitar resultados
        buffer_suggestions = buffer_suggestions[:limit]
        
        # Serializar
        serializer = BufferSuggestionSerializer(buffer_suggestions, many=True)
        
        return Response({
            'target_ph': target_ph,
            'suggestions': serializer.data,
            'total_found': len(buffer_suggestions)
        })


class PresetSearchView(APIView):
    """
    View unificada para búsqueda de presets y buffers.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Búsqueda global de presets y sistemas buffer.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response({
                'chemical_presets': [],
                'buffer_systems': [],
                'query': query
            })
        
        # Buscar en presets químicos
        presets = ChemicalPreset.objects.filter(
            Q(is_active=True) & (
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(chemical_formula__icontains=query) |
                Q(tags__contains=query)
            )
        )[:10]
        
        # Buscar en sistemas buffer
        buffers = BufferSystem.objects.filter(
            Q(is_active=True) & (
                Q(name__icontains=query) |
                Q(acid_formula__icontains=query) |
                Q(base_formula__icontains=query) |
                Q(common_uses__icontains=query)
            )
        )[:10]
        
        return Response({
            'chemical_presets': ChemicalPresetSerializer(presets, many=True).data,
            'buffer_systems': BufferSystemSerializer(buffers, many=True).data,
            'query': query,
            'total_results': presets.count() + buffers.count()
        })