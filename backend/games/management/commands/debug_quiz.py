from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from games.models import QuizQuestion, QuizSession
from games.utils import QuizGameEngine

User = get_user_model()

class Command(BaseCommand):
    help = 'Debug quiz functionality'
    
    def handle(self, *args, **options):
        # Crear usuario de prueba si no existe
        user, created = User.objects.get_or_create(
            username='debug_user',
            defaults={'email': 'debug@example.com'}
        )
        if created:
            user.set_password('debug123')
            user.save()
            self.stdout.write('Usuario de debug creado')
        
        # Mostrar estadísticas de preguntas
        total_questions = QuizQuestion.objects.count()
        self.stdout.write(f'Total de preguntas: {total_questions}')
        
        by_difficulty = QuizQuestion.objects.values('difficulty').distinct()
        for diff in by_difficulty:
            count = QuizQuestion.objects.filter(difficulty=diff['difficulty']).count()
            self.stdout.write(f"  {diff['difficulty']}: {count} preguntas")
        
        by_category = QuizQuestion.objects.values('category').distinct()
        for cat in by_category:
            count = QuizQuestion.objects.filter(category=cat['category']).count()
            self.stdout.write(f"  {cat['category']}: {count} preguntas")
        
        # Probar crear sesión
        try:
            session = QuizGameEngine.create_quiz_session(user, total_questions=3)
            self.stdout.write(f'✓ Sesión creada: ID {session.id}')
            self.stdout.write(f'  Preguntas: {session.questions}')
            
            # Probar obtener pregunta actual
            current_q = QuizGameEngine.get_current_question(session)
            if current_q:
                self.stdout.write(f'✓ Pregunta actual: {current_q.question_text}')
                self.stdout.write(f'  Opciones: {current_q.options}')
                self.stdout.write(f'  Respuesta correcta: {current_q.correct_option}')
            else:
                self.stdout.write('✗ No se pudo obtener pregunta actual')
                
        except Exception as e:
            self.stdout.write(f'✗ Error al crear sesión: {e}')