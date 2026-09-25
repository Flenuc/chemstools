from django.contrib import admin
from .models import ( 
        QuizQuestion, QuizSession, QuizAnswer, QuizLeaderboard,
        ChemicalWord, ChemWordleGame, ChemWordleAttempt, ChemWordleStats, 
        MemoryGame, MemoryStats,
        BalanceChallengeGame, BalanceChallengeAttempt, BalanceChallengeStats,
        PeriodicSpeedGame, PeriodicSpeedStats,
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
    
@admin.register(BalanceChallengeGame)
class BalanceChallengeGameAdmin(admin.ModelAdmin):
    list_display = ['user', 'original_equation', 'difficulty', 'is_completed', 'is_correct', 'attempts', 'started_at']
    list_filter = ['difficulty', 'is_completed', 'is_correct', 'started_at']
    search_fields = ['user__username', 'original_equation', 'target_balanced_equation']
    readonly_fields = ['started_at', 'completed_at', 'time_spent_seconds']
    ordering = ['-started_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'difficulty', 'started_at', 'completed_at')
        }),
        ('Ecuación', {
            'fields': ('original_equation', 'target_balanced_equation', 'target_coefficients')
        }),
        ('Estado del Juego', {
            'fields': ('is_completed', 'is_correct', 'attempts', 'max_attempts', 'time_spent_seconds')
        }),
        ('Interacción del Usuario', {
            'fields': ('user_coefficients', 'hints_used'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(BalanceChallengeAttempt)
class BalanceChallengeAttemptAdmin(admin.ModelAdmin):
    list_display = ['game', 'attempt_number', 'is_correct', 'time_taken_seconds', 'created_at']
    list_filter = ['is_correct', 'game__difficulty', 'created_at']
    search_fields = ['game__user__username', 'game__original_equation']
    readonly_fields = ['created_at']
    ordering = ['game', 'attempt_number']
    
    fieldsets = (
        ('Información del Intento', {
            'fields': ('game', 'attempt_number', 'created_at')
        }),
        ('Respuesta del Usuario', {
            'fields': ('coefficients_submitted', 'is_correct', 'time_taken_seconds')
        }),
        ('Resultado de Validación', {
            'fields': ('validation_result',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('game', 'game__user')

@admin.register(BalanceChallengeStats)
class BalanceChallengeStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'games_played', 'games_correct', 'accuracy_rate', 'current_streak', 'best_streak']
    readonly_fields = [
        'user', 'games_played', 'games_completed', 'games_correct',
        'completion_rate', 'accuracy_rate', 'easy_completed', 'easy_correct',
        'medium_completed', 'medium_correct', 'hard_completed', 'hard_correct',
        'average_time_per_game', 'best_time_easy', 'best_time_medium', 
        'best_time_hard', 'current_streak', 'best_streak'
    ]
    ordering = ['-accuracy_rate', '-games_correct']
    search_fields = ['user__username']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Estadísticas Generales', {
            'fields': ('games_played', 'games_completed', 'games_correct', 'completion_rate', 'accuracy_rate')
        }),
        ('Estadísticas por Dificultad', {
            'fields': (
                ('easy_completed', 'easy_correct'),
                ('medium_completed', 'medium_correct'),
                ('hard_completed', 'hard_correct')
            ),
            'classes': ('collapse',)
        }),
        ('Tiempos y Rachas', {
            'fields': (
                'average_time_per_game',
                ('best_time_easy', 'best_time_medium', 'best_time_hard'),
                ('current_streak', 'best_streak')
            ),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        return False  # Las estadísticas se crean automáticamente
    
    def has_delete_permission(self, request, obj=None):
        return False  # No permitir borrar estadísticas
    
@admin.register(PeriodicSpeedGame)
class PeriodicSpeedGameAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_element_name', 'is_completed', 'is_correct', 'time_taken_seconds', 'hint_used', 'started_at']
    list_filter = ['is_completed', 'is_correct', 'hint_used', 'started_at']
    search_fields = ['user__username']
    readonly_fields = ['started_at', 'completed_at', 'time_taken_seconds']
    ordering = ['-started_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'started_at', 'completed_at')
        }),
        ('Elemento Objetivo', {
            'fields': ('target_element',)
        }),
        ('Estado del Juego', {
            'fields': ('is_completed', 'is_correct', 'time_taken_seconds', 'hint_used')
        }),
        ('Respuesta del Usuario', {
            'fields': ('selected_element',),
            'classes': ('collapse',)
        })
    )
    
    def target_element_name(self, obj):
        """Muestra el nombre del elemento objetivo"""
        if obj.target_element:
            return f"{obj.target_element.get('name', 'Unknown')} ({obj.target_element.get('symbol', '?')})"
        return "Unknown"
    target_element_name.short_description = "Elemento Objetivo"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(PeriodicSpeedStats)
class PeriodicSpeedStatsAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'games_played', 'games_correct', 'accuracy_rate', 
        'best_time_seconds', 'current_streak', 'best_streak'
    ]
    readonly_fields = [
        'user', 'games_played', 'games_correct', 'accuracy_rate',
        'best_time_seconds', 'average_time_seconds', 'total_time_seconds',
        'current_streak', 'best_streak', 'metals_correct', 'nonmetals_correct',
        'metalloids_correct', 'noble_gases_correct', 'best_time_metals',
        'best_time_nonmetals', 'best_time_metalloids', 'best_time_noble_gases'
    ]
    ordering = ['-accuracy_rate', 'best_time_seconds']
    search_fields = ['user__username']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Estadísticas Generales', {
            'fields': ('games_played', 'games_correct', 'accuracy_rate')
        }),
        ('Tiempos', {
            'fields': ('best_time_seconds', 'average_time_seconds', 'total_time_seconds')
        }),
        ('Rachas', {
            'fields': ('current_streak', 'best_streak')
        }),
        ('Estadísticas por Categoría', {
            'fields': (
                'metals_correct', 'nonmetals_correct', 'metalloids_correct', 'noble_gases_correct'
            ),
            'classes': ('collapse',)
        }),
        ('Mejores Tiempos por Categoría', {
            'fields': (
                'best_time_metals', 'best_time_nonmetals', 'best_time_metalloids', 'best_time_noble_gases'
            ),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        return False  # Las estadísticas se crean automáticamente
    
    def has_delete_permission(self, request, obj=None):
        return False  # No permitir borrar estadísticas