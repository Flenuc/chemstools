from django.db import models

class BaseModel(models.Model):
    """
    Un modelo de clase base abstracto que proporciona campos
    ``created_at`` y ``updated_at`` que se actualizan automáticamente.
    También incluye métodos comunes para todos los modelos.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de creación del registro."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Fecha y hora de la última actualización del registro."
    )
    class Meta:
        abstract = True
    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para asegurar que updated_at
        se actualice correctamente.
        """
        super().save(*args, **kwargs)