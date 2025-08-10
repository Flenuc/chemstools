from rest_framework import serializers
from .models import QuizQuestion, QuizSession, QuizAnswer, QuizLeaderboard

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