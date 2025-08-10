from django.core.management.base import BaseCommand
from games.models import ChemicalWord

class Command(BaseCommand):
    help = 'Populate the database with sample ChemWordle words'

    def handle(self, *args, **options):
        words_data = [
            # ELEMENTOS - FÁCIL
            {
                'word': 'HIDROGENO',
                'category': 'element',
                'difficulty': 'easy',
                'hint': 'El elemento más ligero y abundante en el universo',
                'atomic_number': 1,
                'group_number': 1,
                'period_number': 1,
                'state_at_stp': 'gas',
                'chemical_formula': 'H',
                'molecular_weight': 1.008,
                'hints_progressive': [
                    'Es un gas a temperatura ambiente',
                    'Tiene solo un protón',
                    'Se usa en la síntesis del amoníaco',
                    'Forma agua al combinarse con oxígeno',
                    'Su símbolo es H'
                ]
            },
            {
                'word': 'OXIGENO',
                'category': 'element',
                'difficulty': 'easy',
                'hint': 'Gas esencial para la respiración y combustión',
                'atomic_number': 8,
                'group_number': 16,
                'period_number': 2,
                'state_at_stp': 'gas',
                'chemical_formula': 'O',
                'molecular_weight': 15.999,
                'hints_progressive': [
                    'Es un gas diatómico',
                    'Constituye el 21% del aire',
                    'Es necesario para la combustión',
                    'Forma agua con hidrógeno',
                    'Su símbolo es O'
                ]
            },
            {
                'word': 'CARBONO',
                'category': 'element',
                'difficulty': 'easy',
                'hint': 'Base de todos los compuestos orgánicos',
                'atomic_number': 6,
                'group_number': 14,
                'period_number': 2,
                'state_at_stp': 'solid',
                'chemical_formula': 'C',
                'molecular_weight': 12.011,
                'hints_progressive': [
                    'Forma cuatro enlaces covalentes',
                    'Puede formar cadenas largas',
                    'El diamante es una forma de este elemento',
                    'Es la base de la química orgánica',
                    'Su símbolo es C'
                ]
            },
            {
                'word': 'SODIO',
                'category': 'element',
                'difficulty': 'easy',
                'hint': 'Metal alcalino que reacciona violentamente con agua',
                'atomic_number': 11,
                'group_number': 1,
                'period_number': 3,
                'state_at_stp': 'solid',
                'chemical_formula': 'Na',
                'molecular_weight': 22.990,
                'hints_progressive': [
                    'Es un metal muy reactivo',
                    'Forma sal común con cloro',
                    'Su símbolo viene del latín',
                    'Es esencial para el funcionamiento nervioso',
                    'Su símbolo es Na'
                ]
            },
            {
                'word': 'CALCIO',
                'category': 'element',
                'difficulty': 'easy',
                'hint': 'Metal alcalinotérreo importante para huesos y dientes',
                'atomic_number': 20,
                'group_number': 2,
                'period_number': 4,
                'state_at_stp': 'solid',
                'chemical_formula': 'Ca',
                'molecular_weight': 40.078,
                'hints_progressive': [
                    'Es un metal alcalinotérreo',
                    'Es importante para los huesos',
                    'Se encuentra en la leche',
                    'Forma carbonato en piedra caliza',
                    'Su símbolo es Ca'
                ]
            },

            # ELEMENTOS - MEDIO
            {
                'word': 'CLORO',
                'category': 'element',
                'difficulty': 'medium',
                'hint': 'Halógeno usado para desinfectar agua',
                'atomic_number': 17,
                'group_number': 17,
                'period_number': 3,
                'state_at_stp': 'gas',
                'chemical_formula': 'Cl',
                'molecular_weight': 35.453,
                'hints_progressive': [
                    'Es un halógeno',
                    'Se usa para desinfectar piscinas',
                    'Forma sal común con sodio',
                    'Es un gas amarillo-verdoso',
                    'Su símbolo es Cl'
                ]
            },
            {
                'word': 'FOSFORO',
                'category': 'element',
                'difficulty': 'medium',
                'hint': 'No metal que brilla en la oscuridad en una de sus formas',
                'atomic_number': 15,
                'group_number': 15,
                'period_number': 3,
                'state_at_stp': 'solid',
                'chemical_formula': 'P',
                'molecular_weight': 30.974,
                'hints_progressive': [
                    'Tiene varias formas alotrópicas',
                    'El fósforo blanco es muy reactivo',
                    'Es esencial para el ADN y ATP',
                    'Se usa en fertilizantes',
                    'Su símbolo es P'
                ]
            },
            {
                'word': 'ALUMINIO',
                'category': 'element',
                'difficulty': 'medium',
                'hint': 'Metal ligero muy utilizado en aleaciones',
                'atomic_number': 13,
                'group_number': 13,
                'period_number': 3,
                'state_at_stp': 'solid',
                'chemical_formula': 'Al',
                'molecular_weight': 26.982,
                'hints_progressive': [
                    'Es el metal más abundante en la corteza terrestre',
                    'Se usa para hacer latas',
                    'Es muy ligero y resistente',
                    'Se obtiene de la bauxita',
                    'Su símbolo es Al'
                ]
            },

            # COMPUESTOS - FÁCIL
            {
                'word': 'AGUA',
                'category': 'compound',
                'difficulty': 'easy',
                'hint': 'Compuesto esencial para la vida, incoloro e insípido',
                'chemical_formula': 'H2O',
                'molecular_weight': 18.015,
                'state_at_stp': 'liquid',
                'hints_progressive': [
                    'Es el disolvente universal',
                    'Hierve a 100°C a presión normal',
                    'Se congela a 0°C',
                    'Está formada por hidrógeno y oxígeno',
                    'Su fórmula es H2O'
                ]
            },
            {
                'word': 'SAL',
                'category': 'compound',
                'difficulty': 'easy',
                'hint': 'Condimento común formado por sodio y cloro',
                'chemical_formula': 'NaCl',
                'molecular_weight': 58.443,
                'state_at_stp': 'solid',
                'hints_progressive': [
                    'Se usa para condimentar alimentos',
                    'Se obtiene del agua de mar',
                    'Es un compuesto iónico',
                    'Está formado por sodio y cloro',
                    'Su fórmula es NaCl'
                ]
            },
            {
                'word': 'METANO',
                'category': 'compound',
                'difficulty': 'easy',
                'hint': 'Hidrocarburo más simple, componente del gas natural',
                'chemical_formula': 'CH4',
                'molecular_weight': 16.043,
                'state_at_stp': 'gas',
                'hints_progressive': [
                    'Es un hidrocarburo',
                    'Tiene un átomo de carbono',
                    'Es el componente principal del gas natural',
                    'Se produce en la descomposición de materia orgánica',
                    'Su fórmula es CH4'
                ]
            },
            {
                'word': 'AMONIACO',
                'category': 'compound',
                'difficulty': 'medium',
                'hint': 'Compuesto de nitrógeno e hidrógeno, base fuerte',
                'chemical_formula': 'NH3',
                'molecular_weight': 17.031,
                'state_at_stp': 'gas',
                'hints_progressive': [
                    'Es un gas con olor característico',
                    'Se usa para hacer fertilizantes',
                    'Es una base de Lewis',
                    'Se sintetiza por el proceso Haber',
                    'Su fórmula es NH3'
                ]
            },

            # COMPUESTOS - MEDIO
            {
                'word': 'GLUCOSA',
                'category': 'compound',
                'difficulty': 'medium',
                'hint': 'Azúcar simple, fuente de energía para células',
                'chemical_formula': 'C6H12O6',
                'molecular_weight': 180.156,
                'state_at_stp': 'solid',
                'hints_progressive': [
                    'Es un monosacárido',
                    'Se produce en la fotosíntesis',
                    'Es la fuente principal de energía celular',
                    'Se encuentra en la miel y frutas',
                    'Su fórmula es C6H12O6'
                ]
            },
            {
                'word': 'ETANOL',
                'category': 'compound',
                'difficulty': 'medium',
                'hint': 'Alcohol presente en bebidas, también combustible',
                'chemical_formula': 'C2H5OH',
                'molecular_weight': 46.068,
                'state_at_stp': 'liquid',
                'hints_progressive': [
                    'Es un alcohol',
                    'Se produce por fermentación',
                    'Se usa como combustible',
                    'Está presente en bebidas alcohólicas',
                    'Su fórmula es C2H5OH'
                ]
            },
            {
                'word': 'ACETON',
                'category': 'compound',
                'difficulty': 'medium',
                'hint': 'Solvente orgánico usado en removedor de esmaltes',
                'chemical_formula': 'C3H6O',
                'molecular_weight': 58.079,
                'state_at_stp': 'liquid',
                'hints_progressive': [
                    'Es una cetona',
                    'Se usa como solvente',
                    'Es inflamable',
                    'Se encuentra en removedores de esmalte',
                    'Su fórmula es C3H6O'
                ]
            },

            # ELEMENTOS - DIFÍCIL
            {
                'word': 'CESIO',
                'category': 'element',
                'difficulty': 'hard',
                'hint': 'Metal alcalino más reactivo, usado en relojes atómicos',
                'atomic_number': 55,
                'group_number': 1,
                'period_number': 6,
                'state_at_stp': 'solid',
                'chemical_formula': 'Cs',
                'molecular_weight': 132.905,
                'hints_progressive': [
                    'Es el metal alcalino más pesado',
                    'Se usa en relojes atómicos',
                    'Es extremadamente reactivo',
                    'Se funde a temperatura ambiente en días calurosos',
                    'Su símbolo es Cs'
                ]
            },
            {
                'word': 'GALIO',
                'category': 'element',
                'difficulty': 'hard',
                'hint': 'Metal que se funde en la mano',
                'atomic_number': 31,
                'group_number': 13,
                'period_number': 4,
                'state_at_stp': 'solid',
                'chemical_formula': 'Ga',
                'molecular_weight': 69.723,
                'hints_progressive': [
                    'Se funde a temperatura corporal',
                    'Se usa en semiconductores',
                    'Fue predicho por Mendeleev',
                    'Se encuentra en pequeñas cantidades en zinc',
                    'Su símbolo es Ga'
                ]
            },
            {
                'word': 'RENIO',
                'category': 'element',
                'difficulty': 'hard',
                'hint': 'Uno de los metales más raros, punto de fusión muy alto',
                'atomic_number': 75,
                'group_number': 7,
                'period_number': 6,
                'state_at_stp': 'solid',
                'chemical_formula': 'Re',
                'molecular_weight': 186.207,
                'hints_progressive': [
                    'Es uno de los elementos más raros',
                    'Tiene punto de fusión muy alto',
                    'Se usa en aleaciones especiales',
                    'Fue el último elemento estable descubierto',
                    'Su símbolo es Re'
                ]
            },

            # COMPUESTOS - DIFÍCIL
            {
                'word': 'CAFEINA',
                'category': 'compound',
                'difficulty': 'hard',
                'hint': 'Alcaloide estimulante presente en café y té',
                'chemical_formula': 'C8H10N4O2',
                'molecular_weight': 194.19,
                'state_at_stp': 'solid',
                'hints_progressive': [
                    'Es un alcaloide',
                    'Actúa como estimulante del sistema nervioso',
                    'Se encuentra en el café y té',
                    'Es la droga psicoactiva más consumida',
                    'Su fórmula es C8H10N4O2'
                ]
            },
            {
                'word': 'ASPIRINA',
                'category': 'compound',
                'difficulty': 'hard',
                'hint': 'Medicamento antiinflamatorio, ácido acetilsalicílico',
                'chemical_formula': 'C9H8O4',
                'molecular_weight': 180.158,
                'state_at_stp': 'solid',
                'hints_progressive': [
                    'Es un medicamento analgésico',
                    'Se deriva del ácido salicílico',
                    'Se usa para prevenir infartos',
                    'Es un antiinflamatorio no esteroideo',
                    'Su fórmula es C9H8O4'
                ]
            },

            # IONES - MEDIO
            {
                'word': 'SULFATO',
                'category': 'ion',
                'difficulty': 'medium',
                'hint': 'Ion poliatómico con azufre y oxígeno, carga -2',
                'chemical_formula': 'SO4²⁻',
                'molecular_weight': 96.062,
                'hints_progressive': [
                    'Es un ion poliatómico',
                    'Contiene azufre y oxígeno',
                    'Tiene carga -2',
                    'Se encuentra en sales como el yeso',
                    'Su fórmula es SO4²⁻'
                ]
            },
            {
                'word': 'NITRATO',
                'category': 'ion',
                'difficulty': 'medium',
                'hint': 'Ion poliatómico usado en fertilizantes y explosivos',
                'chemical_formula': 'NO3⁻',
                'molecular_weight': 62.004,
                'hints_progressive': [
                    'Es un ion poliatómico',
                    'Contiene nitrógeno y oxígeno',
                    'Se usa en fertilizantes',
                    'Es importante en el ciclo del nitrógeno',
                    'Su fórmula es NO3⁻'
                ]
            },
            {
                'word': 'FOSFATO',
                'category': 'ion',
                'difficulty': 'medium',
                'hint': 'Ion esencial para ADN, ARN y ATP',
                'chemical_formula': 'PO4³⁻',
                'molecular_weight': 94.971,
                'hints_progressive': [
                    'Es un ion poliatómico',
                    'Es esencial para la vida',
                    'Se encuentra en ADN y ARN',
                    'Forma enlaces fosfodiéster',
                    'Su fórmula es PO4³⁻'
                ]
            },

            # MOLÉCULAS - FÁCIL A MEDIO
            {
                'word': 'OZONO',
                'category': 'molecule',
                'difficulty': 'medium',
                'hint': 'Molécula de tres átomos de oxígeno, protege de UV',
                'chemical_formula': 'O3',
                'molecular_weight': 47.998,
                'state_at_stp': 'gas',
                'hints_progressive': [
                    'Es una forma alotrópica del oxígeno',
                    'Protege de la radiación ultravioleta',
                    'Se encuentra en la estratosfera',
                    'Tiene un olor característico',
                    'Su fórmula es O3'
                ]
            },
            {
                'word': 'BENZENO',
                'category': 'molecule',
                'difficulty': 'hard',
                'hint': 'Hidrocarburo aromático con anillo de seis carbonos',
                'chemical_formula': 'C6H6',
                'molecular_weight': 78.114,
                'state_at_stp': 'liquid',
                'hints_progressive': [
                    'Es un hidrocarburo aromático',
                    'Tiene estructura de anillo',
                    'Es cancerígeno',
                    'Se usa como solvente industrial',
                    'Su fórmula es C6H6'
                ]
            }
        ]

        created_count = 0
        for word_data in words_data:
            word, created = ChemicalWord.objects.get_or_create(
                word=word_data['word'],
                defaults=word_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Creada: {word.word} ({word.category})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Ya existe: {word.word} ({word.category})')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Proceso completado: {created_count} palabras nuevas creadas')
        )
        self.stdout.write(
            self.style.SUCCESS(f'📊 Total de palabras en la base de datos: {ChemicalWord.objects.count()}')
        )
        
        # Mostrar estadísticas por categoría y dificultad
        self.stdout.write(self.style.SUCCESS('\n📈 Distribución por categoría:'))
        for category, name in ChemicalWord.CATEGORY_CHOICES:
            count = ChemicalWord.objects.filter(category=category).count()
            self.stdout.write(f'  {name}: {count} palabras')
        
        self.stdout.write(self.style.SUCCESS('\n📊 Distribución por dificultad:'))
        for difficulty, name in ChemicalWord.DIFFICULTY_CHOICES:
            count = ChemicalWord.objects.filter(difficulty=difficulty).count()
            self.stdout.write(f'  {name}: {count} palabras')