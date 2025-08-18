"""
Monitoring API Views
====================
API endpoints for accessing performance metrics,
monitoring dashboards, and Prometheus exports.
"""

import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .performance_monitoring import get_performance_monitor, monitor_performance

# Get global monitor instance
monitor = get_performance_monitor()


@api_view(['GET'])
@permission_classes([AllowAny])
def prometheus_metrics(request):
    """
    Export metrics in Prometheus format.
    
    **Method:** GET
    **URL:** /api/monitoring/metrics
    
    **Response:** Prometheus text format
    """
    metrics_text = monitor.export_prometheus_metrics()
    return HttpResponse(
        metrics_text,
        content_type='text/plain; version=0.0.4'
    )


@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(10)  # Cache for 10 seconds
def dashboard_data(request):
    """
    Get comprehensive dashboard data.
    
    **Method:** GET
    **URL:** /api/monitoring/dashboard
    
    **Response (200):**
    ```json
    {
        "system": {
            "cpu_percent": 45.2,
            "memory_percent": 62.1,
            "disk_percent": 78.5
        },
        "performance": {
            "avg_response_time": 123.4,
            "total_requests": 10234,
            "error_rate": 0.5
        },
        "cache": {
            "hit_rate": 68.5,
            "total_hits": 6789,
            "total_misses": 3211
        },
        "alerts": {
            "active": [...],
            "total_24h": 5
        },
        "timestamp": "2025-08-16T10:30:00Z"
    }
    ```
    """
    data = monitor.get_dashboard_data()
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def metric_history(request, metric_name):
    """
    Get historical data for a specific metric.
    
    **Method:** GET
    **URL:** /api/monitoring/metrics/{metric_name}/history
    
    **Query Parameters:**
    - duration_minutes: Number of minutes of history (default: 60)
    
    **Response (200):**
    ```json
    {
        "metric": "system_cpu_percent",
        "history": [
            {"value": 45.2, "timestamp": "2025-08-16T10:00:00Z"},
            {"value": 48.1, "timestamp": "2025-08-16T10:00:10Z"},
            ...
        ],
        "statistics": {
            "avg": 46.5,
            "min": 40.1,
            "max": 55.2,
            "count": 360
        }
    }
    ```
    """
    from datetime import timedelta
    
    duration_minutes = int(request.GET.get('duration_minutes', 60))
    duration = timedelta(minutes=duration_minutes)
    
    history = monitor.collector.get_history(metric_name, duration)
    stats = monitor.collector.get_statistics(metric_name)
    
    history_data = [
        {
            'value': m.value,
            'timestamp': m.timestamp.isoformat(),
            'labels': m.labels
        }
        for m in history
    ]
    
    return Response({
        'metric': metric_name,
        'history': history_data,
        'statistics': stats
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def active_alerts(request):
    """
    Get currently active alerts.
    
    **Method:** GET
    **URL:** /api/monitoring/alerts/active
    
    **Response (200):**
    ```json
    {
        "alerts": [
            {
                "name": "high_cpu_usage",
                "severity": "warning",
                "message": "High CPU usage detected: 92.3%",
                "metric": "system_cpu_percent",
                "value": 92.3,
                "timestamp": "2025-08-16T10:25:00Z"
            },
            ...
        ],
        "total": 2
    }
    ```
    """
    from django.utils import timezone
    
    # Get alerts from last hour
    active = [
        {
            'name': alert['name'],
            'severity': alert['severity'],
            'message': alert['message'],
            'metric': alert['metric'],
            'value': alert['value'],
            'timestamp': alert['timestamp'].isoformat()
        }
        for alert in monitor.alert_history
        if (timezone.now() - alert['timestamp']).seconds < 3600
    ]
    
    return Response({
        'alerts': active,
        'total': len(active)
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def configure_alert(request):
    """
    Configure a custom alert rule.
    
    **Method:** POST
    **URL:** /api/monitoring/alerts/configure
    
    **Request Body:**
    ```json
    {
        "name": "custom_alert",
        "metric_name": "custom_metric",
        "threshold": 100,
        "comparison": "greater_than",
        "severity": "warning",
        "message_template": "Custom alert: {value}",
        "cooldown_minutes": 15,
        "enabled": true
    }
    ```
    
    **Response (201):**
    ```json
    {
        "message": "Alert rule configured successfully",
        "alert": {...}
    }
    ```
    """
    from .performance_monitoring import AlertRule, AlertSeverity
    
    data = request.data
    
    # Validate required fields
    required = ['name', 'metric_name', 'threshold', 'comparison', 'severity']
    for field in required:
        if field not in data:
            return Response(
                {'error': f'Missing required field: {field}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Create condition function based on comparison type
    threshold = float(data['threshold'])
    comparison = data['comparison']
    
    if comparison == 'greater_than':
        condition = lambda v: v > threshold
    elif comparison == 'less_than':
        condition = lambda v: v < threshold
    elif comparison == 'equals':
        condition = lambda v: v == threshold
    else:
        return Response(
            {'error': 'Invalid comparison type'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create alert rule
    try:
        severity = AlertSeverity[data['severity'].upper()]
    except KeyError:
        return Response(
            {'error': 'Invalid severity level'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    rule = AlertRule(
        name=data['name'],
        metric_name=data['metric_name'],
        condition=condition,
        severity=severity,
        message_template=data.get('message_template', 'Alert: {value}'),
        cooldown_minutes=data.get('cooldown_minutes', 15),
        enabled=data.get('enabled', True)
    )
    
    # Add rule to monitor
    monitor.add_alert_rule(rule)
    
    return Response({
        'message': 'Alert rule configured successfully',
        'alert': {
            'name': rule.name,
            'metric_name': rule.metric_name,
            'severity': rule.severity.value,
            'enabled': rule.enabled
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
@monitor_performance("record_custom_metric", alert_threshold_ms=100)
def record_custom_metric(request):
    """
    Record a custom metric value.
    
    **Method:** POST
    **URL:** /api/monitoring/metrics/record
    
    **Request Body:**
    ```json
    {
        "name": "custom_metric",
        "value": 42.5,
        "type": "gauge",
        "labels": {"component": "frontend", "action": "load"},
        "unit": "ms",
        "description": "Custom metric description"
    }
    ```
    
    **Response (200):**
    ```json
    {
        "message": "Metric recorded successfully",
        "metric": {
            "name": "custom_metric",
            "value": 42.5,
            "timestamp": "2025-08-16T10:30:00Z"
        }
    }
    ```
    """
    from .performance_monitoring import MetricType
    from django.utils import timezone
    
    data = request.data
    
    # Validate required fields
    if 'name' not in data or 'value' not in data:
        return Response(
            {'error': 'Missing required fields: name and value'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Determine metric type
    metric_type = MetricType.GAUGE
    if 'type' in data:
        try:
            metric_type = MetricType[data['type'].upper()]
        except KeyError:
            pass
    
    # Record the metric
    monitor.record_metric(
        name=data['name'],
        value=float(data['value']),
        type=metric_type,
        labels=data.get('labels', {}),
        unit=data.get('unit', ''),
        description=data.get('description', '')
    )
    
    return Response({
        'message': 'Metric recorded successfully',
        'metric': {
            'name': data['name'],
            'value': data['value'],
            'timestamp': timezone.now().isoformat()
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    System health check endpoint.
    
    **Method:** GET
    **URL:** /api/monitoring/health
    
    **Response (200):**
    ```json
    {
        "status": "healthy",
        "checks": {
            "database": "ok",
            "cache": "ok",
            "cpu": "ok",
            "memory": "ok",
            "disk": "ok"
        },
        "timestamp": "2025-08-16T10:30:00Z"
    }
    ```
    """
    from django.db import connection
    from django.core.cache import cache
    from django.utils import timezone
    
    checks = {}
    overall_status = 'healthy'
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks['database'] = 'ok'
    except Exception:
        checks['database'] = 'error'
        overall_status = 'unhealthy'
    
    # Check cache
    try:
        cache.set('health_check', True, 10)
        if cache.get('health_check'):
            checks['cache'] = 'ok'
        else:
            checks['cache'] = 'error'
            overall_status = 'degraded'
    except Exception:
        checks['cache'] = 'error'
        overall_status = 'degraded'
    
    # Check system resources
    cpu = monitor.collector.get_current('system_cpu_percent') or 0
    memory = monitor.collector.get_current('system_memory_percent') or 0
    disk = monitor.collector.get_current('system_disk_usage_percent') or 0
    
    checks['cpu'] = 'ok' if cpu < 90 else 'warning'
    checks['memory'] = 'ok' if memory < 85 else 'warning'
    checks['disk'] = 'ok' if disk < 90 else 'warning'
    
    if any(v == 'warning' for v in [checks['cpu'], checks['memory'], checks['disk']]):
        if overall_status == 'healthy':
            overall_status = 'degraded'
    
    response_data = {
        'status': overall_status,
        'checks': checks,
        'timestamp': timezone.now().isoformat()
    }
    
    # Return appropriate status code
    if overall_status == 'unhealthy':
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        status_code = status.HTTP_200_OK
    
    return Response(response_data, status=status_code)
