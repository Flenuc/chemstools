from django.http import HttpResponse
from django.views import View
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
import psutil
import json
import time

class MetricsView(View):
    def get(self, request):
        """
        Expone métricas personalizadas para Prometheus
        """
        metrics = []
        
        # Métricas del sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics.append(f'# HELP django_cpu_usage_percent CPU usage percentage')
        metrics.append(f'# TYPE django_cpu_usage_percent gauge')
        metrics.append(f'django_cpu_usage_percent {cpu_percent}')
        
        metrics.append(f'# HELP django_memory_usage_percent Memory usage percentage')
        metrics.append(f'# TYPE django_memory_usage_percent gauge')
        metrics.append(f'django_memory_usage_percent {memory.percent}')
        
        metrics.append(f'# HELP django_memory_available_bytes Available memory in bytes')
        metrics.append(f'# TYPE django_memory_available_bytes gauge')
        metrics.append(f'django_memory_available_bytes {memory.available}')
        
        metrics.append(f'# HELP django_disk_usage_percent Disk usage percentage')
        metrics.append(f'# TYPE django_disk_usage_percent gauge')
        metrics.append(f'django_disk_usage_percent {disk.percent}')
        
        # Métricas de la base de datos
        with connection.cursor() as cursor:
            # Número de conexiones activas
            cursor.execute("SELECT count(*) FROM pg_stat_activity")
            db_connections = cursor.fetchone()[0]
            
            metrics.append(f'# HELP django_db_connections Number of active database connections')
            metrics.append(f'# TYPE django_db_connections gauge')
            metrics.append(f'django_db_connections {db_connections}')
            
            # Tamaño de la base de datos
            cursor.execute("SELECT pg_database_size(current_database())")
            db_size = cursor.fetchone()[0]
            
            metrics.append(f'# HELP django_db_size_bytes Database size in bytes')
            metrics.append(f'# TYPE django_db_size_bytes gauge')
            metrics.append(f'django_db_size_bytes {db_size}')
        
        # Métricas de Redis/Cache
        try:
            # Test de conexión a Redis
            start_time = time.time()
            cache.set('metrics_test', 'test_value', 1)
            cache.get('metrics_test')
            redis_latency = (time.time() - start_time) * 1000  # en milisegundos
            redis_available = 1
            
            # Intentar obtener estadísticas de Redis
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            redis_info = redis_conn.info()
            
            metrics.append(f'# HELP django_redis_available Redis availability (1=up, 0=down)')
            metrics.append(f'# TYPE django_redis_available gauge')
            metrics.append(f'django_redis_available {redis_available}')
            
            metrics.append(f'# HELP django_redis_latency_ms Redis operation latency in milliseconds')
            metrics.append(f'# TYPE django_redis_latency_ms gauge')
            metrics.append(f'django_redis_latency_ms {redis_latency:.2f}')
            
            metrics.append(f'# HELP django_redis_used_memory_bytes Redis used memory in bytes')
            metrics.append(f'# TYPE django_redis_used_memory_bytes gauge')
            metrics.append(f'django_redis_used_memory_bytes {redis_info.get("used_memory", 0)}')
            
            metrics.append(f'# HELP django_redis_connected_clients Number of connected Redis clients')
            metrics.append(f'# TYPE django_redis_connected_clients gauge')
            metrics.append(f'django_redis_connected_clients {redis_info.get("connected_clients", 0)}')
            
            metrics.append(f'# HELP django_redis_total_commands_processed Total number of commands processed by Redis')
            metrics.append(f'# TYPE django_redis_total_commands_processed counter')
            metrics.append(f'django_redis_total_commands_processed {redis_info.get("total_commands_processed", 0)}')
            
        except Exception as e:
            metrics.append(f'# HELP django_redis_available Redis availability (1=up, 0=down)')
            metrics.append(f'# TYPE django_redis_available gauge')
            metrics.append(f'django_redis_available 0')
        
        # Métricas de aplicación personalizadas
        from users.models import CustomUser as User
        from molecules.models import Molecule
        from telemetry.models import TelemetryEvent
        
        user_count = User.objects.count()
        molecule_count = Molecule.objects.count()
        telemetry_count = TelemetryEvent.objects.count()
        
        metrics.append(f'# HELP django_total_users Total number of registered users')
        metrics.append(f'# TYPE django_total_users gauge')
        metrics.append(f'django_total_users {user_count}')
        
        metrics.append(f'# HELP django_total_molecules Total number of molecules in database')
        metrics.append(f'# TYPE django_total_molecules gauge')
        metrics.append(f'django_total_molecules {molecule_count}')
        
        metrics.append(f'# HELP django_total_telemetry_events Total number of telemetry events')
        metrics.append(f'# TYPE django_total_telemetry_events gauge')
        metrics.append(f'django_total_telemetry_events {telemetry_count}')
        
        # Eventos recientes (últimas 24 horas)
        recent_events = TelemetryEvent.objects.filter(
            timestamp__gte=timezone.now() - timezone.timedelta(hours=24)
        ).count()
        
        metrics.append(f'# HELP django_recent_events_24h Number of telemetry events in the last 24 hours')
        metrics.append(f'# TYPE django_recent_events_24h gauge')
        metrics.append(f'django_recent_events_24h {recent_events}')
        
        # Timestamp de la última métrica
        metrics.append(f'# HELP django_metrics_generated_timestamp Unix timestamp of metrics generation')
        metrics.append(f'# TYPE django_metrics_generated_timestamp gauge')
        metrics.append(f'django_metrics_generated_timestamp {int(time.time())}')
        
        return HttpResponse('\n'.join(metrics), content_type='text/plain; version=0.0.4')

class HealthView(View):
    def get(self, request):
        """
        Endpoint de health check para el monitoreo
        """
        health_status = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'checks': {}
        }
        
        # Check de base de datos
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status['checks']['database'] = 'ok'
        except Exception as e:
            health_status['checks']['database'] = f'error: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        # Check de Redis/Cache
        try:
            cache.set('health_check', 'ok', 1)
            if cache.get('health_check') == 'ok':
                health_status['checks']['redis'] = 'ok'
            else:
                health_status['checks']['redis'] = 'error: cannot read from cache'
                health_status['status'] = 'unhealthy'
        except Exception as e:
            health_status['checks']['redis'] = f'error: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        # Check de espacio en disco
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            health_status['checks']['disk'] = f'warning: {disk.percent}% used'
            if disk.percent > 95:
                health_status['status'] = 'unhealthy'
        else:
            health_status['checks']['disk'] = 'ok'
        
        # Check de memoria
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            health_status['checks']['memory'] = f'warning: {memory.percent}% used'
            if memory.percent > 95:
                health_status['status'] = 'unhealthy'
        else:
            health_status['checks']['memory'] = 'ok'
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        
        return HttpResponse(
            json.dumps(health_status, indent=2),
            content_type='application/json',
            status=status_code
        )
