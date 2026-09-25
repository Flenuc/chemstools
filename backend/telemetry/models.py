from django.db import models
from django.conf import settings

class TelemetryEvent(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # No borramos el evento si el usuario se elimina
        null=True,
        blank=True
    )
    session_id = models.CharField(max_length=100, blank=True) # Para agrupar eventos de una sesión
    event_name = models.CharField(max_length=100)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_name} by {self.user.username if self.user else 'Anonymous'} at {self.timestamp}"