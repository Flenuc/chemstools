from django.urls import path
from .views import PeriodicTableView

urlpatterns = [
    path('periodic-table/', PeriodicTableView.as_view(), name='periodic-table'),
]