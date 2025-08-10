from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel
import json

User = get_user_model()

class QuizQuestion(BaseModel):
    """Modelo para almacenar preguntas de química con opciones múltiples"""
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Fácil'),
        ('medium', 'Medio'),
        ('hard', 'Difícil'),
    ]
    
    CATEGORY_CHOICES = [
        ('nomenclature', 'Nomenclatura'),
        ('periodic_table', 'Tabla Periódica'),
        ('reactions', 'Reacciones Químicas'),
        ('atomic_structure', 'Estructura Atómica'),
        ('lewis_structures', 'Estructuras de Lewis'),
        ('solutions', 'Disoluciones'),
        ('ph_calculations', 'Cálculos de pH'),
    ]
    
    question_text = models.TextField(verbose_name="Pregunta")
    options = models.JSONField(verbose_name="Opciones", help_text="Array de 4 opciones")
    correct_option = models.IntegerField(verbose_name="Opción correcta", help_text="Índice de la opción correcta (0-3)")
    explanation = models.TextField(verbose_name="Explicación", blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    points = models.IntegerField(default=10, verbose_name="Puntos")
    
    class Meta:
        verbose_name = "Pregunta de Quiz"
        verbose_name_plural = "Preguntas de Quiz"
    
    def __str__(self):
        return f"{self.category} - {self.question_text[:50]}..."

class QuizSession(BaseModel):
    """Sesión de quiz de un usuario"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    questions = models.JSONField(verbose_name="IDs de preguntas", help_text="Array de IDs de preguntas")
    current_question_index = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=10)
    is_completed = models.BooleanField(default=False)
    time_limit_seconds = models.IntegerField(default=300)  # 5 minutos por defecto
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Sesión de Quiz"
        verbose_name_plural = "Sesiones de Quiz"

class QuizAnswer(BaseModel):
    """Respuesta individual de una pregunta en una sesión"""
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_option = models.IntegerField(verbose_name="Opción seleccionada")
    is_correct = models.BooleanField()
    time_taken_seconds = models.IntegerField(verbose_name="Tiempo en segundos")
    points_earned = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Respuesta de Quiz"
        verbose_name_plural = "Respuestas de Quiz"

class QuizLeaderboard(BaseModel):
    """Tabla de clasificación para el ranking"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    best_score = models.IntegerField(default=0)
    total_games = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    fastest_completion = models.IntegerField(null=True, blank=True, verbose_name="Tiempo más rápido (segundos)")
    
    class Meta:
        verbose_name = "Tabla de Clasificación"
        verbose_name_plural = "Tablas de Clasificación"
        ordering = ['-best_score', 'fastest_completion']
        
class ChemicalWord(BaseModel):
    """Modelo para almacenar palabras químicas para Wordle"""
    
    CATEGORY_CHOICES = [
        ('element', 'Elemento'),
        ('compound', 'Compuesto'),
        ('ion', 'Ion'),
        ('molecule', 'Molécula'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Fácil'),
        ('medium', 'Medio'),
        ('hard', 'Difícil'),
    ]
    
    word = models.CharField(max_length=20, unique=True, verbose_name="Palabra")
    word_lower = models.CharField(max_length=20, db_index=True, verbose_name="Palabra en minúsculas")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    hint = models.TextField(verbose_name="Pista principal")
    
    # Metadatos químicos específicos
    atomic_number = models.IntegerField(null=True, blank=True, verbose_name="Número atómico")
    group_number = models.IntegerField(null=True, blank=True, verbose_name="Grupo")
    period_number = models.IntegerField(null=True, blank=True, verbose_name="Período")
    state_at_stp = models.CharField(max_length=10, blank=True, verbose_name="Estado a STP")
    chemical_formula = models.CharField(max_length=50, blank=True, verbose_name="Fórmula química")
    molecular_weight = models.FloatField(null=True, blank=True, verbose_name="Peso molecular")
    
    # Pistas progresivas (JSON)
    hints_progressive = models.JSONField(default=list, verbose_name="Pistas progresivas")
    
    # Estadísticas de uso
    times_used = models.IntegerField(default=0, verbose_name="Veces usada")
    success_rate = models.FloatField(default=0.0, verbose_name="Tasa de éxito")
    
    class Meta:
        verbose_name = "Palabra Química"
        verbose_name_plural = "Palabras Químicas"
        ordering = ['word']
    
    def save(self, *args, **kwargs):
        self.word_lower = self.word.lower()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.word} ({self.category})"

class ChemWordleGame(BaseModel):
    """Sesión de juego ChemWordle para un usuario"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_word = models.ForeignKey(ChemicalWord, on_delete=models.CASCADE)
    
    # Estado del juego
    is_completed = models.BooleanField(default=False)
    is_won = models.BooleanField(default=False)
    attempts_used = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=6)
    
    # Progreso del juego
    guesses = models.JSONField(default=list, verbose_name="Intentos realizados")
    hints_revealed = models.JSONField(default=list, verbose_name="Pistas reveladas")
    
    # Tiempo de juego
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Partida ChemWordle"
        verbose_name_plural = "Partidas ChemWordle"
        unique_together = ['user', 'target_word', 'started_at']
    
    def __str__(self):
        status = "Ganada" if self.is_won else "Perdida" if self.is_completed else "En progreso"
        return f"{self.user.username} - {self.target_word.word} ({status})"

class ChemWordleAttempt(BaseModel):
    """Intento individual en una partida de ChemWordle"""
    game = models.ForeignKey(ChemWordleGame, on_delete=models.CASCADE, related_name='attempts')
    attempt_number = models.IntegerField(verbose_name="Número de intento")
    guessed_word = models.CharField(max_length=20, verbose_name="Palabra adivinada")
    
    # Resultado del intento (array de estados por letra)
    letter_results = models.JSONField(verbose_name="Resultado por letra")
    
    # Tiempo del intento
    time_taken_seconds = models.IntegerField(verbose_name="Tiempo en segundos")
    
    class Meta:
        verbose_name = "Intento ChemWordle"
        verbose_name_plural = "Intentos ChemWordle"
        unique_together = ['game', 'attempt_number']
        ordering = ['attempt_number']

class ChemWordleStats(BaseModel):
    """Estadísticas globales de ChemWordle por usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Estadísticas generales
    games_played = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    win_percentage = models.FloatField(default=0.0)
    
    # Estadísticas de intentos
    current_streak = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    
    # Distribución de intentos para ganar (JSON: {1: count, 2: count, ...})
    win_distribution = models.JSONField(default=dict)
    
    # Mejor tiempo
    best_time_seconds = models.IntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Estadísticas ChemWordle"
        verbose_name_plural = "Estadísticas ChemWordle"