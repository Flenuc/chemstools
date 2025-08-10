from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import ( 
        QuizQuestion, QuizSession, QuizAnswer, QuizLeaderboard, 
        ChemicalWord, ChemWordleGame, ChemWordleAttempt, ChemWordleStats 
        , MemoryGame, MemoryStats,
        BalanceChallengeGame, BalanceChallengeAttempt, BalanceChallengeStats,)
from .serializers import (
    QuizQuestionSerializer, QuizSessionSerializer, QuizAnswerSerializer, 
    QuizLeaderboardSerializer, QuizQuestionWithAnswerSerializer,
    ChemicalWordSerializer, ChemWordleGameSerializer, ChemWordleGameCompleteSerializer,
    ChemWordleAttemptSerializer, ChemWordleStatsSerializer,
    MemoryCardRevealSerializer, MemoryGameSerializer, MemoryGameCreateSerializer, MemoryStatsSerializer,
    BalanceChallengeAttemptSerializer, BalanceChallengeGameSerializer, BalanceChallengeStatsSerializer, 
    BalanceChallengeCreateSerializer, BalanceChallengeSubmitSerializer, BalanceChallengeGameCompleteSerializer,
)
from .utils import QuizGameEngine
from .utils import ChemWordleEngine
from .utils import MemoryGameEngine
from .utils import BalanceChallengeEngine


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

