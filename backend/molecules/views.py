from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Molecule
from .serializers import MoleculeSerializer

class MoleculeViewSet(viewsets.ModelViewSet):
    serializer_class = MoleculeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Molecule.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)