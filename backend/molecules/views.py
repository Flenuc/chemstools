from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Molecule
from .serializers import MoleculeSerializer

class MoleculeViewSet(viewsets.ModelViewSet):
    serializer_class = MoleculeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Asegura que los usuarios solo puedan ver sus propias moléculas,
        ordenadas por fecha de creación descendente.
        """
        return Molecule.objects.filter(owner=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)