import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import json
from games.models import QuizQuestion, QuizSession
from games.utils import QuizGameEngine

User = get_user_model()

class QuizAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Crear preguntas de ejemplo
        self.question1 = QuizQuestion.objects.create(
            question_text="¿Cuál es el símbolo del hidrógeno?",
            options=["H", "He", "Hi", "Hy"],
            correct_option=0,
            category="periodic_table",
            difficulty="easy",
            points=10,
            explanation="El hidrógeno es el primer elemento."
        )
        
        self.question2 = QuizQuestion.objects.create(
            question_text="¿Cuántos electrones tiene el carbono?",
            options=["4", "6", "12", "14"],
            correct_option=1,
            category="atomic_structure",
            difficulty="medium",
            points=15,
            explanation="El carbono tiene número atómico 6."
        )
        
        self.question3 = QuizQuestion.objects.create(
            question_text="¿Cuál es el símbolo del oxígeno?",
            options=["O", "Ox", "O2", "Og"],
            correct_option=0,
            category="periodic_table",
            difficulty="easy",
            points=10,
            explanation="El oxígeno tiene símbolo O."
        )
    
    def test_start_quiz_session(self):
        """Probar inicio de sesión de quiz"""
        response = self.client.post('/api/games/quiz/start_session/', {
            'difficulty': 'easy',
            'total_questions': 2
        }, format='json')
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('session', response.data)
        self.assertEqual(response.data['session']['total_questions'], 2)
    
    def test_get_current_question(self):
        """Probar obtención de pregunta actual"""
        session = QuizGameEngine.create_quiz_session(self.user, total_questions=2)
        
        response = self.client.get(f'/api/games/quiz/get_question/?session_id={session.id}')
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('question', response.data)
    
    def test_submit_correct_answer(self):
        """Probar envío de respuesta correcta"""
        session = QuizGameEngine.create_quiz_session(self.user, total_questions=1)
        current_question = QuizGameEngine.get_current_question(session)
        
        print(f"Session ID: {session.id}")
        print(f"Question ID: {current_question.id}")
        print(f"Correct option: {current_question.correct_option}")
        print(f"Session questions: {session.questions}")
        
        response = self.client.post('/api/games/quiz/submit_answer/', {
            'session_id': session.id,
            'question_id': current_question.id,
            'selected_option': current_question.correct_option,
            'time_taken': 30
        }, format='json')
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertTrue(response.data['answer']['is_correct'])
        self.assertEqual(response.data['answer']['points_earned'], current_question.points)
    
    def test_submit_wrong_answer(self):
        """Probar envío de respuesta incorrecta"""
        session = QuizGameEngine.create_quiz_session(self.user, total_questions=1)
        current_question = QuizGameEngine.get_current_question(session)
        wrong_option = (current_question.correct_option + 1) % len(current_question.options)
        
        response = self.client.post('/api/games/quiz/submit_answer/', {
            'session_id': session.id,
            'question_id': current_question.id,
            'selected_option': wrong_option,
            'time_taken': 45
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(response.data['answer']['is_correct'])
        self.assertEqual(response.data['answer']['points_earned'], 0)
    
    def test_leaderboard_access(self):
        """Probar acceso a tabla de clasificación"""
        response = self.client.get('/api/games/quiz/leaderboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('leaderboard', response.data)
    
    def test_user_stats(self):
        """Probar estadísticas del usuario"""
        response = self.client.get('/api/games/quiz/my_stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_start_quiz_with_no_questions(self):
        """Probar iniciar quiz sin preguntas disponibles"""
        # Eliminar todas las preguntas
        QuizQuestion.objects.all().delete()
        
        response = self.client.post('/api/games/quiz/start_session/', {
            'difficulty': 'easy',
            'total_questions': 2
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_submit_answer_with_invalid_session(self):
        """Probar envío de respuesta con sesión inválida"""
        response = self.client.post('/api/games/quiz/submit_answer/', {
            'session_id': 99999,
            'question_id': self.question1.id,
            'selected_option': 0,
            'time_taken': 30
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
