from django.contrib import admin
from .models import QuizQuestion, QuizSession, QuizAnswer, QuizLeaderboard

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'category', 'difficulty', 'points', 'created_at']
    list_filter = ['category', 'difficulty', 'created_at']
    search_fields = ['question_text', 'explanation']
    ordering = ['-created_at']

@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'score', 'total_questions', 'is_completed', 'started_at']
    list_filter = ['is_completed', 'started_at']
    readonly_fields = ['started_at', 'completed_at']

@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ['session', 'question', 'is_correct', 'points_earned', 'time_taken_seconds']
    list_filter = ['is_correct', 'created_at']

@admin.register(QuizLeaderboard)
class QuizLeaderboardAdmin(admin.ModelAdmin):
    list_display = ['user', 'best_score', 'total_games', 'average_score', 'fastest_completion']
    readonly_fields = ['user', 'best_score', 'total_games', 'average_score', 'fastest_completion']
    ordering = ['-best_score']