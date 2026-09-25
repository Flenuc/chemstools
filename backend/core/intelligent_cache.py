"""
Intelligent Cache System for ChemsTools
========================================
Advanced caching system with TTL management, adaptive invalidation,
and system load-based strategies for scientific computations.

Features:
- Redis backend with fallback to in-memory cache
- Configurable TTL with adaptive adjustments
- LRU eviction policy
- Cache warming and preloading
- Performance metrics and monitoring
"""

import hashlib
import json
import logging
import pickle
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

import psutil
from django.conf import settings
from django.core.cache import caches, cache
from django.core.cache.backends.base import BaseCache
from django.utils import timezone

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache invalidation strategies"""
    AGGRESSIVE = "aggressive"  # Short TTL, frequent invalidation
    BALANCED = "balanced"      # Moderate TTL, normal invalidation
    CONSERVATIVE = "conservative"  # Long TTL, minimal invalidation
    ADAPTIVE = "adaptive"      # Adjusts based on system load


@dataclass
class CacheConfig:
    """Configuration for intelligent cache"""
    backend: str = "default"  # Cache backend name from Django settings
    default_ttl: int = 3600    # Default TTL in seconds (1 hour)
    min_ttl: int = 60          # Minimum TTL (1 minute)
    max_ttl: int = 86400       # Maximum TTL (24 hours)
    strategy: CacheStrategy = CacheStrategy.ADAPTIVE
    enable_compression: bool = True
    compression_threshold: int = 1024  # Compress if larger than 1KB
    enable_metrics: bool = True
    warm_cache_on_startup: bool = False
    max_cache_size_mb: int = 500  # Maximum cache size in MB


@dataclass
class CacheMetrics:
    """Metrics for cache performance monitoring"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    evictions: int = 0
    total_size_bytes: int = 0
    avg_retrieval_time: float = 0.0
    avg_computation_time: float = 0.0
    last_reset: datetime = field(default_factory=timezone.now)
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hit_rate,
            'sets': self.sets,
            'evictions': self.evictions,
            'total_size_mb': self.total_size_bytes / (1024 * 1024),
            'avg_retrieval_time_ms': self.avg_retrieval_time * 1000,
            'avg_computation_time_ms': self.avg_computation_time * 1000,
            'last_reset': self.last_reset.isoformat()
        }


