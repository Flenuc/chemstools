from django.shortcuts import render
import json
from pathlib import Path
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class PeriodicTableView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        json_file_path = Path(__file__).parent / 'static' / 'data' / 'periodic_table.json'
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        return JsonResponse(data)
