# Prueba de Formularios de Autenticación

## Configuración de Entorno

### Desarrollo Local (sin Docker)
```bash
# Terminal 1 - Backend
cd backend
python manage.py runserver

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

### Desarrollo con Docker
```bash
docker-compose up
```

## URLs de Prueba

- **Login**: http://localhost:3000/login
- **Registro**: http://localhost:3000/register
- **Con Docker**: Los mismos URLs funcionan

## Pruebas de Funcionalidad

### 1. Formulario de Registro (/register)

#### Validaciones a probar:
- [ ] Campo usuario vacío muestra error
- [ ] Usuario < 3 caracteres muestra error  
- [ ] Usuario > 20 caracteres muestra error
- [ ] Usuario con caracteres especiales (excepto _) muestra error
- [ ] Email inválido muestra error
- [ ] Contraseña < 8 caracteres muestra error
- [ ] Contraseñas que no coinciden muestra error
- [ ] Indicador de fuerza de contraseña funciona
- [ ] Registro exitoso redirige a /login después de 2 segundos

#### Datos de prueba válidos:
```
Usuario: testuser123
Email: test@example.com
Contraseña: TestPass123!
Confirmar: TestPass123!
```

### 2. Formulario de Login (/login)

#### Validaciones a probar:
- [ ] Campo usuario vacío muestra error
- [ ] Campo contraseña vacío muestra error
- [ ] Credenciales incorrectas muestra mensaje de error
- [ ] Botón muestra estado de carga durante el login
- [ ] Login exitoso limpia el formulario

#### Datos de prueba:
```
Usuario: testuser123
Contraseña: TestPass123!
```

## Verificación Visual

### Elementos a verificar:
- [ ] Gradientes de fondo se ven correctamente
- [ ] Animaciones de entrada funcionan
- [ ] Hover effects en inputs y botones
- [ ] Iconos en los campos se muestran
- [ ] Toggle de visibilidad de contraseña funciona
- [ ] Alertas se muestran con animación
- [ ] Links de navegación entre login/register funcionan

## Solución de Problemas Comunes

### Error: "Module not found: Can't resolve '@/lib/theme'"
**Solución**: El archivo ya fue creado en src/lib/theme.ts

### Error: "Las contraseñas no coinciden" (aunque sí coincidan)
**Solución**: Se agregó hasFeedback a los campos de contraseña para mejor visualización

### Error de conexión con backend
**Verificar**:
- Backend está corriendo en puerto 8000
- Redis está corriendo en puerto 6379
- PostgreSQL está corriendo en puerto 5432

### Para desarrollo local sin Docker:
```bash
# Verificar servicios
curl http://localhost:8000/api/
curl http://localhost:6379/ # Redis no responde HTTP, usar redis-cli
psql -h localhost -p 5432 -U postgres -l
```

### Para desarrollo con Docker:
```bash
docker-compose ps  # Todos los servicios deben estar "Up"
docker-compose logs backend  # Ver logs del backend
docker-compose logs frontend # Ver logs del frontend
```

## Comandos Útiles

```bash
# Reiniciar solo el frontend
docker-compose restart frontend

# Ver logs en tiempo real
docker-compose logs -f frontend

# Reconstruir frontend después de cambios en package.json
docker-compose build frontend
docker-compose up -d frontend

# Limpiar cache de Next.js
rm -rf frontend/.next
npm run dev
```
