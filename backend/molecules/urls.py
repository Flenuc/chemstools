from rest_framework.routers import DefaultRouter
from .views import MoleculeViewSet

router = DefaultRouter()
router.register(r'', MoleculeViewSet, basename='molecule')
urlpatterns = router.urls