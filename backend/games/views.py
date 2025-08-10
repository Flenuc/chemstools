from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import QuizQuestion, QuizSession, QuizAnswer, QuizLeaderboard
from .serializers import (
    QuizQuestionSerializer, QuizSessionSerializer, QuizAnswerSerializer, 
    QuizLeaderboardSerializer, QuizQuestionWithAnswerSerializer
)
from .utils import QuizGameEngine

class QuizViewSet(viewsets.ViewSet):
    """ViewSet para el sistema de quiz"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def start_session(self, request):
        """Iniciar una nueva sesión de quiz"""
        difficulty = request.data.get('difficulty')
        category = request.data.get('category')
        total_questions = request.data.get('total_questions', 10)
        
        try:
            # Verificar que hay suficientes preguntas disponibles
            questions_query = QuizQuestion.objects.all()
            
            if difficulty:
                questions_query = questions_query.filter(difficulty=difficulty)
            if category:
                questions_query = questions_query.filter(category=category)
            
            available_count = questions_query.count()
            if available_count == 0:
                return Response({
                    'success': False,
                    'error': 'No hay preguntas disponibles con los criterios especificados'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Ajustar total_questions si es necesario
            if total_questions > available_count:
                total_questions = available_count
            
            session = QuizGameEngine.create_quiz_session(
                user=request.user,
                difficulty=difficulty,
                category=category,
                total_questions=total_questions
            )
            
            serializer = QuizSessionSerializer(session)
            return Response({
                'success': True,
                'session': serializer.data,
                'message': 'Sesión de quiz iniciada correctamente'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al iniciar sesión: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def get_question(self, request):
        """Obtener la pregunta actual de la sesión activa"""
        try:
            session_id = request.query_params.get('session_id')
            if not session_id:
                return Response({
                    'success': False,
                    'error': 'Se requiere session_id'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            session = QuizSession.objects.get(id=session_id, user=request.user)
            
            if session.is_completed:
                return Response({
                    'success': False,
                    'error': 'La sesión ya está completada'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            question = QuizGameEngine.get_current_question(session)
            if not question:
                return Response({
                    'success': False,
                    'error': 'No hay más preguntas'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = QuizQuestionSerializer(question)
            return Response({
                'success': True,
                'question': serializer.data,
                'current_index': session.current_question_index,
                'total_questions': session.total_questions,
                'current_score': session.score
            })
            
        except QuizSession.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Sesión no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def submit_answer(self, request):
        """Enviar una respuesta"""
        try:
            session_id = request.data.get('session_id')
            question_id = request.data.get('question_id')
            selected_option = request.data.get('selected_option')
            time_taken = request.data.get('time_taken', 0)
            
            # Validar datos requeridos
            if not all([session_id, question_id is not None, selected_option is not None]):
                return Response({
                    'success': False,
                    'error': 'Faltan datos requeridos (session_id, question_id, selected_option)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            session = QuizSession.objects.get(id=session_id, user=request.user)
            
            if session.is_completed:
                return Response({
                    'success': False,
                    'error': 'La sesión ya está completada'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar que la pregunta pertenece a la sesión actual
            current_question = QuizGameEngine.get_current_question(session)
            if not current_question or current_question.id != int(question_id):
                return Response({
                    'success': False,
                    'error': 'Pregunta no válida para la sesión actual'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            answer = QuizGameEngine.submit_answer(
                session=session,
                question_id=question_id,
                selected_option=selected_option,
                time_taken=time_taken
            )
            
            serializer = QuizAnswerSerializer(answer)
            return Response({
                'success': True,
                'answer': serializer.data,
                'session_completed': session.is_completed,
                'final_score': session.score if session.is_completed else None,
                'message': 'Respuesta procesada correctamente'
            })
            
        except QuizSession.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Sesión no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al procesar respuesta: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Obtener tabla de clasificación"""
        leaderboard = QuizLeaderboard.objects.all()[:10]  # Top 10
        serializer = QuizLeaderboardSerializer(leaderboard, many=True)
        
        return Response({
            'success': True,
            'leaderboard': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def my_stats(self, request):
        """Obtener estadísticas del usuario actual"""
        try:
            leaderboard = QuizLeaderboard.objects.get(user=request.user)
            serializer = QuizLeaderboardSerializer(leaderboard)
            
            return Response({
                'success': True,
                'stats': serializer.data
            })
        except QuizLeaderboard.DoesNotExist:
            return Response({
                'success': True,
                'stats': None,
                'message': 'No hay estadísticas disponibles'
            })
