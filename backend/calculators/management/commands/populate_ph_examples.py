"""
Comando para poblar ejemplos de cálculos de pH.
Uso: python manage.py populate_ph_examples
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from calculators.models import PHCalculationHistory
from calculators.utils import comprehensive_ph_calculation
import uuid

User = get_user_model()


class Command(BaseCommand):
    help = 'Pobla la base de datos con ejemplos de cálculos de pH para testing y demos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username del usuario para asignar los cálculos (opcional)',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Número de cálculos de ejemplo a crear (default: 20)',
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Eliminar ejemplos existentes antes de crear nuevos',
        )

    def handle(self, *args, **options):
        user = None
        
        # Obtener o crear usuario
        if options['user']:
            try:
                user = User.objects.get(username=options['user'])
                self.stdout.write(f"Usando usuario existente: {user.username}")
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Usuario '{options['user']}' no encontrado")
                )
                return
        else:
            # Crear usuario demo si no existe
            user, created = User.objects.get_or_create(
                username='demo_user',
                defaults={
                    'email': 'demo@chemstools.com',
                    'first_name': 'Demo',
                    'last_name': 'User'
                }
            )
            if created:
                user.set_password('demo123')
                user.save()
                self.stdout.write(f"Usuario demo creado: {user.username}")
            else:
                self.stdout.write(f"Usando usuario demo existente: {user.username}")

        # Limpiar ejemplos existentes si se solicita
        if options['clean']:
            deleted_count = PHCalculationHistory.objects.filter(
                user=user,
                input_data__contains={'example': True}
            ).delete()[0]
            self.stdout.write(f"Eliminados {deleted_count} ejemplos existentes")

        # Crear ejemplos
        examples = self._get_example_calculations()
        created_count = 0
        
        for i, example in enumerate(examples[:options['count']]):
            try:
                # Realizar cálculo
                results = comprehensive_ph_calculation(example['input_data'])
                
                # Crear entrada en historial
                calculation = PHCalculationHistory.objects.create(
                    user=user,
                    calculation_type=example['input_data']['calculation_type'],
                    input_data={**example['input_data'], 'example': True},
                    results=results,
                    calculation_steps=example.get('steps'),
                    warnings=example.get('warnings', []),
                    temperature=example['input_data'].get('temperature', 25.0),
                    ionic_strength=example['input_data'].get('ionic_strength'),
                    calculation_time_ms=example.get('calculation_time_ms', 100)
                )
                
                created_count += 1
                self.stdout.write(f"Creado ejemplo {i+1}: {example['description']}")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error creando ejemplo {i+1}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Creados {created_count} ejemplos de cálculos de pH para el usuario {user.username}"
            )
        )

    def _get_example_calculations(self):
        """Devuelve lista de cálculos de ejemplo."""
        return [
            # Ejemplos básicos de pH
            {
                'description': 'Agua pura a 25°C',
                'input_data': {
                    'calculation_type': 'ph_to_all',
                    'input_value': 7.0,
                    'input_type': 'ph',
                    'temperature': 25.0,
                    'show_steps': True
                },
                'steps': [
                    'Agua pura a 25°C tiene pH neutro = 7.0',
                    '[H+] = 10^(-7) = 1.0×10⁻⁷ M',
                    '[OH-] = Kw/[H+] = 1.0×10⁻¹⁴/1.0×10⁻⁷ = 1.0×10⁻⁷ M',
                    'pOH = -log([OH-]) = 7.0'
                ]
            },
            {
                'description': 'Ácido fuerte (HCl 0.01 M)',
                'input_data': {
                    'calculation_type': 'concentration_to_ph',
                    'input_value': 0.01,
                    'input_type': 'h_concentration',
                    'temperature': 25.0,
                    'show_steps': True
                },
                'steps': [
                    'HCl es un ácido fuerte, disociación completa',
                    '[H+] = 0.01 M',
                    'pH = -log([H+]) = -log(0.01) = 2.0',
                    '[OH-] = Kw/[H+] = 1.0×10⁻¹⁴/0.01 = 1.0×10⁻¹² M'
                ]
            },
            {
                'description': 'Base fuerte (NaOH 0.001 M)',
                'input_data': {
                    'calculation_type': 'concentration_to_ph',
                    'input_value': 0.001,
                    'input_type': 'oh_concentration',
                    'temperature': 25.0,
                    'show_steps': True
                },
                'steps': [
                    'NaOH es una base fuerte, disociación completa',
                    '[OH-] = 0.001 M',
                    'pOH = -log([OH-]) = -log(0.001) = 3.0',
                    'pH = 14 - pOH = 14 - 3 = 11.0'
                ]
            },
            {
                'description': 'Sistema buffer acetato (pH 4.76)',
                'input_data': {
                    'calculation_type': 'buffer_calculation',
                    'input_value': 4.76,
                    'input_type': 'ph',
                    'buffer_components': [
                        {'compound': 'CH3COOH', 'concentration': 0.1, 'pka': 4.76},
                        {'compound': 'CH3COONa', 'concentration': 0.1}
                    ],
                    'temperature': 25.0,
                    'show_steps': True
                },
                'steps': [
                    'Sistema buffer acetato/acetato',
                    'Concentraciones iguales: [CH3COOH] = [CH3COO-] = 0.1 M',
                    'En el pKa, pH = pKa = 4.76',
                    'Capacidad buffer máxima en el pKa'
                ]
            },
            {
                'description': 'Corrección por actividad (I = 0.5 M)',
                'input_data': {
                    'calculation_type': 'activity_correction',
                    'input_value': 2.0,
                    'input_type': 'ph',
                    'ionic_strength': 0.5,
                    'include_activity': True,
                    'temperature': 25.0,
                    'show_steps': True
                },
                'warnings': ['Fuerza iónica alta (0.5 M): los coeficientes de actividad son aproximados']
            },
            {
                'description': 'Agua a alta temperatura (80°C)',
                'input_data': {
                    'calculation_type': 'ph_to_all',
                    'input_value': 6.14,  # pH neutro a 80°C
                    'input_type': 'ph',
                    'temperature': 80.0,
                    'show_steps': True
                },
                'warnings': ['Temperatura alta: puede afectar la estabilidad de compuestos'],
                'steps': [
                    'A 80°C, Kw = 2.5×10⁻¹³',
                    'pH neutro = -0.5×log(Kw) = 6.14',
                    'Corrección de temperatura aplicada'
                ]
            },
            {
                'description': 'Sistema extremadamente ácido (pH 0.5)',
                'input_data': {
                    'calculation_type': 'ph_to_all',
                    'input_value': 0.5,
                    'input_type': 'ph',
                    'temperature': 25.0,
                    'show_steps': True
                },
                'warnings': ['pH muy ácido (<1): considere medidas de seguridad']
            },
            {
                'description': 'Sistema extremadamente básico (pH 13.5)',
                'input_data': {
                    'calculation_type': 'ph_to_all',
                    'input_value': 13.5,
                    'input_type': 'ph',
                    'temperature': 25.0,
                    'show_steps': True
                },
                'warnings': ['pH muy básico (>13): considere medidas de seguridad']
            },
            {
                'description': 'Buffer fosfato fisiológico (pH 7.4)',
                'input_data': {
                    'calculation_type': 'buffer_calculation',
                    'input_value': 7.4,
                    'input_type': 'ph',
                    'buffer_components': [
                        {'compound': 'H2PO4-', 'concentration': 0.025, 'pka': 7.21},
                        {'compound': 'HPO4-2', 'concentration': 0.075}
                    ],
                    'temperature': 37.0,  # Temperatura corporal
                    'ionic_strength': 0.15,  # Fuerza iónica fisiológica
                    'include_activity': True,
                    'show_steps': True
                }
            },
            {
                'description': 'Titulación ácido fuerte - base fuerte (punto de equivalencia)',
                'input_data': {
                    'calculation_type': 'ph_to_all',
                    'input_value': 7.0,
                    'input_type': 'ph',
                    'temperature': 25.0,
                    'show_steps': True
                },
                'steps': [
                    'Punto de equivalencia en titulación HCl + NaOH',
                    'Solo agua y sal presente: NaCl',
                    'pH = 7.0 (neutro) a 25°C'
                ]
            },
            {
                'description': 'Sistema con muy baja fuerza iónica',
                'input_data': {
                    'calculation_type': 'activity_correction',
                    'input_value': 7.0,
                    'input_type': 'ph',
                    'ionic_strength': 0.001,
                    'include_activity': True,
                    'temperature': 25.0
                }
            },
            {
                'description': 'Buffer Tris para bioquímica (pH 8.0)',
                'input_data': {
                    'calculation_type': 'buffer_calculation',
                    'input_value': 8.0,
                    'input_type': 'ph',
                    'buffer_components': [
                        {'compound': 'Tris-H+', 'concentration': 0.05, 'pka': 8.07},
                        {'compound': 'Tris', 'concentration': 0.15}
                    ],
                    'temperature': 25.0,
                    'show_steps': True
                }
            },
            {
                'description': 'Lluvia ácida (pH 4.2)',
                'input_data': {
                    'calculation_type': 'ph_to_all',
                    'input_value': 4.2,
                    'input_type': 'ph',
                    'temperature': 25.0,
                    'show_steps': True
                },
                'steps': [
                    'Lluvia ácida debido a contaminación atmosférica',
                    '[H+] = 10^(-4.2) = 6.3×10⁻⁵ M',
                    'Concentración significativa de ácido'
                ]
            },
            {
                'description': 'Agua de mar (pH 8.1)',
                'input_data': {
                    'calculation_type': 'activity_correction',
                    'input_value': 8.1,
                    'input_type': 'ph',
                    'ionic_strength': 0.7,  # Fuerza iónica del agua de mar
                    'include_activity': True,
                    'temperature': 25.0,
                    'show_steps': True
                },
                'warnings': ['Fuerza iónica alta (0.7 M): los coeficientes de actividad son aproximados']
            },
            {
                'description': 'Buffer carbonato (pH 10.3)',
                'input_data': {
                    'calculation_type': 'buffer_calculation',
                    'input_value': 10.3,
                    'input_type': 'ph',
                    'buffer_components': [
                        {'compound': 'HCO3-', 'concentration': 0.1, 'pka': 10.33},
                        {'compound': 'CO3-2', 'concentration': 0.1}
                    ],
                    'temperature': 25.0,
                    'show_steps': True
                }
            },
            {
                'description': 'Concentración muy diluida (pH 6.8)',
                'input_data': {
                    'calculation_type': 'concentration_to_ph',
                    'input_value': 1.58e-7,
                    'input_type': 'h_concentration',
                    'temperature': 25.0,
                    'show_steps': True
                },
                'steps': [
                    'Concentración muy diluida de ácido',
                    '[H+] = 1.58×10⁻⁷ M',
                    'pH = -log(1.58×10⁻⁷) = 6.8',
                    'Cercano al neutro debido a dilución extrema'
                ]
            },
            {
                'description': 'Sistema a baja temperatura (5°C)',
                'input_data': {
                    'calculation_type': 'ph_to_all',
                    'input_value': 7.47,  # pH neutro a 5°C
                    'input_type': 'ph',
                    'temperature': 5.0,
                    'show_steps': True
                },
                'warnings': ['Temperatura baja: puede afectar la cinética de reacciones'],
                'steps': [
                    'A 5°C, Kw = 1.85×10⁻¹⁵',
                    'pH neutro = -0.5×log(Kw) = 7.47',
                    'El agua es menos ionizada a baja temperatura'
                ]
            },
            {
                'description': 'Buffer con capacidad limitada (concentración baja)',
                'input_data': {
                    'calculation_type': 'buffer_calculation',
                    'input_value': 4.76,
                    'input_type': 'ph',
                    'buffer_components': [
                        {'compound': 'CH3COOH', 'concentration': 0.001, 'pka': 4.76},
                        {'compound': 'CH3COONa', 'concentration': 0.001}
                    ],
                    'temperature': 25.0,
                    'show_steps': True
                },
                'warnings': ['Concentración total baja (<0.01M): capacidad buffer limitada']
            },
            {
                'description': 'Sistema poliprótico (H3PO4)',
                'input_data': {
                    'calculation_type': 'buffer_calculation',
                    'input_value': 2.15,  # pKa1 del H3PO4
                    'input_type': 'ph',
                    'buffer_components': [
                        {'compound': 'H3PO4', 'concentration': 0.1, 'pka': 2.15},
                        {'compound': 'H2PO4-', 'concentration': 0.1}
                    ],
                    'temperature': 25.0,
                    'show_steps': True
                }
            },
            {
                'description': 'Efecto de dilución en ácido débil',
                'input_data': {
                    'calculation_type': 'concentration_to_ph',
                    'input_value': 1e-8,
                    'input_type': 'h_concentration',
                    'temperature': 25.0,
                    'show_steps': True
                },
                'steps': [
                    'Concentración extremadamente baja',
                    '[H+] = 1.0×10⁻⁸ M',
                    'pH = 8.0 (básico debido a contribución del agua)',
                    'La autoionización del agua domina'
                ]
            }
        ]