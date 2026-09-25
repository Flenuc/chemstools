from django.urls import path
from . import views

app_name = 'reactions'

urlpatterns = [
    path('balance-equation/', views.balance_equation, name='balance_equation'),
    path('balanced-reactions/', views.get_balanced_reactions, name='get_balanced_reactions'),
    path('health/', views.health_check, name='health_check'),
]