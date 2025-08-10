from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, ChemWordleViewSet, MemoryGameViewSet, BalanceChallengeViewSet, PeriodicSpeedViewSet

router = DefaultRouter()
router.register(r'quiz', QuizViewSet, basename='quiz')
router.register(r'chemwordle', ChemWordleViewSet, basename='chemwordle')
router.register(r'memory', MemoryGameViewSet, basename='memory')
router.register(r'balance-challenge', BalanceChallengeViewSet, basename='balance-challenge')
router.register(r'periodic-speed', PeriodicSpeedViewSet, basename='periodic-speed')

urlpatterns = [
    path('', include(router.urls)),
]