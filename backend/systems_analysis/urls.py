"""
URLs para el sistema de análisis de sistemas químicos.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SystemAnalysisView,
    SeparationMethodsView,
    GenerateSeparationFlowView,
    SubstancePropertiesView,
    SubstanceSearchView,
    SystemAnalysisViewSet
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'analysis-history', SystemAnalysisViewSet, basename='system-analysis')

app_name = 'systems_analysis'

urlpatterns = [
    # Análisis principal
    path('analyze/', SystemAnalysisView.as_view(), name='analyze-system'),
    
    # Métodos de separación
    path('separation-methods/', SeparationMethodsView.as_view(), name='separation-methods'),
    
    # Generación de diagramas
    path('generate-separation-flow/', GenerateSeparationFlowView.as_view(), name='generate-flow'),
    
    # Propiedades de sustancias
    path('substance-properties/<int:id>/', SubstancePropertiesView.as_view(), name='substance-properties'),
    
    # Búsqueda de sustancias
    path('substances/search/', SubstanceSearchView.as_view(), name='substance-search'),
    
    # ViewSet routes
    path('', include(router.urls)),
]