class ChemWordleViewSet(viewsets.ViewSet):
    """ViewSet para el juego ChemWordle"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def start_game(self, request):
        """Inicia un nuevo juego o continúa uno existente"""
        try:
            difficulty = request.query_params.get('difficulty')
            game = ChemWordleEngine.get_daily_word(request.user, difficulty)
            
            # Usar serializer diferente si el juego está completado
            if game.is_completed:
                serializer = ChemWordleGameCompleteSerializer(game)
            else:
                serializer = ChemWordleGameSerializer(game)
            
            return Response({
                'success': True,
                'game': serializer.data,
                'message': 'Juego iniciado correctamente'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al iniciar juego: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def submit_guess(self, request):
        """Envía una adivinanza"""
        try:
            game_id = request.data.get('game_id')
            guess = request.data.get('guess')
            time_taken = request.data.get('time_taken', 0)
            
            if not all([game_id, guess]):
                return Response({
                    'success': False,
                    'error': 'Se requieren game_id y guess'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            game = ChemWordleGame.objects.get(id=game_id, user=request.user)
            
            if game.is_completed:
                return Response({
                    'success': False,
                    'error': 'El juego ya está completado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            attempt, error = ChemWordleEngine.submit_guess(game, guess, time_taken)
            if error:
                return Response({
                    'success': False,
                    'error': error
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Preparar respuesta
            attempt_serializer = ChemWordleAttemptSerializer(attempt)
            
            # Usar serializer completo si el juego terminó
            if game.is_completed:
                game_serializer = ChemWordleGameCompleteSerializer(game)
            else:
                game_serializer = ChemWordleGameSerializer(game)
            
            return Response({
                'success': True,
                'attempt': attempt_serializer.data,
                'game': game_serializer.data,
                'game_completed': game.is_completed,
                'game_won': game.is_won,
                'message': 'Intento procesado correctamente'
            })
            
        except ChemWordleGame.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Juego no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al procesar intento: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def get_hint(self, request):
        """Obtiene una pista progresiva"""
        try:
            game_id = request.data.get('game_id')
            hint_level = request.data.get('hint_level', 1)
            
            if not game_id:
                return Response({
                    'success': False,
                    'error': 'Se requiere game_id'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            game = ChemWordleGame.objects.get(id=game_id, user=request.user)
            
            if game.is_completed:
                return Response({
                    'success': False,
                    'error': 'No se pueden solicitar pistas para juegos completados'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            hint = ChemWordleEngine.get_progressive_hint(game, hint_level)
            
            # Actualizar pistas reveladas
            if hint_level not in game.hints_revealed:
                game.hints_revealed.append(hint_level)
                game.save()
            
            return Response({
                'success': True,
                'hint': hint,
                'hint_level': hint_level,
                'hints_revealed': game.hints_revealed
            })
            
        except ChemWordleGame.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Juego no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al obtener pista: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Obtiene estadísticas del usuario"""
        try:
            # CORRECCIÓN: Usar el modelo correcto
            stats, created = ChemWordleStats.objects.get_or_create(
                user=request.user,
                defaults={
                    'games_played': 0,
                    'games_won': 0,
                    'win_percentage': 0.0,
                    'current_streak': 0,
                    'max_streak': 0,
                    'win_distribution': {},
                    'best_time_seconds': None
                }
            )
            serializer = ChemWordleStatsSerializer(stats)
            
            return Response({
                'success': True,
                'stats': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al obtener estadísticas: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Obtiene tabla de clasificación global"""
        try:
            top_players = ChemWordleStats.objects.filter(
                games_played__gte=1  # Reducir mínimo para testing
            ).order_by('-win_percentage', '-games_won')[:10]
            
            leaderboard_data = []
            for i, stat in enumerate(top_players, 1):
                leaderboard_data.append({
                    'rank': i,
                    'username': stat.user.username,
                    'games_played': stat.games_played,
                    'games_won': stat.games_won,
                    'win_percentage': stat.win_percentage,
                    'current_streak': stat.current_streak,
                    'max_streak': stat.max_streak
                })
            
            return Response({
                'success': True,
                'leaderboard': leaderboard_data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al obtener clasificación: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
            
class MemoryGameViewSet(viewsets.ViewSet):
    """ViewSet para el juego Memory Molecular"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def start_game(self, request):
        """Inicia una nueva partida de Memory Molecular"""
        try:
            serializer = MemoryGameCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Datos inválidos',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            difficulty = serializer.validated_data['difficulty']
            total_pairs = serializer.validated_data['total_pairs']
            
            # Verificar si hay una partida activa
            active_game = MemoryGame.objects.filter(
                user=request.user,
                is_completed=False
            ).first()
            
            if active_game:
                game_serializer = MemoryGameSerializer(active_game)
                return Response({
                    'success': True,
                    'game': game_serializer.data,
                    'message': 'Continuando partida existente'
                })
            
            # Crear nueva partida
            game = MemoryGameEngine.create_memory_game(
                user=request.user,
                difficulty=difficulty,
                total_pairs=total_pairs
            )
            
            game_serializer = MemoryGameSerializer(game)
            return Response({
                'success': True,
                'game': game_serializer.data,
                'message': 'Nueva partida de Memory Molecular iniciada'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al iniciar partida: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def reveal_card(self, request):
        """Revela una carta del tablero"""
        try:
            serializer = MemoryCardRevealSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Datos inválidos',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            game_id = serializer.validated_data['game_id']
            card_position = serializer.validated_data['card_position']
            
            game = MemoryGame.objects.get(id=game_id, user=request.user)
            
            if game.is_completed:
                return Response({
                    'success': False,
                    'error': 'La partida ya está completada'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            result, error = MemoryGameEngine.reveal_card(game, card_position)
            
            if error:
                return Response({
                    'success': False,
                    'error': error
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener estado actualizado del juego
            game.refresh_from_db()
            game_serializer = MemoryGameSerializer(game)
            
            response_data = {
                'success': True,
                'result': result,
                'game': game_serializer.data,
                'message': 'Carta revelada correctamente'
            }
            
            # Mensajes específicos según el resultado
            if result['is_match']:
                response_data['message'] = '¡Excelente! Has encontrado un par'
                if result['game_completed']:
                    response_data['message'] = '¡Felicitaciones! Has completado el juego'
            
            return Response(response_data)
            
        except MemoryGame.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Partida no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al revelar carta: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def hide_cards(self, request):
        """Oculta cartas reveladas que no fueron emparejadas"""
        try:
            game_id = request.data.get('game_id')
            if not game_id:
                return Response({
                    'success': False,
                    'error': 'Se requiere game_id'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            game = MemoryGame.objects.get(id=game_id, user=request.user)
            
            if game.is_completed:
                return Response({
                    'success': False,
                    'error': 'La partida ya está completada'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            MemoryGameEngine.hide_revealed_cards(game)
            
            game.refresh_from_db()
            game_serializer = MemoryGameSerializer(game)
            
            return Response({
                'success': True,
                'game': game_serializer.data,
                'message': 'Cartas ocultadas correctamente'
            })
            
        except MemoryGame.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Partida no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al ocultar cartas: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def current_game(self, request):
        """Obtiene la partida actual del usuario"""
        try:
            game = MemoryGame.objects.filter(
                user=request.user,
                is_completed=False
            ).first()
            
            if not game:
                return Response({
                    'success': True,
                    'game': None,
                    'message': 'No hay partida activa'
                })
            
            game_serializer = MemoryGameSerializer(game)
            return Response({
                'success': True,
                'game': game_serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al obtener partida: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Obtiene estadísticas del usuario"""
        try:
            stats, created = MemoryStats.objects.get_or_create(
                user=request.user,
                defaults={
                    'games_played': 0,
                    'games_completed': 0,
                    'completion_rate': 0.0,
                    'total_pairs_found': 0,
                    'total_attempts': 0,
                    'average_accuracy': 0.0
                }
            )
            
            serializer = MemoryStatsSerializer(stats)
            return Response({
                'success': True,
                'stats': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al obtener estadísticas: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Obtiene tabla de clasificación de Memory Molecular"""
        try:
            # Top jugadores por tasa de finalización y precisión
            top_players = MemoryStats.objects.filter(
                games_played__gte=3  # Mínimo 3 partidas
            ).order_by('-completion_rate', '-average_accuracy')[:10]
            
            leaderboard_data = []
            for i, stat in enumerate(top_players, 1):
                # Calcular mejor tiempo general
                best_times = [stat.best_time_easy, stat.best_time_medium, stat.best_time_hard]
                best_overall = min([t for t in best_times if t is not None], default=None)
                
                leaderboard_data.append({
                    'rank': i,
                    'username': stat.user.username,
                    'games_played': stat.games_played,
                    'completion_rate': round(stat.completion_rate, 1),
                    'average_accuracy': round(stat.average_accuracy, 1),
                    'best_time_overall': best_overall,
                    'total_pairs_found': stat.total_pairs_found
                })
            
            return Response({
                'success': True,
                'leaderboard': leaderboard_data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al obtener clasificación: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'])
    def end_game(self, request):
        """Termina la partida actual (abandonar)"""
        try:
            game = MemoryGame.objects.filter(
                user=request.user,
                is_completed=False
            ).first()
            
            if not game:
                return Response({
                    'success': False,
                    'error': 'No hay partida activa para terminar'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Marcar como completada sin actualizar estadísticas de victoria
            game.is_completed = True
            game.completed_at = timezone.now()
            game.total_time_seconds = (game.completed_at - game.started_at).seconds
            game.save()
            
            # Actualizar solo estadísticas de partidas jugadas
            stats, created = MemoryStats.objects.get_or_create(
                user=request.user,
                defaults={'games_played': 0}
            )
            stats.games_played += 1
            stats.completion_rate = (stats.games_completed / stats.games_played) * 100
            stats.save()
            
            return Response({
                'success': True,
                'message': 'Partida terminada'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al terminar partida: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
            
class BalanceChallengeViewSet(viewsets.ViewSet):
    """ViewSet para el desafío de balanceo de ecuaciones"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def start_challenge(self, request):
        """Inicia un nuevo desafío de balanceo"""
        try:
            serializer = BalanceChallengeCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Datos inválidos',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            difficulty = serializer.validated_data['difficulty']
            
            # Verificar si hay un juego activo
            active_game = BalanceChallengeGame.objects.filter(
                user=request.user,
                is_completed=False
            ).first()
            
            if active_game:
                game_serializer = BalanceChallengeGameSerializer(active_game)
                return Response({
                    'success': True,
                    'game': game_serializer.data,
                    'message': 'Continuando desafío existente'
                })
            
            # Crear nuevo desafío
            from .utils import BalanceChallengeEngine
            game = BalanceChallengeEngine.create_balance_challenge(
                user=request.user,
                difficulty=difficulty
            )
            
            game_serializer = BalanceChallengeGameSerializer(game)
            return Response({
                'success': True,
                'game': game_serializer.data,
                'message': 'Nuevo desafío de balanceo iniciado'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al iniciar desafío: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def submit_coefficients(self, request):
        """Envía coeficientes para validación"""
        try:
            serializer = BalanceChallengeSubmitSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Datos inválidos',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            game_id = serializer.validated_data['game_id']
            coefficients = serializer.validated_data['coefficients']
            time_taken = serializer.validated_data['time_taken']
            
            game = BalanceChallengeGame.objects.get(id=game_id, user=request.user)
            
            from .utils import BalanceChallengeEngine
            attempt, error = BalanceChallengeEngine.submit_attempt(
                game, coefficients, time_taken
            )
            
            if error:
                return Response({
                    'success': False,
                    'error': error
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Preparar respuesta
            attempt_serializer = BalanceChallengeAttemptSerializer(attempt)
            
            # Usar serializer completo si el juego terminó
            if game.is_completed:
                game_serializer = BalanceChallengeGameCompleteSerializer(game)
            else:
                game_serializer = BalanceChallengeGameSerializer(game)
            
            return Response({
                'success': True,
                'attempt': attempt_serializer.data,
                'game': game_serializer.data,
                'game_completed': game.is_completed,
                'is_correct': attempt.is_correct,
                'validation_result': attempt.validation_result,
                'message': 'Intento procesado correctamente'
            })
            
        except BalanceChallengeGame.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Desafío no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al procesar intento: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def get_hint(self, request):
        """Obtiene una pista"""
        try:
            game_id = request.data.get('game_id')
            hint_type = request.data.get('hint_type', 'element')
            
            if not game_id:
                return Response({
                    'success': False,
                    'error': 'Se requiere game_id'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            game = BalanceChallengeGame.objects.get(id=game_id, user=request.user)
            
            from .utils import BalanceChallengeEngine
            hint, error = BalanceChallengeEngine.get_hint(game, hint_type)
            
            if error:
                return Response({
                    'success': False,
                    'error': error
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'success': True,
                'hint': hint,
                'hint_type': hint_type,
                'hints_used': game.hints_used
            })
            
        except BalanceChallengeGame.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Desafío no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al obtener pista: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def current_challenge(self, request):
        """Obtiene el desafío actual del usuario"""
        try:
            game = BalanceChallengeGame.objects.filter(
                user=request.user,
                is_completed=False
            ).first()
            
            if not game:
                return Response({
                    'success': True,
                    'game': None,
                    'message': 'No hay desafío activo'
                })
            
            game_serializer = BalanceChallengeGameSerializer(game)
            return Response({
                'success': True,
                'game': game_serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al obtener desafío: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Obtiene estadísticas del usuario"""
        try:
            stats, created = BalanceChallengeStats.objects.get_or_create(
                user=request.user,
                defaults={
                    'games_played': 0,
                    'games_completed': 0,
                    'games_correct': 0,
                    'completion_rate': 0.0,
                    'accuracy_rate': 0.0,
                    'average_time_per_game': 0.0,
                    'current_streak': 0,
                    'best_streak': 0
                }
            )
            
            serializer = BalanceChallengeStatsSerializer(stats)
            return Response({
                'success': True,
                'stats': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al obtener estadísticas: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Obtiene tabla de clasificación"""
        try:
            # Top jugadores por tasa de precisión y racha
            top_players = BalanceChallengeStats.objects.filter(
                games_completed__gte=3  # Mínimo 3 juegos completados
            ).order_by('-accuracy_rate', '-best_streak', '-games_correct')[:10]
            
            leaderboard_data = []
            for i, stat in enumerate(top_players, 1):
                leaderboard_data.append({
                    'rank': i,
                    'username': stat.user.username,
                    'games_played': stat.games_played,
                    'games_correct': stat.games_correct,
                    'accuracy_rate': round(stat.accuracy_rate, 1),
                    'best_streak': stat.best_streak,
                    'current_streak': stat.current_streak,
                    'average_time': round(stat.average_time_per_game, 1) if stat.average_time_per_game else 0
                })
            
            return Response({
                'success': True,
                'leaderboard': leaderboard_data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al obtener clasificación: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'])
    def end_challenge(self, request):
        """Termina el desafío actual (abandonar)"""
        try:
            game = BalanceChallengeGame.objects.filter(
                user=request.user,
                is_completed=False
            ).first()
            
            if not game:
                return Response({
                    'success': False,
                    'error': 'No hay desafío activo para terminar'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Marcar como completado sin ser correcto
            game.is_completed = True
            game.completed_at = timezone.now()
            game.time_spent_seconds = (game.completed_at - game.started_at).seconds
            game.save()
            
            # Actualizar estadísticas básicas
            from .utils import BalanceChallengeEngine
            BalanceChallengeEngine._update_stats(game)
            
            return Response({
                'success': True,
                'message': 'Desafío terminado'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al terminar desafío: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)