from django.urls import path
from .views import HealthCheckView, MolecularWeightCalculatorView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('calculate/molecular-weight/', MolecularWeightCalculatorView.as_view(), name='molecular-weight'),
]
