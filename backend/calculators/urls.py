from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GlossaryTermViewSet, pHCalculatorView

router = DefaultRouter()
router.register(r'glossary', GlossaryTermViewSet, basename='glossaryterm')

urlpatterns = [
    path('', include(router.urls)),
    path('ph-calculator/', pHCalculatorView.as_view(), name='ph-calculator'),
]
