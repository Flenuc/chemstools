# Configuración de Nginx para ChemsTools

Este directorio contiene la configuración de Nginx como proxy reverso para el proyecto ChemsTools, permitiendo el acceso desde dispositivos externos en la red local.

## Características

- **Proxy reverso** para el backend (Django) y frontend (Next.js)
- **Soporte CORS** completo para permitir peticiones desde dispositivos externos
- **Compresión gzip** para mejorar el rendimiento
- **Soporte WebSocket** para actualizaciones en tiempo real
- **Headers de seguridad** configurados
- **Cache de archivos estáticos**

## Cómo usar

### 1. Construcción y ejecución con Docker Compose

```bash
# Desde el directorio raíz del proyecto
docker-compose up -d nginx
```

### 2. Acceso desde dispositivos externos

Una vez que nginx esté ejecutándose, puedes acceder a la aplicación desde cualquier dispositivo en la misma red local:

#### Desde tu computadora local:
- Frontend: `http://localhost`
- API Backend: `http://localhost/api/`
- Admin Django: `http://localhost/admin/`

#### Desde otros dispositivos en la red:
1. Encuentra tu IP local:
   ```bash
   # Windows
   ipconfig
   
   # Linux/Mac
   ip addr show
   # o
   ifconfig
   ```

2. Accede desde otros dispositivos usando tu IP local:
   - Frontend: `http://TU_IP_LOCAL`
   - API Backend: `http://TU_IP_LOCAL/api/`
   - Admin Django: `http://TU_IP_LOCAL/admin/`

   Por ejemplo: `http://192.168.1.100`

### 3. Configuración del Firewall (si es necesario)

Si no puedes acceder desde otros dispositivos, puede que necesites configurar el firewall:

#### Windows:
```powershell
# Permitir puerto 80 (HTTP)
New-NetFirewallRule -DisplayName "Allow ChemsTools HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
```

#### Linux (Ubuntu/Debian):
```bash
# Permitir puerto 80
sudo ufw allow 80/tcp
```

#### macOS:
El firewall de macOS generalmente no bloquea las conexiones salientes, pero si tienes problemas:
1. Ve a Preferencias del Sistema > Seguridad y Privacidad > Firewall
2. Haz clic en "Opciones de Firewall"
3. Asegúrate de que Docker Desktop esté permitido

## Estructura de rutas

| Ruta | Descripción | Proxy hacia |
|------|-------------|-------------|
| `/` | Frontend de la aplicación | `frontend:3000` |
| `/api/` | API del backend | `backend:8000` |
| `/admin/` | Panel de administración de Django | `backend:8000` |
| `/static/` | Archivos estáticos de Django | `backend:8000` |
| `/media/` | Archivos media de Django | `backend:8000` |
| `/ws/` | WebSocket del backend | `backend:8000` |
| `/_next/webpack-hmr` | Hot Module Replacement de Next.js | `frontend:3000` |
| `/health` | Endpoint de salud | Respuesta directa de nginx |

## Configuración CORS

La configuración actual permite:
- **Orígenes permitidos**: localhost, 127.0.0.1, y todas las IPs de red local (192.168.x.x, 10.x.x.x, 172.16-31.x.x)
- **Métodos HTTP**: GET, POST, PUT, DELETE, PATCH, OPTIONS
- **Headers permitidos**: Authorization, Content-Type, y otros headers comunes
- **Credenciales**: Habilitadas

## Logs

Los logs de nginx se guardan en:
- Access log: `/var/log/nginx/access.log`
- Error log: `/var/log/nginx/error.log`

Para ver los logs en tiempo real:
```bash
docker-compose logs -f nginx
```

## Solución de problemas

### Error: "Connection refused"
- Verifica que todos los servicios estén ejecutándose: `docker-compose ps`
- Asegúrate de que los puertos no estén siendo usados por otros servicios

### Error CORS
- Verifica que la IP desde la que estás accediendo esté en el rango permitido
- Revisa los logs del backend: `docker-compose logs -f backend`

### La página no carga desde dispositivos externos
1. Verifica que tu firewall permita conexiones en el puerto 80
2. Asegúrate de estar usando la IP correcta de tu máquina
3. Verifica que todos los dispositivos estén en la misma red

## Seguridad

⚠️ **Importante para producción**:
- Cambia `ALLOWED_HOSTS = ['*']` en `settings.py` a una lista específica de hosts permitidos
- Desactiva `DEBUG = True` en `settings.py`
- Configura HTTPS con certificados SSL
- Restringe los orígenes CORS a dominios específicos
- Implementa rate limiting
- Usa variables de entorno para datos sensibles

## Personalización

Para modificar la configuración de nginx, edita el archivo `nginx.conf` y reinicia el contenedor:

```bash
docker-compose restart nginx
```
