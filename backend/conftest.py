import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _clear_cache():
    """Aísla la caché (respuestas cacheadas y contadores de throttling) entre tests."""
    cache.clear()
    yield
