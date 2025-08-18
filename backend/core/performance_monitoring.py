"""
Performance Monitoring Module for ChemsTools
=============================================
Comprehensive performance monitoring system with metrics collection,
Prometheus integration, and automated alerting.

Features:
- Real-time performance metrics
- Prometheus export endpoint
- Customizable alerting thresholds
- Historical metrics storage
- Performance dashboards
"""

import time
import logging
import functools
import threading
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import deque, defaultdict
from dataclasses import dataclass, field
from enum import Enum

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.core.mail import send_mail

import psutil

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics to track"""
    COUNTER = "counter"        # Monotonically increasing value
    GAUGE = "gauge"            # Value that can go up or down
    HISTOGRAM = "histogram"    # Distribution of values
    SUMMARY = "summary"        # Similar to histogram with percentiles


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Individual metric data"""
    name: str
    type: MetricType
    value: float
    timestamp: datetime = field(default_factory=timezone.now)
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    description: str = ""
    
    def to_prometheus(self) -> str:
        """Convert to Prometheus format"""
        # Format: metric_name{label1="value1",label2="value2"} value timestamp
        labels_str = ",".join(f'{k}="{v}"' for k, v in self.labels.items())
        if labels_str:
            labels_str = f"{{{labels_str}}}"
        
        timestamp_ms = int(self.timestamp.timestamp() * 1000)
        return f"{self.name}{labels_str} {self.value} {timestamp_ms}"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    metric_name: str
    condition: Callable[[float], bool]
    severity: AlertSeverity
    message_template: str
    cooldown_minutes: int = 15
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    
    def should_trigger(self, value: float) -> bool:
        """Check if alert should be triggered"""
        if not self.enabled:
            return False
            
        if not self.condition(value):
            return False
            
        # Check cooldown
        if self.last_triggered:
            cooldown = timedelta(minutes=self.cooldown_minutes)
            if timezone.now() - self.last_triggered < cooldown:
                return False
                
        return True


class MetricsCollector:
    """Collects and stores performance metrics"""
    
    def __init__(self, max_history: int = 1000):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.current_values: Dict[str, float] = {}
        self.lock = threading.Lock()
        
    def record(self, metric: Metric):
        """Record a metric value"""
        with self.lock:
            self.metrics[metric.name].append(metric)
            self.current_values[metric.name] = metric.value
            
    def get_current(self, name: str) -> Optional[float]:
        """Get current value of a metric"""
        return self.current_values.get(name)
        
    def get_history(
        self,
        name: str,
        duration: Optional[timedelta] = None
    ) -> List[Metric]:
        """Get historical metrics"""
        with self.lock:
            metrics = list(self.metrics.get(name, []))
            
        if duration:
            cutoff = timezone.now() - duration
            metrics = [m for m in metrics if m.timestamp >= cutoff]
            
        return metrics
        
    def get_statistics(self, name: str) -> Dict[str, float]:
        """Calculate statistics for a metric"""
        history = self.get_history(name)
        if not history:
            return {}
            
        values = [m.value for m in history]
        return {
            'count': len(values),
            'sum': sum(values),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'latest': values[-1] if values else 0
        }
        
    def export_prometheus(self) -> str:
        """Export all metrics in Prometheus format"""
        lines = []
        
        # Add HELP and TYPE comments
        for name in self.metrics:
            if self.metrics[name]:
                latest = self.metrics[name][-1]
                if latest.description:
                    lines.append(f"# HELP {name} {latest.description}")
                lines.append(f"# TYPE {name} {latest.type.value}")
                
        # Add metric values
        with self.lock:
            for name, history in self.metrics.items():
                if history:
                    lines.append(history[-1].to_prometheus())
                    
        return "\n".join(lines)


