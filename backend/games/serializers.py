from rest_framework import serializers
from .models import QuizQuestion, QuizSession, QuizAnswer, QuizLeaderboard
from .models import ChemicalWord, ChemWordleGame, ChemWordleAttempt, ChemWordleStats

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