from rest_framework import serializers
from .models import GlossaryTerm

class GlossaryTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlossaryTerm
        fields = ['id', 'term', 'definition', 'created_at', 'updated_at']