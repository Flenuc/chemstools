from django.db import models
from django.utils import timezone


class MolecularStructure(models.Model):
    """Model to store generated Lewis structures"""
    formula = models.CharField(max_length=100, db_index=True)
    mol_data = models.TextField(help_text="MOL format data")
    lewis_data = models.JSONField(help_text="Lewis structure JSON representation")
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['formula']
    
    def __str__(self):
        return f"Lewis Structure: {self.formula}"