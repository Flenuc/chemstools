"""
Parallel Computing Module for ChemsTools
=========================================
This module provides parallel processing capabilities for scientific calculations,
optimized for RDKit molecular computations and batch processing.

Features:
- Configurable thread and process pools
- Automatic resource management
- Error handling and fallback mechanisms
- Performance monitoring and metrics
"""

import os
import time
import logging
import functools
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, Future
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ExecutorType(Enum):
    """Type of executor to use for parallel processing"""
    THREAD = "thread"
    PROCESS = "process"
    AUTO = "auto"


@dataclass
class ParallelConfig:
    """Configuration for parallel processing"""
    max_workers: Optional[int] = None
    executor_type: ExecutorType = ExecutorType.AUTO
    timeout: float = 30.0
    chunk_size: int = 10
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour default
    fallback_to_sequential: bool = True
    log_performance: bool = True


class PerformanceMonitor:
    """Monitor and log performance metrics for parallel operations"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.item_count = 0
        self.error_count = 0
        
    def start(self):
        """Start timing the operation"""
        self.start_time = time.time()
        
    def end(self, item_count: int = 0, error_count: int = 0):
        """End timing and log metrics"""
        self.end_time = time.time()
        self.item_count = item_count
        self.error_count = error_count
        
        if self.start_time:
            duration = self.end_time - self.start_time
            throughput = self.item_count / duration if duration > 0 else 0
            
            logger.info(
                f"Parallel operation '{self.operation_name}' completed: "
                f"duration={duration:.2f}s, items={self.item_count}, "
                f"errors={self.error_count}, throughput={throughput:.1f} items/s"
            )
            
            # Store metrics in cache for monitoring
            metrics_key = f"metrics:parallel:{self.operation_name}"
            metrics = {
                'timestamp': self.end_time,
                'duration': duration,
                'item_count': self.item_count,
                'error_count': self.error_count,
                'throughput': throughput
            }
            cache.set(metrics_key, metrics, timeout=3600)
            
            return metrics
        return None


class ParallelExecutor:
    """
    Main class for parallel execution of scientific calculations.
    Provides both thread-based and process-based parallelism.
    """
    
    def __init__(self, config: Optional[ParallelConfig] = None):
        self.config = config or ParallelConfig()
        self._setup_executors()
        
    def _setup_executors(self):
        """Initialize executor pools based on configuration"""
        if self.config.max_workers is None:
            # Auto-detect optimal worker count
            cpu_count = os.cpu_count() or 4
            self.config.max_workers = min(32, (cpu_count * 2))
            
        logger.info(f"Initializing ParallelExecutor with {self.config.max_workers} workers")
        
    @contextmanager
    def get_executor(self, executor_type: Optional[ExecutorType] = None):
        """
        Context manager for getting an appropriate executor.
        
        Args:
            executor_type: Type of executor to use (thread/process/auto)
            
        Yields:
            Executor instance
        """
        executor_type = executor_type or self.config.executor_type
        
        if executor_type == ExecutorType.AUTO:
            # Use threads for I/O bound tasks, processes for CPU bound
            # For RDKit calculations, threads are usually sufficient
            executor_type = ExecutorType.THREAD
            
        if executor_type == ExecutorType.PROCESS:
            executor = ProcessPoolExecutor(max_workers=self.config.max_workers)
        else:
            executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
            
        try:
            yield executor
        finally:
            executor.shutdown(wait=True)
            
    def map_parallel(
        self,
        func: Callable[[T], Any],
        items: List[T],
        operation_name: str = "parallel_map",
        use_cache: bool = None,
        cache_key_func: Optional[Callable[[T], str]] = None
    ) -> List[Any]:
        """
        Apply a function to items in parallel.
        
        Args:
            func: Function to apply to each item
            items: List of items to process
            operation_name: Name for logging and metrics
            use_cache: Whether to use caching (overrides config)
            cache_key_func: Function to generate cache keys from items
            
        Returns:
            List of results in the same order as input items
        """
        if not items:
            return []
            
        use_cache = use_cache if use_cache is not None else self.config.enable_cache
        monitor = PerformanceMonitor(operation_name)
        monitor.start()
        
        results = [None] * len(items)
        errors = []
        
        try:
            with self.get_executor() as executor:
                # Check cache and prepare futures
                futures_to_index = {}
                
                for i, item in enumerate(items):
                    # Check cache if enabled
                    if use_cache and cache_key_func:
                        cache_key = cache_key_func(item)
                        cached_result = cache.get(cache_key)
                        if cached_result is not None:
                            results[i] = cached_result
                            continue
                            
                    # Submit for parallel processing
                    future = executor.submit(func, item)
                    futures_to_index[future] = (i, item)
                    
                # Collect results
                for future in as_completed(futures_to_index, timeout=self.config.timeout):
                    index, item = futures_to_index[future]
                    try:
                        result = future.result()
                        results[index] = result
                        
                        # Cache result if enabled
                        if use_cache and cache_key_func:
                            cache_key = cache_key_func(item)
                            cache.set(cache_key, result, timeout=self.config.cache_ttl)
                            
                    except Exception as e:
                        logger.error(f"Error processing item {index}: {e}")
                        errors.append((index, e))
                        
                        if self.config.fallback_to_sequential:
                            # Try sequential processing as fallback
                            try:
                                results[index] = func(item)
                            except Exception as fallback_e:
                                logger.error(f"Fallback also failed for item {index}: {fallback_e}")
                                results[index] = None
                                
        except Exception as e:
            logger.error(f"Critical error in parallel execution: {e}")
            if self.config.fallback_to_sequential:
                logger.info("Falling back to sequential processing")
                results = [func(item) for item in items]
                
        monitor.end(item_count=len(items), error_count=len(errors))
        
        return results
        
    def batch_process(
        self,
        func: Callable[[List[T]], List[Any]],
        items: List[T],
        batch_size: Optional[int] = None,
        operation_name: str = "batch_process"
    ) -> List[Any]:
        """
        Process items in batches for more efficient parallel processing.
        
        Args:
            func: Function that processes a batch of items
            items: List of items to process
            batch_size: Size of each batch (uses chunk_size from config if not specified)
            operation_name: Name for logging and metrics
            
        Returns:
            List of results
        """
        if not items:
            return []
            
        batch_size = batch_size or self.config.chunk_size
        monitor = PerformanceMonitor(operation_name)
        monitor.start()
        
        # Create batches
        batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
        
        all_results = []
        with self.get_executor() as executor:
            futures = [executor.submit(func, batch) for batch in batches]
            
            for future in as_completed(futures, timeout=self.config.timeout):
                try:
                    batch_results = future.result()
                    all_results.extend(batch_results)
                except Exception as e:
                    logger.error(f"Error processing batch: {e}")
                    # Add None for failed batch items
                    all_results.extend([None] * batch_size)
                    
        monitor.end(item_count=len(items))
        
        return all_results[:len(items)]  # Ensure we return exact number of items


# Decorator for easy parallel processing
def parallelize(
    operation_name: str = "parallel_function",
    executor_type: ExecutorType = ExecutorType.AUTO,
    max_workers: Optional[int] = None,
    use_cache: bool = True,
    cache_ttl: int = 3600
):
    """
    Decorator to automatically parallelize functions that process lists.
    
    The decorated function should accept a list and return a list.
    Each item will be processed in parallel.
    
    Example:
        @parallelize(operation_name="generate_structures")
        def generate_structures(formulas: List[str]) -> List[dict]:
            return [generate_single_structure(f) for f in formulas]
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(items: List[Any], *args, **kwargs) -> List[Any]:
            config = ParallelConfig(
                max_workers=max_workers,
                executor_type=executor_type,
                enable_cache=use_cache,
                cache_ttl=cache_ttl
            )
            
            executor = ParallelExecutor(config)
            
            # Create a function that processes a single item
            def process_single(item):
                return func([item], *args, **kwargs)[0]
                
            return executor.map_parallel(
                process_single,
                items,
                operation_name=operation_name
            )
            
        return wrapper
    return decorator


# Singleton instance for default executor
_default_executor = None


def get_default_executor() -> ParallelExecutor:
    """Get or create the default parallel executor instance"""
    global _default_executor
    if _default_executor is None:
        _default_executor = ParallelExecutor()
    return _default_executor


def parallel_map(func: Callable, items: List[Any], **kwargs) -> List[Any]:
    """
    Convenience function for parallel mapping using the default executor.
    
    Args:
        func: Function to apply to each item
        items: List of items to process
        **kwargs: Additional arguments for map_parallel
        
    Returns:
        List of results
    """
    executor = get_default_executor()
    return executor.map_parallel(func, items, **kwargs)


def parallel_batch(func: Callable, items: List[Any], batch_size: int = 10, **kwargs) -> List[Any]:
    """
    Convenience function for batch processing using the default executor.
    
    Args:
        func: Function that processes a batch of items
        items: List of items to process
        batch_size: Size of each batch
        **kwargs: Additional arguments for batch_process
        
    Returns:
        List of results
    """
    executor = get_default_executor()
    return executor.batch_process(func, items, batch_size=batch_size, **kwargs)
