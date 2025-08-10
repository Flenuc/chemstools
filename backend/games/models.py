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