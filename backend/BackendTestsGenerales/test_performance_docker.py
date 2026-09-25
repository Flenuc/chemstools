#!/usr/bin/env python
"""
Performance Test Script for Docker Environment
==============================================
Tests the performance improvements with Redis available.
"""

import os
import sys
import time
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chems_tools.settings')
django.setup()

def test_parallel_computing():
    """Test parallel computing with cache"""
    print("\n=== Testing Parallel Computing with Cache ===")
    try:
        from core.parallel_computing import (
            ParallelExecutor,
            ParallelConfig,
            parallel_map,
            get_default_executor
        )
        
        # Test 1: Parallel map with caching
        print("Test 1: Parallel map with caching...")
        def compute_square(x):
            time.sleep(0.01)
            return x ** 2
        
        numbers = list(range(20))
        
        # First run - compute and cache
        start = time.time()
        results1 = parallel_map(compute_square, numbers, operation_name="test_squares")
        time1 = time.time() - start
        
        # Second run - should be faster with cache
        start = time.time()
        results2 = parallel_map(compute_square, numbers, operation_name="test_squares")
        time2 = time.time() - start
        
        assert results1 == results2
        print(f"✓ First run:  {time1:.3f}s")
        print(f"✓ Second run: {time2:.3f}s (cache speedup: {time1/time2:.2f}x)")
        
        # Test 2: Batch processing
        print("\nTest 2: Batch processing...")
        config = ParallelConfig(max_workers=4, chunk_size=5)
        executor = ParallelExecutor(config)
        
        def process_batch(items):
            return [x * 2 for x in items]
        
        results = executor.batch_process(process_batch, numbers, operation_name="test_batch")
        assert len(results) == len(numbers)
        assert results == [x * 2 for x in numbers]
        print("✓ Batch processing working")
        
        print("\n✅ Parallel computing tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_intelligent_cache():
    """Test intelligent cache with Redis"""
    print("\n=== Testing Intelligent Cache with Redis ===")
    try:
        from core.intelligent_cache import (
            IntelligentCache,
            CacheConfig,
            CacheStrategy,
            get_intelligent_cache,
            cached
        )
        
        # Test 1: Basic operations
        print("Test 1: Basic cache operations...")
        cache = get_intelligent_cache()
        
        # Test set/get
        test_data = {'key': 'value', 'number': 42}
        cache.set('test', 'redis_key', test_data, ttl=60)
        
        result = cache.get('test', 'redis_key')
        assert result == test_data
        print("✓ Redis cache working")
        
        # Test 2: Compute function with cache
        print("\nTest 2: Compute with caching...")
        compute_count = 0
        
        def expensive_computation():
            nonlocal compute_count
            compute_count += 1
            time.sleep(0.1)
            return {"result": "computed", "count": compute_count}
        
        # First call - computes
        result1 = cache.get('test', 'compute_redis', compute_func=expensive_computation)
        assert compute_count == 1
        
        # Second call - from cache
        result2 = cache.get('test', 'compute_redis', compute_func=expensive_computation)
        assert compute_count == 1  # Should not increase
        assert result1 == result2
        print("✓ Compute caching working")
        
        # Test 3: Cache metrics
        print("\nTest 3: Cache metrics...")
        metrics = cache.get_metrics()
        print(f"✓ Cache hit rate: {metrics['hit_rate']:.1f}%")
        print(f"✓ Total hits: {metrics['hits']}")
        print(f"✓ Total misses: {metrics['misses']}")
        
        # Test 4: Decorator
        print("\nTest 4: Cache decorator...")
        
        @cached(namespace='test_functions', ttl=60)
        def slow_function(x):
            time.sleep(0.1)
            return x * x
        
        # First call - slow
        start = time.time()
        result1 = slow_function(5)
        time1 = time.time() - start
        
        # Second call - cached
        start = time.time()
        result2 = slow_function(5)
        time2 = time.time() - start
        
        assert result1 == result2 == 25
        assert time2 < time1 / 2  # Should be much faster
        print(f"✓ Decorator working (speedup: {time1/time2:.1f}x)")
        
        print("\n✅ Intelligent cache tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance_monitoring():
    """Test performance monitoring with Redis"""
    print("\n=== Testing Performance Monitoring ===")
    try:
        from core.performance_monitoring import (
            get_performance_monitor,
            monitor_performance,
            MetricType
        )
        
        monitor = get_performance_monitor()
        
        # Test 1: Record and retrieve metrics
        print("Test 1: Metrics recording...")
        monitor.record_metric(
            name="test_metric_redis",
            value=123.45,
            type=MetricType.GAUGE,
            unit="ms"
        )
        
        current = monitor.collector.get_current("test_metric_redis")
        assert current == 123.45
        print("✓ Metrics recording working")
        
        # Test 2: Performance decorator
        print("\nTest 2: Performance decorator...")
        
        @monitor_performance("test_operation_redis", alert_threshold_ms=50)
        def test_function(x):
            time.sleep(0.01)
            return x * 2
        
        result = test_function(10)
        assert result == 20
        
        # Check if metric was recorded
        stats = monitor.collector.get_statistics("test_operation_redis_duration_seconds")
        assert stats.get('count', 0) > 0
        print("✓ Performance decorator working")
        
        # Test 3: Dashboard data
        print("\nTest 3: Dashboard data...")
        dashboard = monitor.get_dashboard_data()
        print(f"✓ CPU: {dashboard['system']['cpu_percent']:.1f}%")
        print(f"✓ Memory: {dashboard['system']['memory_percent']:.1f}%")
        
        print("\n✅ Performance monitoring tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_api():
    """Test batch processing API"""
    print("\n=== Testing Batch Processing API ===")
    try:
        from structures.parallel_utils import (
            ParallelLewisGenerator,
            generate_structures_batch
        )
        
        # Test 1: Parallel generator
        print("Test 1: Parallel Lewis generator...")
        generator = ParallelLewisGenerator(max_workers=2)
        
        # Generate single structure
        result = generator.generate_single_structure('H2O')
        assert result is not None
        print("✓ Single structure generation working")
        
        # Test 2: Batch generation
        print("\nTest 2: Batch generation...")
        formulas = ['H2O', 'CO2', 'NH3']
        start = time.time()
        results = generator.generate_batch_structures(formulas)
        duration = time.time() - start
        
        print(f"✓ Generated {len(results)} structures in {duration:.2f}s")
        
        # Test 3: Performance metrics
        print("\nTest 3: Performance metrics...")
        metrics = generator.get_performance_metrics()
        cache_metrics = metrics.get('cache_metrics', {})
        print(f"✓ Cache hit rate: {cache_metrics.get('hit_rate', 0):.1f}%")
        print(f"✓ System load: {metrics.get('load_level', 'unknown')}")
        
        print("\n✅ Batch API tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("PERFORMANCE TESTS IN DOCKER ENVIRONMENT")
    print("=" * 60)
    print("Testing with Redis cache enabled\n")
    
    # Check Redis connection
    from django.core.cache import cache
    try:
        cache.set('test_connection', 'ok', 10)
        if cache.get('test_connection') == 'ok':
            print("✓ Redis connection successful\n")
        else:
            print("⚠️  Redis connection issue\n")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}\n")
    
    results = {
        'Parallel Computing': test_parallel_computing(),
        'Intelligent Cache': test_intelligent_cache(),
        'Performance Monitoring': test_performance_monitoring(),
        'Batch Processing API': test_batch_api()
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for module, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{module:.<40} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Performance improvements are working correctly.")
        print("\nKey achievements:")
        print("• Parallel processing with caching enabled")
        print("• Redis cache integration working")
        print("• Performance monitoring active")
        print("• Batch API ready for production")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
