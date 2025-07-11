from django.db import models
from django.conf import settings

class Molecule(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='molecules'
    )
    name = models.CharField(max_length=255)
    structure_data = models.TextField()
    format = models.CharField(max_length=50, default='SMILES')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.owner.username})"
