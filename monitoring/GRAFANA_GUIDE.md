# Guía de Acceso y Uso de Grafana para ChemsTools

## 🔐 Credenciales de Acceso

- **URL**: http://localhost:3001
- **Usuario**: `admin`
- **Contraseña**: `admin123`

## 📊 Dashboards Disponibles

### ChemsTools Performance Dashboard
Acceso directo: http://localhost:3001/d/chemstools-performance/chemstools-performance-dashboard

Este dashboard muestra:
- **Métricas del Sistema**
  - Uso de CPU
  - Uso de Memoria
  - Espacio en Disco
  
- **Métricas de Base de Datos**
  - Conexiones activas
  - Tamaño de la base de datos
  - Queries por segundo
  
- **Métricas de Redis**
  - Disponibilidad
  - Latencia de operaciones
  - Memoria usada
  - Comandos procesados
  
- **Métricas de Aplicación**
  - Total de usuarios registrados
  - Total de moléculas en la base de datos
  - Eventos de telemetría
  - Actividad en las últimas 24 horas

## 🔍 Cómo Usar Grafana

### 1. Acceder al Dashboard Principal
1. Abre tu navegador y ve a http://localhost:3001
2. Ingresa las credenciales (admin/admin123)
3. En el menú lateral, selecciona "Dashboards"
4. Haz clic en "ChemsTools Performance Dashboard"

### 2. Personalizar el Rango de Tiempo
- En la esquina superior derecha, encontrarás el selector de tiempo
- Puedes seleccionar rangos predefinidos (últimas 5 min, 1 hora, 24 horas, etc.)
- O definir un rango personalizado

### 3. Explorar Métricas
1. Ve a "Explore" en el menú lateral
2. Selecciona "Prometheus" como datasource
3. Puedes consultar métricas como:
   - `django_total_users` - Total de usuarios
   - `django_cpu_usage_percent` - Uso de CPU
   - `django_redis_latency_ms` - Latencia de Redis
   - `django_db_connections` - Conexiones a la BD

### 4. Crear Alertas
1. En cualquier panel del dashboard, haz clic en el título
2. Selecciona "Edit"
3. Ve a la pestaña "Alert"
4. Define las condiciones de alerta
5. Configura los canales de notificación

## 📈 Métricas Importantes a Monitorear

### Alta Prioridad
- **CPU > 80%**: Puede indicar problemas de performance
- **Memoria > 90%**: Riesgo de crashes por falta de memoria
- **Disco > 85%**: Necesidad de liberar espacio
- **Redis Down**: Cache no disponible, impacto en performance
- **DB Connections > 50**: Posible fuga de conexiones

### Media Prioridad
- **Redis Latency > 10ms**: Degradación en el cache
- **Error Rate > 1%**: Errores en la aplicación
- **Response Time > 1s**: Experiencia de usuario degradada

## 🔔 Configurar Notificaciones

### Email
1. Ve a Configuration → Notification channels
2. Añade un nuevo canal tipo "Email"
3. Configura el servidor SMTP
4. Asocia el canal a las alertas

### Webhook
1. Añade un canal tipo "Webhook"
2. Configura la URL del webhook
3. Personaliza el payload JSON
4. Asocia a las alertas críticas

## 📊 Queries Útiles de Prometheus

```promql
# Uso promedio de CPU en los últimos 5 minutos
rate(django_cpu_usage_percent[5m])

# Memoria disponible en GB
django_memory_available_bytes / 1024 / 1024 / 1024

# Tasa de crecimiento de usuarios
rate(django_total_users[1h])

# Latencia percentil 95 de Redis
histogram_quantile(0.95, django_redis_latency_ms)

# Conexiones a BD por minuto
rate(django_db_connections[1m])
```

## 🛠️ Solución de Problemas

### Dashboard no muestra datos
1. Verifica que Prometheus esté funcionando: http://localhost:9090
2. Confirma que las métricas estén disponibles: http://localhost:8000/api/monitoring/metrics/
3. En Grafana, ve a Configuration → Data Sources → Prometheus → Test

### Métricas faltantes
1. Reinicia el backend: `docker-compose restart backend`
2. Verifica los logs: `docker logs chemstools_project-backend-1`

### Alertas no se envían
1. Verifica AlertManager: http://localhost:9093
2. Revisa la configuración del canal de notificación
3. Confirma que las condiciones de alerta se cumplan

## 📚 Referencias

- [Documentación de Grafana](https://grafana.com/docs/)
- [Queries de Prometheus](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Mejores prácticas de monitoreo](https://grafana.com/blog/2019/05/07/5-monitoring-best-practices/)
