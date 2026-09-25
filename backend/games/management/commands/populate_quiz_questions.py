from django.core.management.base import BaseCommand
from games.models import QuizQuestion

class Command(BaseCommand):
    help = 'Populate the database with sample quiz questions'

    def handle(self, *args, **options):
        questions_data = [
            # Tabla Periódica - Fácil
            {
                'question_text': '¿Cuál es el símbolo químico del hidrógeno?',
                'options': ['H', 'He', 'Hi', 'Hy'],
                'correct_option': 0,
                'explanation': 'El hidrógeno es el primer elemento de la tabla periódica y su símbolo es H.',
                'difficulty': 'easy',
                'category': 'periodic_table',
                'points': 10
            },
            {
                'question_text': '¿Cuál es el elemento más abundante en el universo?',
                'options': ['Oxígeno', 'Carbono', 'Hidrógeno', 'Helio'],
                'correct_option': 2,
                'explanation': 'El hidrógeno constituye aproximadamente el 75% de la masa total del universo.',
                'difficulty': 'easy',
                'category': 'periodic_table',
                'points': 10
            },
            {
                'question_text': '¿Cuántos grupos tiene la tabla periódica moderna?',
                'options': ['16', '17', '18', '19'],
                'correct_option': 2,
                'explanation': 'La tabla periódica moderna está organizada en 18 grupos (columnas verticales).',
                'difficulty': 'easy',
                'category': 'periodic_table',
                'points': 10
            },

            # Estructura Atómica - Medio
            {
                'question_text': '¿Cuántos electrones tiene el átomo de carbono en su estado neutro?',
                'options': ['4', '6', '8', '12'],
                'correct_option': 1,
                'explanation': 'El carbono tiene número atómico 6, por lo que tiene 6 protones y 6 electrones en estado neutro.',
                'difficulty': 'medium',
                'category': 'atomic_structure',
                'points': 15
            },
            {
                'question_text': '¿Cuál es la configuración electrónica del neón (Ne)?',
                'options': ['1s² 2s² 2p⁶', '1s² 2s² 2p⁴', '1s² 2s² 2p⁵', '1s² 2s¹ 2p⁷'],
                'correct_option': 0,
                'explanation': 'El neón tiene 10 electrones: 2 en 1s, 2 en 2s y 6 en 2p, completando el segundo nivel.',
                'difficulty': 'medium',
                'category': 'atomic_structure',
                'points': 15
            },
            {
                'question_text': '¿Qué partícula subatómica determina el número atómico?',
                'options': ['Neutrones', 'Electrones', 'Protones', 'Quarks'],
                'correct_option': 2,
                'explanation': 'El número atómico está determinado por la cantidad de protones en el núcleo.',
                'difficulty': 'medium',
                'category': 'atomic_structure',
                'points': 15
            },

            # Nomenclatura - Medio
            {
                'question_text': '¿Cuál es el nombre del compuesto H₂SO₄?',
                'options': ['Ácido sulfúrico', 'Ácido sulfhídrico', 'Sulfato de hidrógeno', 'Ácido sulfuroso'],
                'correct_option': 0,
                'explanation': 'H₂SO₄ es el ácido sulfúrico, un ácido fuerte muy común en la industria.',
                'difficulty': 'medium',
                'category': 'nomenclature',
                'points': 15
            },
            {
                'question_text': '¿Cuál es la fórmula del cloruro de sodio?',
                'options': ['NaCl₂', 'Na₂Cl', 'NaCl', 'NaClO'],
                'correct_option': 2,
                'explanation': 'El cloruro de sodio (sal común) tiene la fórmula NaCl: un átomo de sodio y uno de cloro.',
                'difficulty': 'easy',
                'category': 'nomenclature',
                'points': 10
            },
            {
                'question_text': '¿Cómo se llama el compuesto Ca(OH)₂?',
                'options': ['Óxido de calcio', 'Hidróxido de calcio', 'Carbonato de calcio', 'Sulfato de calcio'],
                'correct_option': 1,
                'explanation': 'Ca(OH)₂ es hidróxido de calcio, también conocido como cal apagada.',
                'difficulty': 'medium',
                'category': 'nomenclature',
                'points': 15
            },

            # Reacciones Químicas - Medio/Difícil
            {
                'question_text': '¿Cuál es el producto principal de la combustión completa del metano (CH₄)?',
                'options': ['CO + H₂O', 'CO₂ + H₂O', 'C + H₂O₂', 'CH₃OH + O₂'],
                'correct_option': 1,
                'explanation': 'La combustión completa del metano produce dióxido de carbono y agua: CH₄ + 2O₂ → CO₂ + 2H₂O',
                'difficulty': 'medium',
                'category': 'reactions',
                'points': 15
            },
            {
                'question_text': '¿Qué tipo de reacción es 2H₂ + O₂ → 2H₂O?',
                'options': ['Descomposición', 'Síntesis', 'Sustitución simple', 'Doble sustitución'],
                'correct_option': 1,
                'explanation': 'Es una reacción de síntesis porque dos elementos simples se combinan para formar un compuesto.',
                'difficulty': 'medium',
                'category': 'reactions',
                'points': 15
            },
            {
                'question_text': 'En la ecuación Zn + HCl → ZnCl₂ + H₂, ¿cuál es el coeficiente del HCl?',
                'options': ['1', '2', '3', '4'],
                'correct_option': 1,
                'explanation': 'La ecuación balanceada es: Zn + 2HCl → ZnCl₂ + H₂',
                'difficulty': 'hard',
                'category': 'reactions',
                'points': 20
            },

            # Disoluciones - Medio
            {
                'question_text': '¿Qué es la molaridad de una disolución?',
                'options': ['Gramos de soluto por litro', 'Moles de soluto por litro', 'Gramos por 100 mL', 'Moles por kilogramo'],
                'correct_option': 1,
                'explanation': 'La molaridad se define como moles de soluto por litro de disolución.',
                'difficulty': 'medium',
                'category': 'solutions',
                'points': 15
            },
            {
                'question_text': '¿Cuál es la concentración en % m/v de una disolución que contiene 25 g de NaCl en 500 mL?',
                'options': ['5%', '10%', '15%', '20%'],
                'correct_option': 0,
                'explanation': '% m/v = (25 g / 500 mL) × 100 = 5%',
                'difficulty': 'medium',
                'category': 'solutions',
                'points': 15
            },
            {
                'question_text': '¿Qué ocurre cuando se diluye una disolución?',
                'options': ['Aumenta la concentración', 'Disminuye la concentración', 'No cambia la concentración', 'Cambia el soluto'],
                'correct_option': 1,
                'explanation': 'Al añadir más disolvente, la concentración disminuye porque hay la misma cantidad de soluto en mayor volumen.',
                'difficulty': 'easy',
                'category': 'solutions',
                'points': 10
            },

            # Cálculos de pH - Medio/Difícil
            {
                'question_text': '¿Cuál es el pH de una disolución con [H⁺] = 1×10⁻³ M?',
                'options': ['3', '11', '7', '14'],
                'correct_option': 0,
                'explanation': 'pH = -log[H⁺] = -log(1×10⁻³) = 3',
                'difficulty': 'medium',
                'category': 'ph_calculations',
                'points': 15
            },
            {
                'question_text': '¿Qué caracteriza a una disolución con pH = 7?',
                'options': ['Es ácida', 'Es básica', 'Es neutra', 'Es salina'],
                'correct_option': 2,
                'explanation': 'pH = 7 indica que [H⁺] = [OH⁻], lo que caracteriza una disolución neutra.',
                'difficulty': 'easy',
                'category': 'ph_calculations',
                'points': 10
            },
            {
                'question_text': 'Si pH + pOH = 14, ¿cuál es el pOH de una disolución con pH = 9?',
                'options': ['5', '6', '7', '9'],
                'correct_option': 0,
                'explanation': 'pOH = 14 - pH = 14 - 9 = 5',
                'difficulty': 'medium',
                'category': 'ph_calculations',
                'points': 15
            },

            # Estructuras de Lewis - Difícil
            {
                'question_text': '¿Cuántos pares de electrones libres tiene el amoníaco (NH₃)?',
                'options': ['0', '1', '2', '3'],
                'correct_option': 1,
                'explanation': 'El nitrógeno en NH₃ tiene 5 electrones de valencia: 3 forman enlaces y 2 quedan como par libre.',
                'difficulty': 'hard',
                'category': 'lewis_structures',
                'points': 20
            },
            {
                'question_text': '¿Qué tipo de enlace se forma entre Na y Cl en NaCl?',
                'options': ['Covalente polar', 'Covalente no polar', 'Iónico', 'Metálico'],
                'correct_option': 2,
                'explanation': 'La gran diferencia de electronegatividad entre Na y Cl resulta en un enlace iónico.',
                'difficulty': 'medium',
                'category': 'lewis_structures',
                'points': 15
            },
            {
                'question_text': '¿Cuál es la geometría molecular del agua (H₂O)?',
                'options': ['Lineal', 'Angular', 'Triangular', 'Tetraédrica'],
                'correct_option': 1,
                'explanation': 'El agua tiene geometría angular debido a los dos pares libres del oxígeno que repelen los enlaces O-H.',
                'difficulty': 'hard',
                'category': 'lewis_structures',
                'points': 20
            },

            # Preguntas adicionales variadas
            {
                'question_text': '¿Cuál es la masa molar aproximada del CO₂?',
                'options': ['28 g/mol', '32 g/mol', '44 g/mol', '48 g/mol'],
                'correct_option': 2,
                'explanation': 'CO₂: C (12) + 2×O (16) = 12 + 32 = 44 g/mol',
                'difficulty': 'medium',
                'category': 'atomic_structure',
                'points': 15
            },
            {
                'question_text': '¿Cuál es el gas noble del tercer período?',
                'options': ['Helio', 'Neón', 'Argón', 'Kriptón'],
                'correct_option': 2,
                'explanation': 'El argón (Ar) es el gas noble que cierra el tercer período de la tabla periódica.',
                'difficulty': 'medium',
                'category': 'periodic_table',
                'points': 15
            },
            {
                'question_text': '¿Cómo se llama el proceso de paso directo de sólido a gas?',
                'options': ['Evaporación', 'Condensación', 'Sublimación', 'Fusión'],
                'correct_option': 2,
                'explanation': 'La sublimación es el cambio de estado directo de sólido a gas sin pasar por líquido.',
                'difficulty': 'easy',
                'category': 'periodic_table',
                'points': 10
            },
            {
                'question_text': '¿Cuál es la fórmula del ácido nítrico?',
                'options': ['HNO₂', 'HNO₃', 'H₂NO₃', 'HN₃'],
                'correct_option': 1,
                'explanation': 'El ácido nítrico tiene la fórmula HNO₃ y es un ácido fuerte muy utilizado en la industria.',
                'difficulty': 'medium',
                'category': 'nomenclature',
                'points': 15
            },
            {
                'question_text': '¿Qué elemento tiene la configuración electrónica [Ne] 3s¹?',
                'options': ['Magnesio', 'Sodio', 'Aluminio', 'Silicio'],
                'correct_option': 1,
                'explanation': 'El sodio (Na) tiene 11 electrones: 10 como el neón más 1 en el orbital 3s.',
                'difficulty': 'hard',
                'category': 'atomic_structure',
                'points': 20
            },
            {
                'question_text': '¿Cuál es el producto de la reacción: CaCO₃ + calor →?',
                'options': ['CaO + CO₂', 'Ca + CO₃', 'CaC + O₃', 'Ca₂O + CO'],
                'correct_option': 0,
                'explanation': 'La descomposición térmica del carbonato de calcio produce óxido de calcio y dióxido de carbono.',
                'difficulty': 'medium',
                'category': 'reactions',
                'points': 15
            },
            {
                'question_text': '¿Cuántos átomos hay en una molécula de glucosa (C₆H₁₂O₆)?',
                'options': ['18', '24', '30', '36'],
                'correct_option': 1,
                'explanation': 'C₆H₁₂O₆ tiene 6 + 12 + 6 = 24 átomos en total.',
                'difficulty': 'easy',
                'category': 'atomic_structure',
                'points': 10
            },
            {
                'question_text': '¿Qué indica el número de oxidación?',
                'options': ['El número de neutrones', 'La carga aparente del átomo', 'El número de protones', 'La masa atómica'],
                'correct_option': 1,
                'explanation': 'El número de oxidación indica la carga aparente que tendría un átomo si todos los enlaces fueran iónicos.',
                'difficulty': 'medium',
                'category': 'nomenclature',
                'points': 15
            }
        ]

        created_count = 0
        for question_data in questions_data:
            question, created = QuizQuestion.objects.get_or_create(
                question_text=question_data['question_text'],
                defaults=question_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Creada: {question.question_text[:50]}...')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Ya existe: {question.question_text[:50]}...')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Proceso completado: {created_count} preguntas nuevas creadas')
        )
        self.stdout.write(
            self.style.SUCCESS(f'📊 Total de preguntas en la base de datos: {QuizQuestion.objects.count()}')
        )