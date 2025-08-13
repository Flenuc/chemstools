from django.urls import path
from . import views

app_name = 'structures'

urlpatterns = [
    path('lewis-generator/', views.generate_lewis_structure, name='generate_lewis'),
    path('search/', views.search_compound, name='search_compound'),
    path('cached-compounds/', views.list_cached_compounds, name='cached_compounds'),
    path('', views.list_structures, name='list_structures'),  # Just root path for list
    path('<int:structure_id>/', views.get_structure, name='get_structure'),
]
