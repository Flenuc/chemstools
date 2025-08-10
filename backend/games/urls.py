from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, ChemWordleViewSet, MemoryGameViewSet

router = DefaultRouter()
router.register(r'quiz', QuizViewSet, basename='quiz')
router.register(r'chemwordle', ChemWordleViewSet, basename='chemwordle')
router.register(r'memory', MemoryGameViewSet, basename='memory')

urlpatterns = [
    path('', include(router.urls)),
]