from django.db import models

class BalancedReaction(models.Model):
    """
    Modelo para almacenar reacciones químicas balanceadas
    """
    original_equation = models.TextField(help_text="Ecuación química original no balanceada")
    balanced_equation = models.TextField(help_text="Ecuación química balanceada")
    coefficients = models.JSONField(help_text="Coeficientes de balanceo")
    reaction_type = models.CharField(max_length=50, blank=True, null=True, 
                                   help_text="Tipo de reacción (síntesis, descomposición, combustión)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Reacción Balanceada"
        verbose_name_plural = "Reacciones Balanceadas"
    
    def __str__(self):
        return f"{self.original_equation} -> {self.balanced_equation}"