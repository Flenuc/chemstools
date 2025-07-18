from django.shortcuts import render
from rest_framework import generics, permissions
from .models import TelemetryEvent
from .serializers import TelemetryEventSerializer

class LogEventView(generics.CreateAPIView):
    queryset = TelemetryEvent.objects.all()
    serializer_class = TelemetryEventSerializer
    permission_classes = [permissions.IsAuthenticated] # Solo usuarios logueados

    def perform_create(self, serializer):
        # Asigna el usuario actual al evento
        serializer.save(user=self.request.user)