class PerformanceMonitor:
    """
    Main performance monitoring system with metrics collection,
    alerting, and reporting capabilities.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.collector = MetricsCollector()
            self.alert_rules = []
            self.alert_history = deque(maxlen=100)
            self._setup_default_alerts()
            self._start_system_monitoring()
            self.initialized = True
            
    def _setup_default_alerts(self):
        """Configure default alert rules"""
        # High CPU usage alert
        self.add_alert_rule(AlertRule(
            name="high_cpu_usage",
            metric_name="system_cpu_percent",
            condition=lambda v: v > 90,
            severity=AlertSeverity.WARNING,
            message_template="High CPU usage detected: {value:.1f}%"
        ))
        
        # High memory usage alert
        self.add_alert_rule(AlertRule(
            name="high_memory_usage",
            metric_name="system_memory_percent",
            condition=lambda v: v > 85,
            severity=AlertSeverity.WARNING,
            message_template="High memory usage detected: {value:.1f}%"
        ))
        
        # Low cache hit rate alert
        self.add_alert_rule(AlertRule(
            name="low_cache_hit_rate",
            metric_name="cache_hit_rate",
            condition=lambda v: v < 50,
            severity=AlertSeverity.INFO,
            message_template="Low cache hit rate: {value:.1f}%"
        ))
        
        # Slow response time alert
        self.add_alert_rule(AlertRule(
            name="slow_response_time",
            metric_name="avg_response_time_ms",
            condition=lambda v: v > 1000,
            severity=AlertSeverity.WARNING,
            message_template="Slow average response time: {value:.0f}ms"
        ))
        
    def _start_system_monitoring(self):
        """Start background thread for system monitoring"""
        def monitor_system():
            while True:
                try:
                    # Collect system metrics
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    # Record metrics
                    self.record_metric(
                        name="system_cpu_percent",
                        value=cpu_percent,
                        type=MetricType.GAUGE,
                        unit="percent",
                        description="CPU usage percentage"
                    )
                    
                    self.record_metric(
                        name="system_memory_percent",
                        value=memory.percent,
                        type=MetricType.GAUGE,
                        unit="percent",
                        description="Memory usage percentage"
                    )
                    
                    self.record_metric(
                        name="system_memory_available_mb",
                        value=memory.available / (1024 * 1024),
                        type=MetricType.GAUGE,
                        unit="MB",
                        description="Available memory in MB"
                    )
                    
                    self.record_metric(
                        name="system_disk_usage_percent",
                        value=disk.percent,
                        type=MetricType.GAUGE,
                        unit="percent",
                        description="Disk usage percentage"
                    )
                    
                    # Check for alerts
                    self._check_alerts()
                    
                    time.sleep(10)  # Monitor every 10 seconds
                    
                except Exception as e:
                    logger.error(f"Error in system monitoring: {e}")
                    time.sleep(30)  # Back off on error
                    
        # Start monitoring thread
        thread = threading.Thread(target=monitor_system, daemon=True)
        thread.start()
        
    def record_metric(
        self,
        name: str,
        value: float,
        type: MetricType = MetricType.GAUGE,
        labels: Optional[Dict[str, str]] = None,
        unit: str = "",
        description: str = ""
    ):
        """Record a performance metric"""
        metric = Metric(
            name=name,
            type=type,
            value=value,
            labels=labels or {},
            unit=unit,
            description=description
        )
        
        self.collector.record(metric)
        
        # Also store in cache for quick access
        cache_key = f"metric:{name}"
        cache.set(cache_key, {
            'value': value,
            'timestamp': metric.timestamp.isoformat(),
            'labels': labels
        }, timeout=300)  # 5 minutes
        
    def record_timing(
        self,
        name: str,
        duration: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """Record a timing metric (in seconds)"""
        self.record_metric(
            name=f"{name}_duration_seconds",
            value=duration,
            type=MetricType.HISTOGRAM,
            labels=labels,
            unit="seconds",
            description=f"Duration of {name} operation"
        )
        
    def add_alert_rule(self, rule: AlertRule):
        """Add an alert rule"""
        self.alert_rules.append(rule)
        
    def _check_alerts(self):
        """Check all alert rules and trigger if needed"""
        for rule in self.alert_rules:
            value = self.collector.get_current(rule.metric_name)
            if value is not None and rule.should_trigger(value):
                self._trigger_alert(rule, value)
                
    def _trigger_alert(self, rule: AlertRule, value: float):
        """Trigger an alert"""
        rule.last_triggered = timezone.now()
        
        alert = {
            'name': rule.name,
            'severity': rule.severity.value,
            'message': rule.message_template.format(value=value),
            'metric': rule.metric_name,
            'value': value,
            'timestamp': timezone.now()
        }
        
        self.alert_history.append(alert)
        
        # Log the alert
        log_method = getattr(logger, rule.severity.value, logger.info)
        log_method(f"Alert triggered: {alert['message']}")
        
        # Store in cache for dashboard
        cache_key = f"alert:{rule.name}"
        cache.set(cache_key, alert, timeout=3600)  # 1 hour
        
        # Send email for critical alerts (if configured)
        if rule.severity == AlertSeverity.CRITICAL and hasattr(settings, 'ALERT_EMAIL_RECIPIENTS'):
            try:
                send_mail(
                    subject=f"[ChemsTools Alert] {rule.name}",
                    message=alert['message'],
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=settings.ALERT_EMAIL_RECIPIENTS,
                    fail_silently=True
                )
            except Exception as e:
                logger.error(f"Failed to send alert email: {e}")
                
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        return {
            'system': {
                'cpu_percent': self.collector.get_current('system_cpu_percent'),
                'memory_percent': self.collector.get_current('system_memory_percent'),
                'disk_percent': self.collector.get_current('system_disk_usage_percent')
            },
            'performance': {
                'avg_response_time': self.collector.get_statistics('request_duration_seconds').get('avg', 0) * 1000,
                'total_requests': self.collector.get_statistics('request_count').get('sum', 0),
                'error_rate': self._calculate_error_rate()
            },
            'cache': {
                'hit_rate': self.collector.get_current('cache_hit_rate'),
                'total_hits': self.collector.get_statistics('cache_hits').get('sum', 0),
                'total_misses': self.collector.get_statistics('cache_misses').get('sum', 0)
            },
            'alerts': {
                'active': [a for a in self.alert_history if 
                          (timezone.now() - a['timestamp']).seconds < 3600],
                'total_24h': len([a for a in self.alert_history if 
                                 (timezone.now() - a['timestamp']).days < 1])
            },
            'timestamp': timezone.now().isoformat()
        }
        
    def _calculate_error_rate(self) -> float:
        """Calculate error rate percentage"""
        total = self.collector.get_statistics('request_count').get('sum', 0)
        errors = self.collector.get_statistics('request_errors').get('sum', 0)
        
        if total > 0:
            return (errors / total) * 100
        return 0.0
        
    def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        return self.collector.export_prometheus()


# Decorator for timing functions
def monitor_performance(
    operation_name: str,
    record_args: bool = False,
    alert_threshold_ms: Optional[float] = None
):
    """
    Decorator to monitor function performance.
    
    Args:
        operation_name: Name for the operation being monitored
        record_args: Whether to record function arguments as labels
        alert_threshold_ms: Alert if execution time exceeds this (in milliseconds)
        
    Example:
        @monitor_performance("generate_structure", alert_threshold_ms=500)
        def generate_structure(formula: str):
            # Function implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            
            # Prepare labels
            labels = {'operation': operation_name}
            if record_args and args:
                labels['args'] = str(args[:3])  # Record first 3 args
                
            # Start timing
            start_time = time.time()
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Record success
                monitor.record_metric(
                    name=f"{operation_name}_success",
                    value=1,
                    type=MetricType.COUNTER,
                    labels=labels
                )
                
                return result
                
            except Exception as e:
                # Record error
                monitor.record_metric(
                    name=f"{operation_name}_error",
                    value=1,
                    type=MetricType.COUNTER,
                    labels={**labels, 'error': type(e).__name__}
                )
                raise
                
            finally:
                # Record duration
                duration = time.time() - start_time
                monitor.record_timing(operation_name, duration, labels)
                
                # Check alert threshold
                if alert_threshold_ms and duration * 1000 > alert_threshold_ms:
                    logger.warning(
                        f"Operation {operation_name} exceeded threshold: "
                        f"{duration * 1000:.0f}ms > {alert_threshold_ms}ms"
                    )
                    
        return wrapper
    return decorator


# Global monitor instance
def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    return PerformanceMonitor()
