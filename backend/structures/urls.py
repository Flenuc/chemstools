from django.urls import path
from . import views
from . import batch_views

app_name = 'structures'

urlpatterns = [
    path('lewis-generator/', views.generate_lewis_structure, name='generate_lewis'),
    path('search/', views.search_compound, name='search_compound'),
    path('cached-compounds/', views.list_cached_compounds, name='cached_compounds'),
    
    # Batch processing endpoints
    path('batch/generate/', batch_views.batch_generate_structures, name='batch_generate'),
    path('batch/validate/', batch_views.batch_validate_structures, name='batch_validate'),
    path('batch/stream/', batch_views.stream_batch_generation, name='batch_stream'),
    path('batch/status/<str:job_id>/', batch_views.get_batch_job_status, name='batch_status'),
    path('batch/metrics/', batch_views.get_performance_metrics, name='batch_metrics'),
    
    path('', views.list_structures, name='list_structures'),  # Just root path for list
    path('<int:structure_id>/', views.get_structure, name='get_structure'),
]
