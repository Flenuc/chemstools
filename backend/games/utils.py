import random
from django.utils import timezone
from .models import QuizQuestion, QuizSession, QuizAnswer, QuizLeaderboard

class QuizGameEngine:
    """Motor de juego para el quiz de química"""
    
    @staticmethod
    def create_quiz_session(user, difficulty=None, category=None, total_questions=10):
        """Crea una nueva sesión de quiz"""
        questions_query = QuizQuestion.objects.all()
        
        if difficulty:
            questions_query = questions_query.filter(difficulty=difficulty)
        if category:
            questions_query = questions_query.filter(category=category)
        
        # Verificar que hay preguntas disponibles
        total_available = questions_query.count()
        if total_available == 0:
            raise ValueError("No hay preguntas disponibles con los criterios especificados")
        
        # Ajustar el número de preguntas si es necesario
        if total_questions > total_available:
            total_questions = total_available
        
        # Seleccionar preguntas aleatorias
        all_question_ids = list(questions_query.values_list('id', flat=True))
        selected_questions = random.sample(all_question_ids, total_questions)
        
        session = QuizSession.objects.create(
            user=user,
            questions=selected_questions,
            total_questions=total_questions
        )
        
        return session
    
    @staticmethod
    def get_current_question(session):
        """Obtiene la pregunta actual de la sesión"""
        if session.current_question_index >= len(session.questions):
            return None
        
        question_id = session.questions[session.current_question_index]
        try:
            return QuizQuestion.objects.get(id=question_id)
        except QuizQuestion.DoesNotExist:
            return None
    
    @staticmethod
    def submit_answer(session, question_id, selected_option, time_taken):
        """Procesa una respuesta del usuario"""
        try:
            question = QuizQuestion.objects.get(id=question_id)
        except QuizQuestion.DoesNotExist:
            raise ValueError(f"Pregunta con ID {question_id} no encontrada")
        
        # Validar que selected_option es un índice válido
        if selected_option < 0 or selected_option >= len(question.options):
            # Manejar caso especial de tiempo agotado (-1)
            if selected_option == -1:
                is_correct = False
                points_earned = 0
                selected_option = -1  # Mantener -1 para indicar tiempo agotado
            else:
                raise ValueError(f"Opción seleccionada {selected_option} no es válida para la pregunta")
        else:
            is_correct = selected_option == question.correct_option
            points_earned = question.points if is_correct else 0
        
        # Crear la respuesta
        answer = QuizAnswer.objects.create(
            session=session,
            question=question,
            selected_option=selected_option,
            is_correct=is_correct,
            time_taken_seconds=time_taken,
            points_earned=points_earned
        )
        
        # Actualizar la sesión
        session.score += points_earned
        session.current_question_index += 1
        
        # Verificar si el quiz está completo
        if session.current_question_index >= session.total_questions:
            session.is_completed = True
            session.completed_at = timezone.now()
            QuizGameEngine._update_leaderboard(session)
        
        session.save()
        
        return answer
    
    @staticmethod
    def _update_leaderboard(session):
        """Actualiza la tabla de clasificación"""
        leaderboard, created = QuizLeaderboard.objects.get_or_create(
            user=session.user,
            defaults={
                'best_score': session.score,
                'total_games': 1,
                'average_score': float(session.score),
                'fastest_completion': (session.completed_at - session.started_at).seconds
            }
        )
        
        if not created:
            leaderboard.total_games += 1
            if session.score > leaderboard.best_score:
                leaderboard.best_score = session.score
            
            # Actualizar promedio (asegurar que sea float)
            leaderboard.average_score = float(
                (leaderboard.average_score * (leaderboard.total_games - 1) + session.score) / 
                leaderboard.total_games
            )
            
            # Actualizar tiempo más rápido
            completion_time = (session.completed_at - session.started_at).seconds
            if not leaderboard.fastest_completion or completion_time < leaderboard.fastest_completion:
                leaderboard.fastest_completion = completion_time
            
            leaderboard.save()