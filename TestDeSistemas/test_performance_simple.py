#!/usr/bin/env python
"""
Simplified Test Script for Performance Improvements
===================================================
Tests the performance improvements without requiring Redis.
"""

import os
import sys
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

def test_parallel_computing():
    """Test the parallel computing module without Django/Redis"""
    print("\n=== Testing Parallel Computing Module (Standalone) ===")
    try:
        # Import without Django setup
        import concurrent.futures
        from concurrent.futures import ThreadPoolExecutor
        
        # Test 1: Basic parallel execution with ThreadPoolExecutor
        print("Test 1: Basic parallel execution...")
        def square(x):
            time.sleep(0.01)  # Simulate work
            return x ** 2
        
        numbers = list(range(20))
        
        # Sequential timing
        start = time.time()
        sequential_results = [square(x) for x in numbers]
        sequential_time = time.time() - start
        
        # Parallel timing
        start = time.time()
        with ThreadPoolExecutor(max_workers=4) as executor:
            parallel_results = list(executor.map(square, numbers))
        parallel_time = time.time() - start
        
        assert sequential_results == parallel_results, "Results don't match"
        speedup = sequential_time / parallel_time
        
        print(f"✓ Sequential: {sequential_time:.3f}s")
        print(f"✓ Parallel:   {parallel_time:.3f}s")
        print(f"✓ Speedup:    {speedup:.2f}x")
        
        # Test 2: Test our custom ParallelExecutor without cache
        print("\nTest 2: Custom ParallelExecutor...")
        
        # Mock the cache to avoid Redis dependency
        import unittest.mock as mock
        with mock.patch('backend.core.parallel_computing.cache'):
            from backend.core.parallel_computing import ParallelExecutor, ParallelConfig
            
            config = ParallelConfig(
                max_workers=4,
                enable_cache=False,  # Disable cache
                log_performance=False  # Disable performance logging to cache
            )
            executor = ParallelExecutor(config)
            
            # Test map_parallel
            with executor.get_executor() as exec:
                results = list(exec.map(square, numbers[:10]))
            
            assert len(results) == 10
            assert results[0] == 0
            assert results[9] == 81
            print("✓ ParallelExecutor working without cache")
        
        print("\n✅ Parallel computing tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Parallel computing tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_intelligent_cache_memory():
    """Test intelligent cache with in-memory backend"""
    print("\n=== Testing Intelligent Cache (In-Memory) ===")
    try:
        # Use a simple dict as cache backend
        class InMemoryCache:
            def __init__(self):
                self.data = {}
                
            def get(self, key):
                return self.data.get(key)
                
            def set(self, key, value, timeout=None):
                self.data[key] = value
                return True
                
            def delete(self, key):
                if key in self.data:
                    del self.data[key]
        
        # Mock Django cache
        import unittest.mock as mock
        mock_cache = InMemoryCache()
        
        with mock.patch('backend.core.intelligent_cache.cache', mock_cache):
            with mock.patch('backend.core.intelligent_cache.caches', {'default': mock_cache}):
                from backend.core.intelligent_cache import IntelligentCache, CacheConfig
                
                # Test 1: Basic operations
                print("Test 1: Basic cache operations...")
                cache = IntelligentCache(CacheConfig(enable_metrics=False))
                
                # Set and get
                cache.set('test', 'key1', 'value1')
                result = cache.get('test', 'key1')
                assert result == 'value1', f"Expected 'value1', got {result}"
                print("✓ Set/Get working")
                
                # Test 2: Compute function
                print("Test 2: Cache with compute function...")
                compute_count = 0
                
                def compute():
                    nonlocal compute_count
                    compute_count += 1
                    return f"result_{compute_count}"
                
                # First call computes
                result1 = cache.get('test', 'compute_key', compute_func=compute)
                assert compute_count == 1
                assert result1 == "result_1"
                
                # Second call uses cache
                result2 = cache.get('test', 'compute_key', compute_func=compute)
                assert compute_count == 1  # Should not increase
                assert result2 == "result_1"
                print("✓ Compute caching working")
                
        print("\n✅ Intelligent cache tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Intelligent cache tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance_monitoring_basic():
    """Test performance monitoring without Django"""
    print("\n=== Testing Performance Monitoring (Basic) ===")
    try:
        import unittest.mock as mock
        
        # Mock Django components
        with mock.patch('backend.core.performance_monitoring.cache'):
            with mock.patch('backend.core.performance_monitoring.timezone'):
                with mock.patch('backend.core.performance_monitoring.send_mail'):
                    from backend.core.performance_monitoring import (
                        MetricsCollector,
                        Metric,
                        MetricType,
                        PerformanceMonitor
                    )
                    
                    # Test 1: MetricsCollector
                    print("Test 1: Metrics collection...")
                    collector = MetricsCollector()
                    
                    # Record some metrics
                    from datetime import datetime
                    metric = Metric(
                        name="test_metric",
                        type=MetricType.GAUGE,
                        value=42.5,
                        timestamp=datetime.now()
                    )
                    collector.record(metric)
                    
                    current = collector.get_current("test_metric")
                    assert current == 42.5, f"Expected 42.5, got {current}"
                    print("✓ Metrics collection working")
                    
                    # Test 2: Statistics
                    print("Test 2: Metrics statistics...")
                    for i in range(5):
                        metric = Metric(
                            name="stat_metric",
                            type=MetricType.GAUGE,
                            value=i * 10,
                            timestamp=datetime.now()
                        )
                        collector.record(metric)
                    
                    stats = collector.get_statistics("stat_metric")
                    assert stats['count'] == 5
                    assert stats['avg'] == 20.0  # (0+10+20+30+40)/5
                    assert stats['min'] == 0
                    assert stats['max'] == 40
                    print("✓ Statistics calculation working")
                    
        print("\n✅ Performance monitoring tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Performance monitoring tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_system_load():
    """Test system load monitoring with psutil"""
    print("\n=== Testing System Load Monitoring ===")
    try:
        import psutil
        
        print("Test 1: CPU usage...")
        cpu = psutil.cpu_percent(interval=0.1)
        print(f"✓ CPU: {cpu:.1f}%")
        
        print("Test 2: Memory usage...")
        memory = psutil.virtual_memory()
        print(f"✓ Memory: {memory.percent:.1f}% ({memory.available / (1024**3):.1f} GB available)")
        
        print("Test 3: Disk usage...")
        disk = psutil.disk_usage('/')
        print(f"✓ Disk: {disk.percent:.1f}% ({disk.free / (1024**3):.1f} GB free)")
        
        print("\n✅ System monitoring working!")
        return True
        
    except Exception as e:
        print(f"❌ System monitoring failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("SIMPLIFIED PERFORMANCE TESTS - Beta 1.0.0")
    print("=" * 60)
    print("Note: Running without Redis/Django dependencies")
    
    results = {
        'Parallel Computing': test_parallel_computing(),
        'Intelligent Cache (Memory)': test_intelligent_cache_memory(),
        'Performance Monitoring': test_performance_monitoring_basic(),
        'System Load Monitoring': test_system_load()
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for module, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {module:.<40} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Core functionality is working.")
        print("\nNote: For full functionality, you'll need to:")
        print("1. Install and configure Redis")
        print("2. Update Django settings with Redis cache backend")
        print("3. Run the full test suite with Django integration")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
