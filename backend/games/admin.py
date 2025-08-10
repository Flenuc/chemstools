from django.contrib import admin
from .models import ( 
        QuizQuestion, QuizSession, QuizAnswer, QuizLeaderboard,
        ChemicalWord, ChemWordleGame, ChemWordleAttempt, ChemWordleStats, 
        MemoryGame, MemoryStats,
        )

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
    
@admin.register(ChemicalWord)
class ChemicalWordAdmin(admin.ModelAdmin):
    list_display = ['word', 'category', 'difficulty', 'atomic_number', 'times_used', 'success_rate']
    list_filter = ['category', 'difficulty', 'state_at_stp']
    search_fields = ['word', 'hint', 'chemical_formula']
    ordering = ['word']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('word', 'category', 'difficulty', 'hint')
        }),
        ('Metadatos Químicos', {
            'fields': ('atomic_number', 'group_number', 'period_number', 
                      'state_at_stp', 'chemical_formula', 'molecular_weight')
        }),
        ('Pistas Progresivas', {
            'fields': ('hints_progressive',)
        }),
        ('Estadísticas', {
            'fields': ('times_used', 'success_rate'),
            'classes': ('collapse',)
        })
    )

@admin.register(ChemWordleGame)
class ChemWordleGameAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_word', 'is_completed', 'is_won', 'attempts_used', 'started_at']
    list_filter = ['is_completed', 'is_won', 'target_word__difficulty', 'started_at']
    search_fields = ['user__username', 'target_word__word']
    readonly_fields = ['started_at', 'completed_at']
    ordering = ['-started_at']

@admin.register(ChemWordleAttempt)
class ChemWordleAttemptAdmin(admin.ModelAdmin):
    list_display = ['game', 'attempt_number', 'guessed_word', 'time_taken_seconds']
    list_filter = ['game__target_word__difficulty', 'attempt_number']
    ordering = ['game', 'attempt_number']

@admin.register(ChemWordleStats)
class ChemWordleStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'games_played', 'games_won', 'win_percentage', 'current_streak', 'max_streak']
    readonly_fields = ['user', 'games_played', 'games_won', 'win_percentage', 
                      'current_streak', 'max_streak', 'win_distribution', 'best_time_seconds']
    ordering = ['-win_percentage', '-games_won']
    
@admin.register(MemoryGame)
class MemoryGameAdmin(admin.ModelAdmin):
    list_display = ['user', 'difficulty', 'pairs_found', 'total_pairs', 'is_completed', 'score', 'started_at']
    list_filter = ['difficulty', 'is_completed', 'started_at']
    search_fields = ['user__username']
    readonly_fields = ['started_at', 'completed_at']
    ordering = ['-started_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'difficulty', 'started_at', 'completed_at')
        }),
        ('Progreso del Juego', {
            'fields': ('is_completed', 'pairs_found', 'total_pairs', 'attempts', 'score')
        }),
        ('Datos del Juego', {
            'fields': ('cards_data', 'revealed_pairs'),
            'classes': ('collapse',)
        }),
        ('Tiempo', {
            'fields': ('total_time_seconds',),
            'classes': ('collapse',)
        })
    )

@admin.register(MemoryStats)
class MemoryStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'games_played', 'games_completed', 'completion_rate', 'average_accuracy']
    readonly_fields = ['user', 'games_played', 'games_completed', 'completion_rate', 
                      'total_pairs_found', 'total_attempts', 'average_accuracy',
                      'best_time_easy', 'best_time_medium', 'best_time_hard']
    ordering = ['-completion_rate', '-average_accuracy']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Estadísticas Generales', {
            'fields': ('games_played', 'games_completed', 'completion_rate')
        }),
        ('Rendimiento', {
            'fields': ('total_pairs_found', 'total_attempts', 'average_accuracy')
        }),
        ('Mejores Tiempos', {
            'fields': ('best_time_easy', 'best_time_medium', 'best_time_hard')
        })
    )