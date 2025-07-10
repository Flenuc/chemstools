Changelog
Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en Keep a Changelog (https://keepachangelog.com/en/1.0.0/), 
y este proyecto se adhiere al Versionamiento Semántico (https://semver.org/spec/v2.0.0.html).

[0.1.2] - 2025-07-09
Added
Frontend: Se crearon los componentes de React LoginForm y RegisterForm para gestionar la autenticación del usuario desde la interfaz.

Frontend: Se implementó un Header dinámico que muestra el estado de autenticación del usuario (mensaje de bienvenida y botón de logout, o un mensaje para iniciar sesión).

Frontend: Se configuró el estado global con Redux Toolkit, creando un authSlice para gestionar los tokens de acceso y la información del usuario en toda la aplicación.

Frontend: Se desarrolló un servicio de API base (api.ts) que centraliza las llamadas fetch y adjunta automáticamente el token JWT a las cabeceras de las peticiones protegidas.

Backend: Se añadió un endpoint protegido en /api/auth/me/ que devuelve los datos del usuario actualmente autenticado.

Backend: Se escribió una prueba de integración para el endpoint de perfil de usuario, asegurando que solo sea accesible para usuarios autenticados con un token válido.

Documentation: Se implementó la librería drf-spectacular para generar automáticamente una documentación interactiva de la API (Swagger UI y Redoc).

Changed
Frontend: La página principal (Home) ahora es dinámica y muestra condicionalmente los formularios de autenticación o las herramientas de la aplicación (como la calculadora de peso molecular) basándose en si el usuario ha iniciado sesión.

Backend: La prueba de integración para la vista de perfil de usuario fue mejorada para simular un flujo de login real (obtener token y luego usarlo) en lugar de forzar la autenticación.

Fixed
Backend: Se corrigió el error AssertionError: Incompatible AutoSchema de drf-spectacular al configurar explícitamente el DEFAULT_SCHEMA_CLASS en la configuración de REST_FRAMEWORK.

Frontend: Se solucionó el problema lógico de no poder iniciar sesión al no existir usuarios, mediante la adición del formulario de registro, completando así el ciclo de vida de la autenticación.

[0.1.1] - 2025-07-09
Added
Backend: Se implementó la autenticación de usuarios mediante JSON Web Tokens (JWT) utilizando la librería djangorestframework-simplejwt.

Backend: Se creó una nueva app users para gestionar toda la lógica relacionada con los usuarios, incluyendo un modelo CustomUser para futura extensibilidad.

Backend: Se desarrollaron los endpoints críticos de la API para la autenticación: /api/auth/register/, /api/auth/token/ (login), y /api/auth/token/refresh/.

Backend: Se configuró un sistema de logging básico que registra los eventos de nivel INFO y superior tanto en la consola como en un archivo logs/django.log.

Backend: Se implementó un manejador de excepciones personalizado para la API, asegurando que todos los errores se registren y devuelvan en un formato JSON consistente.

DevOps: Se configuró un pipeline de Integración Continua (CI) con GitHub Actions (.github/workflows/ci.yml) que ejecuta automáticamente linters y pruebas para el backend y el frontend en cada push y pull request a las ramas main y develop.

Changed
Backend: Se actualizó settings.py para designar a users.CustomUser como el modelo de autenticación oficial del proyecto (AUTH_USER_MODEL).

Backend: Se modificó chems_tools/urls.py para incluir las nuevas rutas de la app users bajo el prefijo /api/auth/.

Fixed
Backend: Se solucionó el error django.core.exceptions.ImproperlyConfigured que ocurría al ejecutar migraciones, especificando la ruta de configuración completa (users.apps.UsersConfig) en INSTALLED_APPS para garantizar que la app users se cargue correctamente.

[0.1.0] - 2025-07-09
Added
Backend: Se añadió la app core para alojar la lógica de negocio y los modelos compartidos.

Backend: Se configuró el framework de pruebas con pytest y pytest-django.

Backend: Se creó la primera prueba unitaria para el endpoint de API /api/health/, validando la configuración del entorno de pruebas.

Frontend: Se configuró el entorno de pruebas con Jest y React Testing Library, siguiendo las convenciones de Next.js.

Frontend: Se añadieron las definiciones de tipo (@types/jest) para asegurar la compatibilidad de Jest con TypeScript.

Frontend: Se creó la primera prueba de componente para HealthCheck.tsx, verificando el renderizado inicial y las actualizaciones de estado asíncronas.

Changed
Backend: Se actualizó settings.py para utilizar una base de datos SQLite en memoria durante la ejecución de pruebas, acelerando el proceso y aislando los entornos.

Frontend: Se actualizó el script de package.json para incluir el comando test, estandarizando la forma de ejecutar las pruebas.

Fixed
Backend: Se corrigió un error de recolección de pytest (import file mismatch) al reestructurar el directorio de pruebas de la app api y eliminar el archivo conflictivo tests.py.

Frontend: Se solucionaron los errores de TypeScript (Cannot find name 'describe', 'it', 'expect') en los archivos de prueba.

Frontend: Se eliminó la advertencia act(...) de la consola de pruebas al refactorizar la prueba del componente HealthCheck para usar waitFor, asegurando que se esperen correctamente las actualizaciones de estado asíncronas.