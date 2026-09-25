"""
Views para el laboratorio virtual de análisis de sistemas.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import logging
import uuid

from .models import (
    ChemicalSubstance, SystemAnalysis, SystemComponent,
    SeparationMethod, SeparationProcess
)
from .serializers import (
    ChemicalSubstanceSerializer, SystemAnalysisSerializer,
    SystemAnalysisInputSerializer, SeparationProcessSerializer,
    SeparationMethodSerializer, SeparationFlowDiagramSerializer,
    SubstanceSearchSerializer
)
from .engines import SystemAnalyzer, ComponentData
from .separation_algorithms import evaluate_all_methods

logger = logging.getLogger(__name__)


@method_decorator(ratelimit(key='ip', rate='20/min', method='POST'), name='dispatch')
class SystemAnalysisView(APIView):
    """
    Vista principal para análisis de sistemas químicos.
    
    POST /api/systems/analyze/
    Analiza un sistema químico y sugiere métodos de separación.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Analiza un sistema químico."""
        serializer = SystemAnalysisInputSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            data = serializer.validated_data
            
            # Crear análisis
            analysis = SystemAnalysis.objects.create(
                user=request.user,
                name=data['name'],
                total_mass=data['total_mass'],
                analysis_temperature=data.get('analysis_conditions', {}).get('temperature', 25.0),
                analysis_pressure=data.get('analysis_conditions', {}).get('pressure', 1.0)
            )
            
            # Crear componentes
            analyzer = SystemAnalyzer()
            component_list = []
            
            for comp_data in data['components']:
                # Buscar sustancia
                try:
                    substance = ChemicalSubstance.objects.get(
                        id=comp_data['substance_id']
                    )
                except ChemicalSubstance.DoesNotExist:
                    # Si no existe, buscar por nombre
                    substance = ChemicalSubstance.objects.filter(
                        Q(name__iexact=comp_data['substance_id']) |
                        Q(formula__iexact=comp_data['substance_id'])
                    ).first()
                    
                    if not substance:
                        # Crear sustancia básica
                        substance = ChemicalSubstance.objects.create(
                            name=comp_data['substance_id'],
                            formula=comp_data.get('formula', comp_data['substance_id']),
                            molecular_weight=comp_data.get('molecular_weight', 100),
                            density=comp_data.get('density', 1.0),
                            phase_at_stp=comp_data.get('phase', 'solid'),
                            chemical_category='inorganic'
                        )
                
                # Crear componente del sistema
                SystemComponent.objects.create(
                    system=analysis,
                    substance=substance,
                    mass_fraction=comp_data['mass_fraction'],
                    particle_size=comp_data.get('particle_size'),
                    phase=comp_data.get('phase', substance.phase_at_stp),
                    is_dispersed=comp_data.get('is_dispersed', False)
                )
                
                # Preparar para análisis
                component_list.append(ComponentData(
                    substance_id=substance.name,
                    mass_fraction=comp_data['mass_fraction'],
                    particle_size=comp_data.get('particle_size'),
                    phase=comp_data.get('phase', substance.phase_at_stp)
                ))
            
            # Ejecutar análisis
            conditions = {
                'temperature': analysis.analysis_temperature,
                'pressure': analysis.analysis_pressure
            }
            
            result = analyzer.analyze_mixture(component_list, conditions)
            
            # Guardar resultados
            analysis.system_type = result.system_type
            analysis.phases_detected = [
                {
                    'phase': p.phase_type,
                    'components': p.components,
                    'total_fraction': p.total_fraction
                }
                for p in result.phases
            ]
            
            recommended_methods = []
            for method in result.suggested_methods:
                recommended_methods.append({
                    'method': method.method,
                    'target': method.target_components,
                    'efficiency': method.efficiency,
                    'difficulty': method.difficulty
                })
            
            analysis.analysis_data = {
                'system_type': result.system_type,
                'phases_detected': analysis.phases_detected,
                'recommended_methods': recommended_methods,
                'overall_separability': result.overall_separability,
                'estimated_time': result.estimated_time,
                'complexity_level': result.complexity_level
            }
            analysis.save()
            
            # Serializar respuesta
            response_data = {
                'success': True,
                'analysis_id': str(analysis.id),
                'results': {
                    'system_type': result.system_type,
                    'phases_detected': analysis.phases_detected,
                    'recommended_methods': recommended_methods,
                    'overall_separability': result.overall_separability,
                    'estimated_time': result.estimated_time,
                    'complexity_level': result.complexity_level
                }
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error en análisis de sistema: {e}")
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SeparationMethodsView(APIView):
    """
    Vista para obtener métodos de separación disponibles.
    
    GET /api/systems/separation-methods/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Lista todos los métodos de separación disponibles."""
        methods = SeparationMethod.objects.all()
        
        if 'type' in request.query_params:
            methods = methods.filter(method_type=request.query_params['type'])
        
        if 'complexity' in request.query_params:
            methods = methods.filter(complexity_level=request.query_params['complexity'])
        
        serializer = SeparationMethodSerializer(methods, many=True)
        
        return Response({
            'success': True,
            'methods': serializer.data
        })


@method_decorator(ratelimit(key='ip', rate='10/min', method='POST'), name='dispatch')
class GenerateSeparationFlowView(APIView):
    """
    Vista para generar diagramas de flujo de separación.
    
    POST /api/systems/generate-separation-flow/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Genera un diagrama de flujo optimizado."""
        serializer = SeparationFlowDiagramSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            data = serializer.validated_data
            analysis = SystemAnalysis.objects.get(id=data['analysis_id'])
            
            # Verificar permisos
            if analysis.user and analysis.user != request.user:
                return Response(
                    {'success': False, 'error': 'No autorizado'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Generar proceso de separación
            analyzer = SystemAnalyzer()
            
            # Obtener métodos sugeridos del análisis
            suggested_methods = analysis.analysis_data.get('recommended_methods', [])
            
            # Si hay métodos seleccionados, filtrar
            if data.get('selected_methods'):
                suggested_methods = [
                    m for m in suggested_methods 
                    if m['method'] in data['selected_methods']
                ]
            
            # Crear proceso de separación
            process = SeparationProcess.objects.create(
                system_analysis=analysis,
                user=request.user,
                process_name=f"Proceso para {analysis.name}",
                separation_steps=[],
                predicted_efficiency=0.0,
                estimated_time=0.0,
                estimated_cost=0.0,
                difficulty_level='basic'
            )
            
            # Generar pasos del proceso
            steps = []
            total_efficiency = 1.0
            total_time = 0.0
            max_difficulty = 'basic'
            
            for i, method in enumerate(suggested_methods):
                step = {
                    'step': i + 1,
                    'method': method['method'],
                    'description': f"Separar {', '.join(method['target'][:2])}",
                    'input': ['all_components'] if i == 0 else [f'sink_from_step_{i}'],
                    'output': {
                        method['method']: method['target'],
                        'remaining': f'mixture_minus_{method["method"]}'
                    },
                    'efficiency': method['efficiency'],
                    'time': 0.5,  # Tiempo estimado base
                    'equipment': self._get_equipment_for_method(method['method'])
                }
                
                steps.append(step)
                total_efficiency *= method['efficiency']
                total_time += step['time']
                
                if method['difficulty'] == 'advanced':
                    max_difficulty = 'advanced'
                elif method['difficulty'] == 'intermediate' and max_difficulty != 'advanced':
                    max_difficulty = 'intermediate'
            
            # Actualizar proceso
            process.separation_steps = steps
            process.predicted_efficiency = total_efficiency * 100
            process.estimated_time = total_time
            process.estimated_cost = len(steps) * 10  # Costo base por paso
            process.difficulty_level = max_difficulty
            
            # Generar productos finales
            process.final_products = self._generate_final_products(analysis, steps)
            
            # Generar diagrama
            process.process_diagram = process.generate_process_diagram()
            process.save()
            
            # Respuesta
            response_data = {
                'success': True,
                'process_id': str(process.id),
                'separation_flow': {
                    'steps': steps,
                    'final_products': process.final_products,
                    'overall_efficiency': process.predicted_efficiency,
                    'total_time': process.estimated_time,
                    'total_cost': process.estimated_cost,
                    'diagram_data': process.process_diagram
                }
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error generando flujo de separación: {e}")
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_equipment_for_method(self, method_name):
        """Obtiene el equipo necesario para un método."""
        equipment_map = {
            'tamizacion': ['Tamices', 'Agitador'],
            'magnetic_separation': ['Imán permanente'],
            'filtration': ['Papel filtro', 'Embudo'],
            'flotation': ['Tanque de flotación', 'Agua'],
            'distillation': ['Matraz de destilación', 'Condensador'],
            'crystallization': ['Cristalizador', 'Sistema de enfriamiento']
        }
        return equipment_map.get(method_name, ['Equipo estándar'])
    
    def _generate_final_products(self, analysis, steps):
        """Genera la lista de productos finales."""
        products = []
        
        for component in analysis.systemcomponent_set.all():
            # Determinar en qué paso se separa
            separated_in_step = None
            for step in steps:
                if component.substance.name in step['output'].get(step['method'], []):
                    separated_in_step = step['step']
                    break
            
            products.append({
                'name': component.substance.name,
                'purity': 0.95 if separated_in_step else 0.90,
                'recovery': 0.90 if separated_in_step else 0.85,
                'separated_in_step': separated_in_step
            })
        
        return products


class SubstancePropertiesView(APIView):
    """
    Vista para obtener propiedades de sustancias.
    
    GET /api/systems/substance-properties/{id}/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        """Obtiene las propiedades de una sustancia."""
        try:
            substance = get_object_or_404(ChemicalSubstance, id=id)
            serializer = ChemicalSubstanceSerializer(substance)
            
            return Response({
                'success': True,
                'substance': serializer.data
            })
            
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SubstanceSearchView(APIView):
    """
    Vista para búsqueda de sustancias.
    
    GET /api/systems/substances/search/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Busca sustancias por múltiples criterios."""
        serializer = SubstanceSearchSerializer(data=request.query_params)
        
        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        queryset = ChemicalSubstance.objects.all()
        
        # Aplicar filtros
        if data.get('query'):
            queryset = queryset.filter(
                Q(name__icontains=data['query']) |
                Q(formula__icontains=data['query']) |
                Q(cas_number__icontains=data['query'])
            )
        
        if data.get('phase'):
            queryset = queryset.filter(phase_at_stp=data['phase'])
        
        if data.get('category'):
            queryset = queryset.filter(chemical_category=data['category'])
        
        if data.get('min_density'):
            queryset = queryset.filter(density__gte=data['min_density'])
        
        if data.get('max_density'):
            queryset = queryset.filter(density__lte=data['max_density'])
        
        if data.get('magnetic'):
            queryset = queryset.filter(magnetic_susceptibility__gt=1e-6)
        
        if data.get('soluble'):
            queryset = queryset.filter(solubility_water__gt=10)
        
        # Limitar resultados
        queryset = queryset[:50]
        
        serializer = ChemicalSubstanceSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'count': len(serializer.data),
            'substances': serializer.data
        })


class SystemAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de análisis de sistemas."""
    
    serializer_class = SystemAnalysisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra análisis por usuario."""
        return SystemAnalysis.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Obtiene estadísticas de análisis del usuario."""
        analyses = self.get_queryset()
        
        stats = {
            'total_analyses': analyses.count(),
            'system_types': {},
            'complexity_levels': {},
            'average_separability': 0.0
        }
        
        for analysis in analyses:
            # Contar tipos de sistema
            system_type = analysis.system_type
            stats['system_types'][system_type] = stats['system_types'].get(system_type, 0) + 1
            
            # Contar niveles de complejidad
            if analysis.analysis_data:
                complexity = analysis.analysis_data.get('complexity_level', 'unknown')
                stats['complexity_levels'][complexity] = stats['complexity_levels'].get(complexity, 0) + 1
                
                # Sumar separabilidad
                stats['average_separability'] += analysis.analysis_data.get('overall_separability', 0)
        
        # Calcular promedio
        if analyses.count() > 0:
            stats['average_separability'] /= analyses.count()
        
        return Response(stats)