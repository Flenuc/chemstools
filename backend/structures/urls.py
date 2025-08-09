from django.urls import path
from . import views

app_name = 'structures'

urlpatterns = [
    path('lewis-generator/', views.generate_lewis_structure, name='generate_lewis'),
    path('structures/', views.list_structures, name='list_structures'),
    path('structures/<int:structure_id>/', views.get_structure, name='get_structure'),
]