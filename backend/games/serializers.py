from rest_framework import serializers
from .models import QuizQuestion, QuizSession, QuizAnswer, QuizLeaderboard
from .models import ChemicalWord, ChemWordleGame, ChemWordleAttempt, ChemWordleStats
from .models import MemoryGame, MemoryStats
from django.utils import timezone

class QuizQuestionSerializer(serializers.ModelSerializer):
    """Serializer para preguntas sin mostrar la respuesta correcta"""
    class Meta:
        model = QuizQuestion
        fields = ['id', 'question_text', 'options', 'difficulty', 'category', 'points']

class QuizQuestionWithAnswerSerializer(serializers.ModelSerializer):
    """Serializer completo para mostrar después de responder"""
    class Meta:
        model = QuizQuestion
        fields = '__all__'

class QuizSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSession
        fields = '__all__'
        read_only_fields = ['user']

class QuizAnswerSerializer(serializers.ModelSerializer):
    question_data = QuizQuestionWithAnswerSerializer(source='question', read_only=True)
    
    class Meta:
        model = QuizAnswer
        fields = ['id', 'selected_option', 'is_correct', 'time_taken_seconds', 'points_earned', 'question_data']

class QuizLeaderboardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = QuizLeaderboard
        fields = ['username', 'best_score', 'total_games', 'average_score', 'fastest_completion']
        
class ChemicalWordSerializer(serializers.ModelSerializer):
    """Serializer para palabras químicas (sin revelar la palabra)"""
    class Meta:
        model = ChemicalWord
        fields = ['id', 'category', 'difficulty', 'hint', 'atomic_number', 
                 'group_number', 'period_number', 'state_at_stp', 'chemical_formula',
                 'molecular_weight']

class ChemicalWordFullSerializer(serializers.ModelSerializer):
    """Serializer completo para palabras químicas"""
    class Meta:
        model = ChemicalWord
        fields = '__all__'

class ChemWordleGameSerializer(serializers.ModelSerializer):
    target_word = ChemicalWordSerializer(read_only=True)
    word_length = serializers.SerializerMethodField()
    
    class Meta:
        model = ChemWordleGame
        fields = ['id', 'target_word', 'is_completed', 'is_won', 'attempts_used', 
                 'max_attempts', 'guesses', 'hints_revealed', 'started_at', 'word_length']
        read_only_fields = ['user']
    
    def get_word_length(self, obj):
        return len(obj.target_word.word)

class ChemWordleGameCompleteSerializer(ChemWordleGameSerializer):
    """Serializer para juegos completados que incluye la palabra correcta"""
    target_word = ChemicalWordFullSerializer(read_only=True)

class ChemWordleAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChemWordleAttempt
        fields = ['id', 'attempt_number', 'guessed_word', 'letter_results', 'time_taken_seconds']

class ChemWordleStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChemWordleStats
        fields = ['games_played', 'games_won', 'win_percentage', 'current_streak', 
                 'max_streak', 'win_distribution', 'best_time_seconds']
        
        
class MemoryGameSerializer(serializers.ModelSerializer):
    """Serializer para partidas de Memory Molecular"""
    cards = serializers.SerializerMethodField()
    time_elapsed = serializers.SerializerMethodField()
    
    class Meta:
        model = MemoryGame
        fields = [
            'id', 'difficulty', 'is_completed', 'pairs_found', 'total_pairs',
            'attempts', 'score', 'started_at', 'completed_at', 'total_time_seconds',
            'cards', 'time_elapsed'
        ]
        read_only_fields = ['user']
    
    def get_cards(self, obj):
        """Retorna las cartas sin revelar información sensible si el juego está activo"""
        cards = obj.cards_data.copy()
        
        # Si el juego no está completado, ocultar el contenido de cartas no reveladas
        if not obj.is_completed:
            for card in cards:
                if not card['is_revealed'] and not card['is_matched']:
                    # Mantener estructura pero ocultar contenido
                    safe_card = {
                        'id': card['id'],
                        'position': card['position'],
                        'type': 'hidden',
                        'is_revealed': False,
                        'is_matched': False,
                        'compound_type': card.get('compound_type', 'unknown')
                    }
                    cards[card['position']] = safe_card
        
        return cards
    
    def get_time_elapsed(self, obj):
        """Calcula el tiempo transcurrido en segundos"""
        if obj.completed_at:
            return obj.total_time_seconds
        else:
            return int((timezone.now() - obj.started_at).total_seconds())

class MemoryStatsSerializer(serializers.ModelSerializer):
    """Serializer para estadísticas de Memory Molecular"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = MemoryStats
        fields = [
            'username', 'games_played', 'games_completed', 'completion_rate',
            'best_time_easy', 'best_time_medium', 'best_time_hard',
            'total_pairs_found', 'total_attempts', 'average_accuracy'
        ]

class MemoryCardRevealSerializer(serializers.Serializer):
    """Serializer para revelar cartas"""
    game_id = serializers.IntegerField()
    card_position = serializers.IntegerField(min_value=0)
    
    def validate_card_position(self, value):
        """Validar que la posición de la carta sea válida"""
        if value < 0:
            raise serializers.ValidationError("La posición de la carta debe ser positiva")
        return value

class MemoryGameCreateSerializer(serializers.Serializer):
    """Serializer para crear nuevas partidas"""
    difficulty = serializers.ChoiceField(
        choices=['easy', 'medium', 'hard'],
        default='easy'
    )
    total_pairs = serializers.IntegerField(
        min_value=3,
        max_value=12,
        default=6
    )
    
    def validate_total_pairs(self, value):
        """Validar que el número de pares sea apropiado para la dificultad"""
        difficulty = self.initial_data.get('difficulty', 'easy')
        max_pairs = {
            'easy': 8,
            'medium': 8,
            'hard': 8
        }
        
        if value > max_pairs.get(difficulty, 8):
            raise serializers.ValidationError(
                f"Máximo {max_pairs.get(difficulty, 8)} pares para dificultad {difficulty}"
            )
        
        return value