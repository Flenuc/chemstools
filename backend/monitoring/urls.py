from django.urls import path
from .views import MetricsView, HealthView

app_name = 'monitoring'

urlpatterns = [
    path('metrics/', MetricsView.as_view(), name='metrics'),
    path('health/', HealthView.as_view(), name='health'),
]
