from django.db import models

class BaseModel(models.Model):
    """
    Un modelo de clase base abstracto que proporciona campos
    ``created_at`` y ``updated_at`` que se actualizan automáticamente.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