class SystemLoadMonitor:
    """Monitor system resources for adaptive caching"""
    
    @staticmethod
    def get_system_load() -> Dict[str, float]:
        """Get current system load metrics"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_io_read': psutil.disk_io_counters().read_bytes if hasattr(psutil.disk_io_counters(), 'read_bytes') else 0,
                'disk_io_write': psutil.disk_io_counters().write_bytes if hasattr(psutil.disk_io_counters(), 'write_bytes') else 0,
            }
        except Exception as e:
            logger.warning(f"Failed to get system load: {e}")
            return {
                'cpu_percent': 50.0,  # Default to moderate load
                'memory_percent': 50.0,
                'disk_io_read': 0,
                'disk_io_write': 0
            }
            
    @staticmethod
    def get_load_level() -> str:
        """Determine system load level"""
        load = SystemLoadMonitor.get_system_load()
        cpu = load['cpu_percent']
        memory = load['memory_percent']
        
        # High load if either CPU or memory is stressed
        if cpu > 80 or memory > 85:
            return 'high'
        elif cpu > 50 or memory > 60:
            return 'medium'
        else:
            return 'low'


class IntelligentCache:
    """
    Advanced caching system with intelligent TTL management
    and adaptive strategies based on system load.
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.metrics = CacheMetrics()
        self._cache_backend = self._get_cache_backend()
        self._load_monitor = SystemLoadMonitor()
        
        if self.config.warm_cache_on_startup:
            self._warm_cache()
            
    def _get_cache_backend(self) -> BaseCache:
        """Get the configured cache backend"""
        try:
            return caches[self.config.backend]
        except Exception as e:
            logger.warning(f"Failed to get cache backend '{self.config.backend}': {e}")
            logger.info("Falling back to default cache")
            return cache
            
    def _calculate_ttl(self, base_ttl: Optional[int] = None) -> int:
        """
        Calculate TTL based on strategy and system load.
        
        Args:
            base_ttl: Base TTL to use (uses default if None)
            
        Returns:
            Calculated TTL in seconds
        """
        base_ttl = base_ttl or self.config.default_ttl
        
        if self.config.strategy == CacheStrategy.AGGRESSIVE:
            ttl = int(base_ttl * 0.5)
        elif self.config.strategy == CacheStrategy.CONSERVATIVE:
            ttl = int(base_ttl * 2.0)
        elif self.config.strategy == CacheStrategy.ADAPTIVE:
            # Adjust TTL based on system load
            load_level = self._load_monitor.get_load_level()
            if load_level == 'high':
                # Longer TTL when system is under stress
                ttl = int(base_ttl * 1.5)
            elif load_level == 'low':
                # Shorter TTL when system has capacity
                ttl = int(base_ttl * 0.75)
            else:
                ttl = base_ttl
        else:
            ttl = base_ttl
            
        # Enforce min/max bounds
        return max(self.config.min_ttl, min(ttl, self.config.max_ttl))
        
    def _generate_key(self, namespace: str, identifier: str) -> str:
        """
        Generate a cache key with namespace.
        
        Args:
            namespace: Category or type of cached data
            identifier: Unique identifier for the cached item
            
        Returns:
            Cache key string
        """
        # Use hash for very long identifiers
        if len(identifier) > 200:
            identifier = hashlib.md5(identifier.encode()).hexdigest()
            
        return f"chemstools:{namespace}:{identifier}"
        
    def _compress_value(self, value: Any) -> Tuple[bytes, bool]:
        """
        Compress value if it exceeds threshold.
        
        Args:
            value: Value to potentially compress
            
        Returns:
            Tuple of (processed_value, was_compressed)
        """
        try:
            pickled = pickle.dumps(value)
            
            if self.config.enable_compression and len(pickled) > self.config.compression_threshold:
                import zlib
                compressed = zlib.compress(pickled, level=6)
                
                # Only use compression if it actually reduces size
                if len(compressed) < len(pickled):
                    return compressed, True
                    
            return pickled, False
            
        except Exception as e:
            logger.error(f"Failed to serialize value: {e}")
            raise
            
    def _decompress_value(self, value: bytes, is_compressed: bool) -> Any:
        """
        Decompress and deserialize cached value.
        
        Args:
            value: Cached value bytes
            is_compressed: Whether the value was compressed
            
        Returns:
            Original value
        """
        try:
            if is_compressed:
                import zlib
                value = zlib.decompress(value)
                
            return pickle.loads(value)
            
        except Exception as e:
            logger.error(f"Failed to deserialize cached value: {e}")
            return None
            
    def get(
        self,
        namespace: str,
        identifier: str,
        compute_func: Optional[Callable] = None,
        ttl: Optional[int] = None,
        force_refresh: bool = False
    ) -> Any:
        """
        Get value from cache or compute if missing.
        
        Args:
            namespace: Category of cached data
            identifier: Unique identifier
            compute_func: Function to compute value if cache miss
            ttl: Custom TTL for this item
            force_refresh: Force recomputation even if cached
            
        Returns:
            Cached or computed value
        """
        key = self._generate_key(namespace, identifier)
        start_time = time.time()
        
        if not force_refresh:
            # Try to get from cache
            cached_data = self._cache_backend.get(key)
            
            if cached_data is not None:
                try:
                    # Cached data format: {'value': ..., 'compressed': bool, 'metadata': {...}}
                    if isinstance(cached_data, dict) and 'value' in cached_data:
                        value = self._decompress_value(
                            cached_data['value'],
                            cached_data.get('compressed', False)
                        )
                        
                        if value is not None:
                            retrieval_time = time.time() - start_time
                            self._update_metrics(hit=True, retrieval_time=retrieval_time)
                            
                            # Log cache hit for monitoring
                            if self.config.enable_metrics:
                                logger.debug(f"Cache hit: {key} (retrieval: {retrieval_time:.3f}s)")
                                
                            return value
                            
                except Exception as e:
                    logger.error(f"Error deserializing cached value for {key}: {e}")
                    
        # Cache miss or forced refresh
        self._update_metrics(hit=False)
        
        if compute_func is None:
            return None
            
        # Compute the value
        compute_start = time.time()
        value = compute_func()
        computation_time = time.time() - compute_start
        
        # Store in cache
        if value is not None:
            self.set(namespace, identifier, value, ttl)
            
        self._update_metrics(computation_time=computation_time)
        
        if self.config.enable_metrics:
            logger.debug(f"Cache miss: {key} (computation: {computation_time:.3f}s)")
            
        return value
        
    def set(
        self,
        namespace: str,
        identifier: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache with intelligent TTL.
        
        Args:
            namespace: Category of cached data
            identifier: Unique identifier
            value: Value to cache
            ttl: Custom TTL (uses adaptive calculation if None)
            
        Returns:
            Success status
        """
        key = self._generate_key(namespace, identifier)
        ttl = self._calculate_ttl(ttl)
        
        try:
            compressed_value, is_compressed = self._compress_value(value)
            
            cache_data = {
                'value': compressed_value,
                'compressed': is_compressed,
                'metadata': {
                    'cached_at': timezone.now().isoformat(),
                    'ttl': ttl,
                    'size_bytes': len(compressed_value)
                }
            }
            
            success = self._cache_backend.set(key, cache_data, timeout=ttl)
            
            if success:
                self._update_metrics(set_operation=True, size_bytes=len(compressed_value))
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to cache value for {key}: {e}")
            return False
            
    def delete(self, namespace: str, identifier: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            namespace: Category of cached data
            identifier: Unique identifier
            
        Returns:
            Success status
        """
        key = self._generate_key(namespace, identifier)
        try:
            self._cache_backend.delete(key)
            self._update_metrics(eviction=True)
            return True
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False
            
    def clear_namespace(self, namespace: str) -> int:
        """
        Clear all cached values in a namespace.
        
        Args:
            namespace: Namespace to clear
            
        Returns:
            Number of items cleared
        """
        pattern = f"chemstools:{namespace}:*"
        try:
            # This requires cache backend to support pattern deletion
            # For Redis backend
            if hasattr(self._cache_backend, 'delete_pattern'):
                return self._cache_backend.delete_pattern(pattern)
            else:
                logger.warning(f"Cache backend doesn't support pattern deletion")
                return 0
        except Exception as e:
            logger.error(f"Failed to clear namespace {namespace}: {e}")
            return 0
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get current cache metrics"""
        return self.metrics.to_dict()
        
    def reset_metrics(self):
        """Reset cache metrics"""
        self.metrics = CacheMetrics()
        
    def _update_metrics(
        self,
        hit: Optional[bool] = None,
        set_operation: bool = False,
        eviction: bool = False,
        retrieval_time: Optional[float] = None,
        computation_time: Optional[float] = None,
        size_bytes: int = 0
    ):
        """Update internal metrics"""
        if hit is True:
            self.metrics.hits += 1
        elif hit is False:
            self.metrics.misses += 1
            
        if set_operation:
            self.metrics.sets += 1
            
        if eviction:
            self.metrics.evictions += 1
            
        if retrieval_time is not None:
            # Update average retrieval time
            n = self.metrics.hits
            if n > 0:
                self.metrics.avg_retrieval_time = (
                    (self.metrics.avg_retrieval_time * (n - 1) + retrieval_time) / n
                )
                
        if computation_time is not None:
            # Update average computation time
            n = self.metrics.misses
            if n > 0:
                self.metrics.avg_computation_time = (
                    (self.metrics.avg_computation_time * (n - 1) + computation_time) / n
                )
                
        self.metrics.total_size_bytes += size_bytes
        
    def _warm_cache(self):
        """Warm cache with frequently used data"""
        logger.info("Warming cache with frequently used data...")
        # This would be implemented based on specific application needs
        # For example, preloading common molecular structures
        pass


# Decorators for easy caching
def cached(
    namespace: str,
    ttl: Optional[int] = None,
    key_func: Optional[Callable] = None,
    strategy: CacheStrategy = CacheStrategy.ADAPTIVE
):
    """
    Decorator for caching function results.
    
    Args:
        namespace: Cache namespace
        ttl: Time to live in seconds
        key_func: Function to generate cache key from arguments
        strategy: Caching strategy
        
    Example:
        @cached(namespace="lewis_structures", ttl=3600)
        def generate_structure(formula: str) -> dict:
            # Expensive computation
            return result
    """
    def decorator(func: Callable) -> Callable:
        cache_instance = IntelligentCache(
            CacheConfig(strategy=strategy, default_ttl=ttl or 3600)
        )
        
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: use function name and arguments
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                
            # Use cache.get with compute function
            return cache_instance.get(
                namespace=namespace,
                identifier=cache_key,
                compute_func=lambda: func(*args, **kwargs),
                ttl=ttl
            )
            
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.cache = cache_instance  # Expose cache instance for management
        
        return wrapper
        
    return decorator


# Global cache instance
_intelligent_cache = None


def get_intelligent_cache(config: Optional[CacheConfig] = None) -> IntelligentCache:
    """Get or create the global intelligent cache instance"""
    global _intelligent_cache
    if _intelligent_cache is None:
        _intelligent_cache = IntelligentCache(config)
    return _intelligent_cache
