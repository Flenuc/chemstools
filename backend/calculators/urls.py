from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django_ratelimit.decorators import ratelimit

from .views import GlossaryTermViewSet, pHCalculatorView, SolutionCalculatorView
from .advanced_views import (
    AdvancedPHCalculatorView,
    PHCalculationHistoryViewSet,
    ExportPHCalculationsView,
    PHCalculationStatsView,
    BufferCalculatorView
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'glossary', GlossaryTermViewSet, basename='glossaryterm')
router.register(r'ph-calculation-history', PHCalculationHistoryViewSet, basename='ph-calculation-history')

# Aplicar rate limiting a views específicas
advanced_ph_calculator_view = ratelimit(
    key='user', 
    rate='30/m', 
    method='POST'
)(AdvancedPHCalculatorView.as_view())

export_ph_calculations_view = ratelimit(
    key='user', 
    rate='5/m', 
    method='POST'
)(ExportPHCalculationsView.as_view())

ph_calculation_stats_view = ratelimit(
    key='user', 
    rate='100/m', 
    method='GET'
)(PHCalculationStatsView.as_view())

buffer_calculator_view = ratelimit(
    key='user', 
    rate='20/m', 
    method='POST'
)(BufferCalculatorView.as_view())

urlpatterns = [
    # URLs del router (incluye glossary y ph-calculation-history)
    path('', include(router.urls)),
    
    # Endpoints básicos existentes (mantener backward compatibility)
    path('ph-calculator/', pHCalculatorView.as_view(), name='ph-calculator'),
    path('solution-calculator/', SolutionCalculatorView.as_view(), name='solution-calculator'),
    
    # Nuevos endpoints avanzados
    path('advanced-ph-calculator/', advanced_ph_calculator_view, name='advanced-ph-calculator'),
    path('export-ph-calculations/', export_ph_calculations_view, name='export-ph-calculations'),
    path('ph-calculation-stats/', ph_calculation_stats_view, name='ph-calculation-stats'),
    path('buffer-calculator/', buffer_calculator_view, name='buffer-calculator'),
]

# URLs con rate limiting específico:
# - advanced-ph-calculator/: 30/min - Permite cálculos frecuentes pero controlados
# - export-ph-calculations/: 5/min - Limita exports para evitar abuso del sistema
# - ph-calculation-history/: 100/min - Permite consultas frecuentes del historial
# - ph-calculation-stats/: 100/min - Permite consultas frecuentes de estadísticas
# - buffer-calculator/: 20/min - Rate limiting moderado para cálculos de buffer