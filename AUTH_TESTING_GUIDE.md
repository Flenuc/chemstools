# Guía de Pruebas del Sistema de Autenticación - ChemsTools

## 🚀 Estado Actual

### ✅ Funcionando Correctamente:
1. **Backend API** - Endpoints de autenticación operativos
2. **Frontend Proxy** - Comunicación frontend-backend a través del proxy Next.js
3. **Registro de usuarios** - Funciona vía API directa
4. **Login de usuarios** - Funciona vía API directa con generación de tokens JWT
5. **Refresh de tokens** - Renovación de tokens funcionando
6. **Endpoints protegidos** - Validación de autenticación correcta

### 🔧 Correcciones Realizadas:

1. **Eliminación de Providers duplicados** 
   - Se removieron los Providers de Redux duplicados en las páginas de login y registro
   - El StoreProvider ahora está solo en el layout principal

2. **Configuración del Proxy**
   - Se actualizó `next.config.js` para manejar correctamente las trailing slashes
   - Se corrigió el servicio API para usar siempre rutas relativas en el cliente

3. **Redirección después del login**
   - Se agregó `useRouter` para redirigir a la página principal después del login exitoso
   - Se agregó notificación de éxito al hacer login

4. **Mejoras en el manejo de errores**
   - Se mejoró el manejo de errores en el formulario de registro
   - Se agregaron logs de debug para facilitar el diagnóstico

## 📋 Páginas de Prueba Disponibles

### 1. **Formulario de Registro Principal**
```
http://localhost:3000/register
```
- Formulario con Ant Design y validaciones
- Medidor de fuerza de contraseña
- Animaciones con Framer Motion

### 2. **Formulario de Login Principal**
```
http://localhost:3000/login
```
- Formulario con Ant Design
- Redirección automática después del login
- Integración con Redux para gestión de estado

### 3. **Formulario de Test Simple (React)**
```
http://localhost:3000/test-register
```
- Formulario React simple sin Ant Design
- Muestra información de debug en tiempo real
- Útil para verificar la comunicación con el backend

### 4. **Formulario HTML Puro (Debug)**
```
http://localhost:3000/test-form.html
```
- HTML y JavaScript vanilla
- Log detallado de todas las operaciones
- Ideal para debug de problemas de conexión

## 🧪 Scripts de Prueba Automatizados

### 1. **Test Completo del Sistema**
```bash
python test_auth_system.py
```
Prueba:
- Health checks de servicios
- Registro directo al backend
- Registro a través del proxy del frontend
- Login y obtención de tokens
- Refresh de tokens
- Acceso a endpoints protegidos

### 2. **Test del Frontend**
```bash
python test_frontend_auth.py
```
Prueba:
- Carga de páginas del frontend
- Registro a través del proxy
- Login a través del proxy
- Validaciones de formularios
- Persistencia de autenticación

## 🐛 Troubleshooting

### Si el formulario de registro no envía datos:

1. **Abrir la consola del navegador** (F12)
2. **Verificar errores de JavaScript**
3. **Revisar la pestaña Network** para ver si se envía la petición
4. **Usar el formulario de test** en `/test-form.html` que tiene logs detallados

### Si el login no redirige:

1. **Verificar que el token se está guardando** en Redux
2. **Revisar la consola para errores**
3. **Asegurarse de que la página principal (`/`) está accesible**

### Para ver logs del frontend:
```bash
docker logs chemstools_project-frontend-1 --tail 50 -f
```

### Para ver logs del backend:
```bash
docker logs chemstools_project-backend-1 --tail 50 -f
```

## 📊 Datos de Prueba

### Usuario de prueba válido:
```json
{
  "username": "testuser123",
  "email": "test@example.com",
  "password": "TestPassword123!"
}
```

### Casos de prueba para validación:

**Usuario muy corto (debe fallar):**
```json
{
  "username": "ab",
  "email": "test@test.com",
  "password": "Pass123!"
}
```

**Email inválido (debe fallar):**
```json
{
  "username": "testuser",
  "email": "invalid-email",
  "password": "Pass123!"
}
```

**Contraseña débil (debe fallar):**
```json
{
  "username": "testuser",
  "email": "test@test.com",
  "password": "123"
}
```

## 🔍 Verificación Manual

### 1. Probar registro desde el navegador:
1. Ir a `http://localhost:3000/register`
2. Llenar el formulario con datos válidos
3. Verificar que aparece el mensaje de éxito
4. Verificar que redirige a `/login` después de 2 segundos

### 2. Probar login desde el navegador:
1. Ir a `http://localhost:3000/login`
2. Usar las credenciales del usuario registrado
3. Verificar que redirige a la página principal `/`
4. Verificar que aparece la notificación de bienvenida

### 3. Verificar persistencia:
1. Después del login, refrescar la página
2. El usuario debe permanecer autenticado
3. Verificar en Redux DevTools que el estado de auth persiste

## 🚨 Problemas Conocidos y Soluciones

### Problema: "Las contraseñas no coinciden" aunque sean iguales
**Solución:** Verificar que no hay espacios al final de las contraseñas. El formulario ahora hace una comparación directa sin trim.

### Problema: El botón de registro no responde
**Solución:** 
1. Verificar que todos los campos tienen valores válidos
2. Revisar la consola del navegador para errores
3. Usar el formulario de test en `/test-form.html`

### Problema: Error de CORS
**Solución:** El proxy de Next.js debe estar manejando las peticiones. Verificar que las URLs usan rutas relativas (`/api/...`) y no absolutas.

## 📝 Notas Importantes

1. **Redis debe estar funcionando** para la gestión de sesiones
2. **PostgreSQL debe estar activo** para almacenar usuarios
3. **El backend debe estar en el puerto 8000**
4. **El frontend debe estar en el puerto 3000**

## 🎯 Próximos Pasos Recomendados

1. Implementar recuperación de contraseña
2. Agregar autenticación con OAuth (Google, GitHub)
3. Implementar 2FA (autenticación de dos factores)
4. Mejorar las validaciones del backend
5. Agregar tests E2E con Cypress o Playwright
