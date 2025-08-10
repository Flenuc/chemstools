from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, ChemWordleViewSet

router = DefaultRouter()
router.register(r'quiz', QuizViewSet, basename='quiz')
router.register(r'chemwordle', ChemWordleViewSet, basename='chemwordle')

urlpatterns = [
    path('', include(router.urls)),
]