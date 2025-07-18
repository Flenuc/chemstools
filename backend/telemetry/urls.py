from django.urls import path
from .views import LogEventView

urlpatterns = [
    path('log/', LogEventView.as_view(), name='log-event'),
]