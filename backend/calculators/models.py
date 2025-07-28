from django.db import models
from core.models import BaseModel

class GlossaryTerm(BaseModel):
    """
    Representa un término en el glosario químico.
    """
    term = models.CharField(max_length=255, unique=True, help_text="El término químico.")
    definition = models.TextField(help_text="La definición del término.")

    class Meta:
        verbose_name = "Término del Glosario"
        verbose_name_plural = "Términos del Glosario"
        ordering = ['term']

    def __str__(self):
        return self.term
