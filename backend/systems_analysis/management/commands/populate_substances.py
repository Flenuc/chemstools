"""
Comando para poblar la base de datos con sustancias químicas comunes.
"""
from django.core.management.base import BaseCommand
from systems_analysis.models import ChemicalSubstance, SeparationMethod
import json


class Command(BaseCommand):
    help = 'Pobla la base de datos con sustancias químicas comunes'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--category',
            type=str,
            help='Categoría específica a poblar'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpiar datos existentes antes de poblar'
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Limpiando datos existentes...')
            ChemicalSubstance.objects.all().delete()
            SeparationMethod.objects.all().delete()
        
        # Poblar sustancias
        self.populate_substances(options.get('category'))
        
        # Poblar métodos de separación
        self.populate_separation_methods()
        
        self.stdout.write(
            self.style.SUCCESS('Base de datos poblada exitosamente')
        )
    
    def populate_substances(self, category=None):
        """Pobla las sustancias químicas."""
        substances = [
            # Metales
            {
                'name': 'Hierro',
                'formula': 'Fe',
                'molecular_weight': 55.845,
                'density': 7.874,
                'melting_point': 1538,
                'boiling_point': 2862,
                'magnetic_susceptibility': 2.2e-1,
                'phase_at_stp': 'solid',
                'chemical_category': 'metal',
                'color': 'Gris metálico'
            },
            {
                'name': 'Aluminio',
                'formula': 'Al',
                'molecular_weight': 26.982,
                'density': 2.70,
                'melting_point': 660.3,
                'boiling_point': 2519,
                'phase_at_stp': 'solid',
                'chemical_category': 'metal',
                'color': 'Plateado'
            },
            {
                'name': 'Cobre',
                'formula': 'Cu',
                'molecular_weight': 63.546,
                'density': 8.96,
                'melting_point': 1085,
                'boiling_point': 2562,
                'phase_at_stp': 'solid',
                'chemical_category': 'metal',
                'color': 'Rojizo'
            },
            
            # Sales
            {
                'name': 'Cloruro de sodio',
                'formula': 'NaCl',
                'molecular_weight': 58.44,
                'density': 2.165,
                'melting_point': 801,
                'boiling_point': 1465,
                'solubility_water': 359,
                'phase_at_stp': 'solid',
                'chemical_category': 'salt',
                'color': 'Blanco'
            },
            {
                'name': 'Sulfato de cobre',
                'formula': 'CuSO4',
                'molecular_weight': 159.61,
                'density': 3.60,
                'melting_point': 110,
                'solubility_water': 203,
                'phase_at_stp': 'solid',
                'chemical_category': 'salt',
                'color': 'Azul'
            },
            {
                'name': 'Carbonato de calcio',
                'formula': 'CaCO3',
                'molecular_weight': 100.09,
                'density': 2.71,
                'melting_point': 825,
                'solubility_water': 0.013,
                'phase_at_stp': 'solid',
                'chemical_category': 'salt',
                'color': 'Blanco'
            },
            
            # Óxidos
            {
                'name': 'Óxido de hierro(III)',
                'formula': 'Fe2O3',
                'molecular_weight': 159.69,
                'density': 5.24,
                'melting_point': 1539,
                'magnetic_susceptibility': 3.5e-3,
                'phase_at_stp': 'solid',
                'chemical_category': 'oxide',
                'color': 'Rojo óxido'
            },
            {
                'name': 'Dióxido de silicio',
                'formula': 'SiO2',
                'molecular_weight': 60.08,
                'density': 2.65,
                'melting_point': 1713,
                'boiling_point': 2950,
                'phase_at_stp': 'solid',
                'chemical_category': 'oxide',
                'color': 'Transparente/Blanco'
            },
            
            # Materiales comunes
            {
                'name': 'Arena',
                'formula': 'SiO2',
                'molecular_weight': 60.08,
                'density': 2.65,
                'particle_size_range': {'min': 100, 'max': 2000},
                'phase_at_stp': 'solid',
                'chemical_category': 'mineral',
                'color': 'Amarillo/Beige'
            },
            {
                'name': 'Agua',
                'formula': 'H2O',
                'molecular_weight': 18.015,
                'density': 1.00,
                'melting_point': 0,
                'boiling_point': 100,
                'phase_at_stp': 'liquid',
                'chemical_category': 'inorganic',
                'color': 'Transparente'
            },
            {
                'name': 'Aceite vegetal',
                'formula': 'C57H104O6',
                'molecular_weight': 885.4,
                'density': 0.92,
                'boiling_point': 300,
                'solubility_water': 0.001,
                'phase_at_stp': 'liquid',
                'chemical_category': 'organic',
                'color': 'Amarillo'
            },
            {
                'name': 'Corcho',
                'formula': 'C123H182O56N2',
                'molecular_weight': 2500,
                'density': 0.24,
                'particle_size_range': {'min': 1000, 'max': 5000},
                'phase_at_stp': 'solid',
                'chemical_category': 'organic',
                'color': 'Marrón claro'
            },
            {
                'name': 'Limaduras de hierro',
                'formula': 'Fe',
                'molecular_weight': 55.845,
                'density': 7.874,
                'magnetic_susceptibility': 2.2e-1,
                'particle_size_range': {'min': 50, 'max': 500},
                'phase_at_stp': 'solid',
                'chemical_category': 'metal',
                'color': 'Gris oscuro'
            },
            
            # Líquidos
            {
                'name': 'Etanol',
                'formula': 'C2H5OH',
                'molecular_weight': 46.07,
                'density': 0.789,
                'melting_point': -114.1,
                'boiling_point': 78.37,
                'solubility_water': 1000000,  # Miscible
                'phase_at_stp': 'liquid',
                'chemical_category': 'organic',
                'color': 'Transparente'
            },
            {
                'name': 'Ácido clorhídrico',
                'formula': 'HCl',
                'molecular_weight': 36.46,
                'density': 1.18,
                'boiling_point': 108.6,
                'solubility_water': 720,
                'phase_at_stp': 'liquid',
                'chemical_category': 'acid',
                'color': 'Transparente'
            },
            
            # Gases
            {
                'name': 'Dióxido de carbono',
                'formula': 'CO2',
                'molecular_weight': 44.01,
                'density': 0.00198,
                'melting_point': -78.5,
                'boiling_point': -78.5,
                'phase_at_stp': 'gas',
                'chemical_category': 'inorganic',
                'color': 'Incoloro'
            }
        ]
        
        created_count = 0
        for data in substances:
            if category and data['chemical_category'] != category:
                continue
            
            substance, created = ChemicalSubstance.objects.get_or_create(
                formula=data['formula'],
                defaults=data
            )
            if created:
                created_count += 1
                self.stdout.write(f"Creada sustancia: {substance.name}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Se crearon {created_count} sustancias')
        )
    
    def populate_separation_methods(self):
        """Pobla los métodos de separación."""
        methods = [
            {
                'name': 'Tamización',
                'method_type': 'mechanical',
                'description': 'Separación por tamaño de partícula usando tamices',
                'principle': 'Diferencia en el tamaño de partícula',
                'equipment_required': ['Tamices', 'Agitador'],
                'efficiency_range': {'min': 90, 'max': 99},
                'cost_factor': 1,
                'complexity_level': 'basic',
                'applicable_phases': ['solid'],
                'property_criteria': {'particle_size_ratio': 10}
            },
            {
                'name': 'Separación Magnética',
                'method_type': 'magnetic',
                'description': 'Separación usando propiedades magnéticas',
                'principle': 'Diferencia en susceptibilidad magnética',
                'equipment_required': ['Imán', 'Separador magnético'],
                'efficiency_range': {'min': 95, 'max': 99},
                'cost_factor': 2,
                'complexity_level': 'basic',
                'applicable_phases': ['solid'],
                'property_criteria': {'magnetic_susceptibility': 1e-6}
            },
            {
                'name': 'Flotación',
                'method_type': 'physical',
                'description': 'Separación por diferencia de densidad en líquido',
                'principle': 'Diferencia de densidad relativa',
                'equipment_required': ['Tanque de flotación', 'Agitador'],
                'efficiency_range': {'min': 70, 'max': 95},
                'cost_factor': 2,
                'complexity_level': 'basic',
                'applicable_phases': ['solid'],
                'property_criteria': {'density_difference': 0.1}
            },
            {
                'name': 'Filtración',
                'method_type': 'physical',
                'description': 'Separación sólido-líquido usando membrana',
                'principle': 'Retención por tamaño de poro',
                'equipment_required': ['Filtro', 'Embudo', 'Bomba de vacío'],
                'efficiency_range': {'min': 95, 'max': 99.9},
                'cost_factor': 1,
                'complexity_level': 'basic',
                'applicable_phases': ['solid', 'liquid'],
                'property_criteria': {'min_particle_size': 1}
            },
            {
                'name': 'Decantación',
                'method_type': 'physical',
                'description': 'Separación por gravedad de líquidos inmiscibles',
                'principle': 'Diferencia de densidad entre líquidos',
                'equipment_required': ['Embudo de decantación'],
                'efficiency_range': {'min': 85, 'max': 95},
                'cost_factor': 1,
                'complexity_level': 'basic',
                'applicable_phases': ['liquid'],
                'property_criteria': {'density_difference': 0.05}
            },
            {
                'name': 'Destilación Simple',
                'method_type': 'thermal',
                'description': 'Separación por diferencia de punto de ebullición',
                'principle': 'Volatilidad diferencial',
                'equipment_required': ['Matraz', 'Condensador', 'Fuente de calor'],
                'efficiency_range': {'min': 85, 'max': 95},
                'cost_factor': 3,
                'complexity_level': 'intermediate',
                'applicable_phases': ['liquid'],
                'property_criteria': {'boiling_point_difference': 25}
            },
            {
                'name': 'Cristalización',
                'method_type': 'physical',
                'description': 'Separación por diferencia de solubilidad',
                'principle': 'Sobresaturación y nucleación',
                'equipment_required': ['Cristalizador', 'Sistema de enfriamiento'],
                'efficiency_range': {'min': 80, 'max': 95},
                'cost_factor': 3,
                'complexity_level': 'intermediate',
                'applicable_phases': ['solid', 'liquid'],
                'property_criteria': {'solubility_difference': 10}
            },
            {
                'name': 'Extracción Líquido-Líquido',
                'method_type': 'chemical',
                'description': 'Separación usando solvente selectivo',
                'principle': 'Solubilidad selectiva',
                'equipment_required': ['Embudo de extracción', 'Solventes'],
                'efficiency_range': {'min': 75, 'max': 90},
                'cost_factor': 4,
                'complexity_level': 'intermediate',
                'applicable_phases': ['liquid'],
                'property_criteria': {'partition_coefficient': 10}
            },
            {
                'name': 'Sublimación',
                'method_type': 'thermal',
                'description': 'Separación por transición sólido-gas directa',
                'principle': 'Sublimación selectiva',
                'equipment_required': ['Sublimador', 'Sistema de vacío'],
                'efficiency_range': {'min': 90, 'max': 98},
                'cost_factor': 4,
                'complexity_level': 'advanced',
                'applicable_phases': ['solid'],
                'property_criteria': {'sublimation_temperature': 100}
            },
            {
                'name': 'Cromatografía',
                'method_type': 'physical',
                'description': 'Separación por afinidad diferencial',
                'principle': 'Partición entre fases',
                'equipment_required': ['Columna', 'Fase estacionaria', 'Eluyente'],
                'efficiency_range': {'min': 95, 'max': 99.9},
                'cost_factor': 5,
                'complexity_level': 'advanced',
                'applicable_phases': ['liquid', 'gas'],
                'property_criteria': {'retention_factor': 0.1}
            }
        ]
        
        created_count = 0
        for data in methods:
            method, created = SeparationMethod.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                created_count += 1
                self.stdout.write(f"Creado método: {method.name}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Se crearon {created_count} métodos de separación')
        )