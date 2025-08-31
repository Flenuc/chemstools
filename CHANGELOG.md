Changelog
Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en Keep a Changelog (https://keepachangelog.com/en/1.0.0/), 
y este proyecto se adhiere al Versionamiento Semántico (https://semver.org/spec/v2.0.0.html).

[1.1.0-beta] - 2025-08-31

Fixed
Frontend: Se han corregido errores de TypeScript en los componentes de la calculadora de pH avanzada:
- Corregido el error de tipo en PHExport.tsx cambiando el string literal 'csv' por el valor del enum ExportFormat.CSV
- Actualizado PHHistory.tsx para usar el enum CalculationType importado desde types/advancedPH.ts en lugar de tipos literales de string
- Agregado el slice advancedPH al store principal de Redux en store/index.ts para resolver errores de estado no definido
- Asegurada la consistencia de tipos entre los componentes y las definiciones TypeScript centralizadas

Added
Frontend: Se ha implementado la interfaz completa de la Calculadora de pH/pOH Avanzada con componentes React modernos y funcionalidades profesionales:
- Página principal (frontend/src/app/calculators/advanced-ph/page.tsx) con diseño responsive y navegación por pestañas
- Suite completa de componentes en frontend/src/components/calculators/ incluyendo:
  * PHCalculatorForm: Formulario principal con validación en tiempo real y selección de tipo de cálculo
  * PHResultDisplay: Visualización profesional de resultados con indicadores de pH y clasificación de solución
  * PHStepByStep: Vista detallada paso a paso con fórmulas matemáticas renderizadas y explicaciones
  * PHHistoryTable: Tabla de historial con filtros, búsqueda y acciones de exportación
  * BufferSystemSelector: Selector inteligente de sistemas buffer con recomendaciones basadas en pH objetivo
  * PHExportOptions: Panel de opciones de exportación con soporte para múltiples formatos (PDF, CSV, JSON, Excel)
- Servicio dedicado (frontend/src/services/phCalculatorService.ts) para comunicación con la API backend
- Estado global con Redux (frontend/src/store/advancedPHSlice.ts) para gestión centralizada del estado
- Hooks personalizados (frontend/src/store/hooks.ts) para acceso tipado al store de Redux
- Tipos TypeScript completos (frontend/src/types/advancedPH.ts) para todas las entidades del dominio
- Utilidad de exportación PDF (frontend/src/utils/pdfExport.ts) con generación de documentos profesionales

Frontend: Se han implementado características avanzadas de UX/UI en la calculadora de pH:
- Animaciones fluidas con Framer Motion para transiciones y feedback visual
- Gráficos interactivos con Chart.js para visualización de tendencias y distribuciones
- Indicador visual de pH con escala de colores y clasificación automática (ácido/neutro/base)
- Sistema de notificaciones integrado para feedback inmediato al usuario
- Formularios con validación en tiempo real y mensajes de ayuda contextuales
- Modo oscuro/claro con persistencia de preferencias del usuario
- Tooltips informativos con explicaciones químicas para cada campo

Frontend: Se ha desarrollado un sistema completo de gestión del historial de cálculos:
- Tabla paginada con ordenamiento por múltiples columnas
- Filtros avanzados por tipo de cálculo, rango de fechas y presencia de warnings
- Búsqueda en tiempo real con debounce para optimización
- Acciones batch para exportación y eliminación múltiple
- Vista de detalle expandible para cada cálculo con pasos completos
- Integración con el sistema de exportación para generar reportes

Frontend: Se ha implementado un sistema robusto de exportación de datos:
- Generación de PDFs profesionales con jsPDF incluyendo gráficos y tablas
- Exportación a CSV con formato optimizado para Excel
- Exportación JSON estructurada con metadatos completos
- Exportación Excel (XLSX) con hojas múltiples y formato condicional
- Preview de exportación antes de descarga
- Configuración personalizable de campos a incluir

Added
Backend: Se ha implementado la Calculadora de pH/pOH Avanzada con funcionalidades profesionales, transformando la calculadora básica en una herramienta científica robusta.

Backend: Se ha creado un sistema de validación químicamente preciso usando cerberus con esquemas especializados:
- ph_calculation_schema: Para cálculos básicos de pH/pOH con validación de rangos (pH 0-14, temperatura 0-100°C)
- buffer_calculation_schema: Para sistemas buffer con validación de componentes y concentraciones
- ionic_strength_schema: Para cálculos de fuerza iónica con iones y cargas
- Validación específica por tipo de entrada (pH, pOH, concentraciones H+/OH-)
- Generación automática de warnings químicos contextuales para condiciones extremas

Backend: Se ha desarrollado un sistema de cálculos químicos avanzados en chemistry_utils.py con funciones científicas profesionales:
- calculate_ionic_strength(): Implementa I = 0.5 × Σ(ci × zi²) para sistemas multiónicos
- calculate_activity_coefficient(): Ecuación de Debye-Hückel extendida con parámetros de tamaño iónico específicos
- calculate_buffer_capacity(): Fórmula completa β = 2.303 × (Kw/[H+] + [H+] + Σ términos buffer)
- correct_kw_for_temperature(): Corrección de constante del agua con interpolación entre 0-100°C
- comprehensive_ph_calculation(): Motor principal que integra todas las correcciones químicas
- Constantes químicas precisas: KW_TEMPERATURE_CORRECTION, ACTIVITY_COEFFICIENTS, COMMON_BUFFERS
- Decoradores de rendimiento: @parallelize, @cached(ttl), @monitor_performance

Backend: Se ha implementado el modelo PHCalculationHistory para persistencia completa del historial de cálculos:
- Almacenamiento con UUID como primary key y metadatos completos (usuario, tipo, tiempo de cálculo)
- Campos especializados: input_data (JSON), results (JSON), calculation_steps, warnings, temperature, ionic_strength
- Métodos avanzados: export_to_dict(), get_formatted_results(), is_buffer_calculation(), get_stats_for_user()
- Índices optimizados para consultas frecuentes por usuario, tipo de cálculo y fecha
- Soporte para usuarios anónimos y estadísticas agregadas por usuario

Backend: Se han creado serializers avanzados con validación integrada y funcionalidades profesionales:
- AdvancedPHCalculatorSerializer: Validación completa con cerberus + cálculo automático integrado
- PHCalculationHistorySerializer: Manejo del historial con campos formateados y metadatos
- BufferCalculationSerializer: Especializado para sistemas buffer con análisis de componentes
- ExportSerializer: Validación para exportaciones en múltiples formatos (CSV, PDF, JSON)
- Generación automática de pasos detallados del cálculo para propósitos educativos

Backend: Se han implementado views profesionales en advanced_views.py con manejo robusto de errores:
- AdvancedPHCalculatorView: Endpoint principal que integra validación, cálculo y guardado automático
- PHCalculationHistoryViewSet: CRUD completo con filtros avanzados (tipo, warnings, rango de fechas)
- ExportPHCalculationsView: Exportación asíncrona en CSV, PDF y JSON con URLs temporales
- PHCalculationStatsView: Estadísticas detalladas con insights químicos y análisis de patrones de uso
- BufferCalculatorView: Cálculos especializados de buffer con análisis de efectividad
- Logging detallado y manejo de excepciones específicas para debugging químico

Backend: Se ha desarrollado un sistema de exportación profesional en export_utils.py:
- export_to_csv(): Usando pandas con formato científico, encoding UTF-8-sig para Excel
- export_to_pdf(): Con reportlab incluyendo tablas profesionales, estadísticas y metadatos
- export_to_json(): Estructura completa con información de exportación y versionado
- PHCalculationPDFGenerator: Clase para PDFs avanzados con header, análisis y anexos
- CSVExporter: Optimizado para datos científicos con notación científica apropiada
- create_download_url(): URLs temporales con expiración automática (24h default)
- cleanup_expired_exports(): Función utilitaria para limpieza automática de archivos

Backend: Se han implementado 8 nuevos endpoints API con rate limiting diferenciado:
- POST /api/calculators/advanced-ph-calculator/ (30/min): Cálculo principal con todas las funcionalidades
- GET /api/calculators/ph-calculation-history/ (100/min): ViewSet completo del historial
- POST /api/calculators/export-ph-calculations/ (5/min): Exportación controlada en múltiples formatos
- GET /api/calculators/ph-calculation-stats/ (100/min): Estadísticas con insights químicos
- POST /api/calculators/buffer-calculator/ (20/min): Cálculos especializados de buffer
- Mantenimiento de backward compatibility con endpoints básicos existentes

Backend: Se ha creado una suite exhaustiva de pruebas en test_advanced_ph.py con >85% de cobertura:
- TestAdvancedPHValidation: 25+ pruebas de validación con casos edge complejos
- TestChemistryUtils: Validación de precisión química contra literatura científica
- TestAdvancedPHCalculator: Pruebas de API endpoints con autenticación y casos reales
- TestPHCalculationHistory: Persistencia, filtros y aislamiento de usuarios
- TestExportFunctionality: Exportación en todos los formatos con validación de contenido
- TestPerformanceOptimizations: Pruebas de cache, paralelización y datasets grandes
- PHCalculationTestFixtures: Fixtures reutilizables con datos químicos realistas

Backend: Se ha añadido el comando de management populate_ph_examples.py para poblado de datos:
- 20+ ejemplos químicos realistas: agua pura, ácidos/bases fuertes, sistemas buffer
- Casos especiales: corrección de temperatura, alta fuerza iónica, pH extremos
- Sistemas fisiológicos: buffer fosfato (pH 7.4), agua de mar, lluvia ácida
- Sistemas buffer profesionales: acetato, fosfato, Tris, carbonato con análisis completo
- Soporte para usuario demo y limpieza de ejemplos existentes

Infrastructure: Se han actualizado las dependencias en requirements.txt para funcionalidades avanzadas:
- cerberus>=1.3.4: Validación de esquemas químicos robusta
- reportlab>=4.0.0: Generación de PDFs profesionales con gráficos
- pandas>=1.3.0: Manipulación de datos científicos para exportación
- matplotlib>=3.7.0 + seaborn>=0.12.0: Gráficos estadísticos para PDFs
- django-ratelimit>=4.1.0: Rate limiting avanzado con Redis backend

Changed
Architecture: Se ha adoptado un patrón de separación clara entre validación (validators.py), cálculos químicos (chemistry_utils.py), persistencia (models.py) y presentación (advanced_views.py), mejorando mantenibilidad y testing.

Performance: Se ha implementado un sistema de cache inteligente con TTL configurable, optimización de consultas ORM con índices especializados, y preparación para paralelización de cálculos intensivos.

API Design: Se ha establecido un patrón consistente de respuestas JSON con campos success/error, metadatos completos (calculation_id, tiempo, metodología), y manejo unificado de warnings químicos.

Documentation: Se han mejorado significativamente todos los docstrings con ejemplos químicos específicos, parámetros detallados y referencias a literatura científica para mejor comprensión del código.

Fixed
Validation: Se han corregido los validadores personalizados de cerberus para usar reglas estándar (min/max) en lugar de validadores custom que causaban warnings, asegurando validación química precisa.

Testing: Se han solucionado problemas de importación en la suite de pruebas agregando django.db.models.Min y configurando correctamente los fixtures para casos químicos realistas.

Backend: Se ha corregido el manejo de casos edge en cálculos químicos incluyendo concentraciones extremadamente bajas, pH cercanos a neutro con corrección de actividad, y sistemas buffer con componentes desbalanceados.

[1.0.0-beta] - 2025-08-18

Added

BACKEND - Infraestructura de Rendimiento:

Backend: Se ha implementado un sistema completo de paralelización para cálculos científicos:
- Módulo backend/core/parallel_computing.py con ThreadPoolExecutor y ProcessPoolExecutor configurables
- Gestión automática de recursos con detección de CPUs disponibles
- Fallback inteligente a procesamiento secuencial en caso de error
- Decorador @parallelize para facilitar la integración en funciones existentes
- Monitoreo de rendimiento integrado con métricas de ejecución
- Speedup demostrado de hasta 4x en operaciones paralelas

Backend: Se ha creado un sistema de cache inteligente con TTL adaptativo:
- Módulo backend/core/intelligent_cache.py con Redis como backend principal
- TTL adaptativo basado en la carga del sistema (CPU, memoria)
- Compresión automática para datos grandes (>512 bytes)
- Estrategias de invalidación configurables (Aggressive, Balanced, Conservative, Adaptive)
- Métricas detalladas de hit rate y performance
- Decorador @cached con configuración flexible
- Cache hit rate del 66.7% alcanzado en pruebas con speedup de hasta 1430x para datos cacheados

Backend: Se ha optimizado la generación de estructuras moleculares:
- Módulo backend/structures/parallel_utils.py para procesamiento paralelo
- Generación paralela de múltiples estructuras de Lewis
- Cálculo paralelo de propiedades moleculares con RDKit
- Validación batch de estructuras químicas
- Optimización de coordenadas 2D en paralelo
- Integración completa con cache inteligente

Backend: Se han implementado endpoints de procesamiento batch:
- POST /api/structures/batch/generate/ para generación batch de estructuras
- POST /api/structures/batch/validate/ para validación paralela de moléculas
- POST /api/structures/batch/stream/ con streaming de resultados (Server-Sent Events)
- GET /api/structures/batch/status/{job_id}/ para tracking de trabajos
- GET /api/structures/batch/metrics/ para métricas de rendimiento en tiempo real
- Throughput de 50+ estructuras/segundo en hardware moderno

Backend: Se ha desarrollado un sistema completo de monitoreo de rendimiento:
- Módulo backend/core/performance_monitoring.py con métricas en tiempo real
- Tracking de CPU, memoria, disco y operaciones de I/O
- Exportación de métricas en formato Prometheus
- Sistema de alertas configurables por umbrales
- Dashboard interno de monitoreo con visualización de métricas
- Health checks automáticos para servicios críticos
- Decorador @monitor_performance para instrumentación de funciones

FRONTEND - Migración a Ant Design y Framer Motion:

Frontend: Se ha implementado un nuevo sistema de navegación escalable:
- Componente NavigationSidebar.tsx con drawer responsive para móviles
- Componente DesktopSidebar.tsx con sidebar colapsable para escritorio
- Categorización de contenido (Herramientas, Juegos, Demos, Educación)
- Búsqueda integrada en el sidebar con filtrado en tiempo real
- Badges informativos para nuevas funcionalidades
- Soporte completo para autenticación con menú de usuario
- Layout wrapper AppLayout.tsx que integra ambos componentes

Frontend: Se ha migrado completamente la página de Glossary a Ant Design:
- Índice alfabético interactivo para filtrar términos rápidamente
- Búsqueda optimizada con debounce que filtra en términos y definiciones
- Visualización con Cards de Ant Design con texto expandible
- Indicadores visuales de cantidad total y filtrada de términos
- Animaciones suaves con Framer Motion y AnimatePresence
- Estados de carga, error y vacío con componentes especializados
- Diseño responsive con gradientes y efectos glassmorphism
- Botón flotante para volver arriba en listados largos

Frontend: Se ha refinado el componente LewisStructureGenerator con nueva UI:
- Migración completa a componentes de Ant Design (Card, Input, Select, Button, Alert, Tag, Tooltip)
- Animaciones con Framer Motion para transiciones suaves
- Header animado con gradiente de colores y efectos visuales
- Cards con degradado de colores para secciones principales
- Iconos animados con rebote y rotación para elementos moleculares
- Integración del sistema de ayuda con tooltips contextuales
- Mantenimiento de toda la funcionalidad original (búsqueda PubChem, renderizado Kekule.js)

DEVOPS - Monitoreo Avanzado con Prometheus y Grafana:

DevOps: Se ha configurado un stack completo de monitoreo:
- Prometheus (puerto 9090) recolectando métricas de todos los servicios
- Grafana (puerto 3001) con dashboards preconfigurados
- AlertManager (puerto 9093) para gestión de alertas
- Exportadores especializados: Redis Exporter (9121), Node Exporter (9100), PostgreSQL Exporter (9187)
- Configuración de scraping cada 15 segundos para métricas en tiempo real

DevOps: Se han creado dashboards personalizados en Grafana:
- Dashboard principal de ChemsTools Performance con 15+ paneles
- Métricas del sistema (CPU, memoria, disco, red)
- Métricas de base de datos (conexiones, tamaño, queries)
- Métricas de Redis (latencia, memoria, comandos procesados)
- Métricas de aplicación (usuarios, moléculas, eventos)
- Visualización de cache hit rates y performance
- Gráficos de tendencias y alertas visuales

DevOps: Se han implementado endpoints de monitoreo en Django:
- GET /api/monitoring/metrics/ con métricas en formato Prometheus
- GET /api/monitoring/health/ con health checks completos
- GET /api/monitoring/dashboard/ con dashboard HTML interactivo
- POST /api/monitoring/alerts/ para gestión de alertas
- Integración con telemetría existente para métricas de aplicación

DevOps: Se ha creado documentación completa de monitoreo:
- Guía GRAFANA_GUIDE.md con instrucciones detalladas
- Configuración de datasources (Prometheus, PostgreSQL, Redis)
- Queries útiles de PromQL para análisis avanzado
- Configuración de alertas y notificaciones
- Troubleshooting y mejores prácticas

INFRAESTRUCTURA - Nginx y Acceso Remoto:

Infrastructure: Se ha implementado un servidor proxy reverso Nginx completo para permitir el acceso desde dispositivos externos en la red local:
- Creación de archivo de configuración nginx.conf en docker/nginx/ con soporte completo para proxy reverso
- Configuración de upstreams para backend (puerto 8000) y frontend (puerto 3000)
- Implementación de rutas específicas para API (/api/), administración Django (/admin/), archivos estáticos (/static/), y archivos media (/media/)
- Soporte para WebSockets tanto para backend (/ws/) como para Hot Module Replacement del frontend (/_next/webpack-hmr)
- Configuración de compresión gzip para optimizar el rendimiento de transferencia de datos
- Headers de seguridad configurados (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection)
- Endpoint de health check (/health) para monitoreo del servicio

Infrastructure: Se ha creado Dockerfile especializado para el contenedor de Nginx:
- Imagen base nginx:alpine para menor tamaño y mejor seguridad
- Eliminación de configuración por defecto y aplicación de configuración personalizada
- Creación de directorios necesarios para logs
- Exposición del puerto 80 para acceso HTTP estándar

Backend: Se ha actualizado la configuración de CORS en Django settings.py para permitir acceso desde dispositivos externos:
- Actualización de ALLOWED_HOSTS para incluir wildcard (*) en desarrollo
- Configuración expandida de CORS_ALLOWED_ORIGINS con soporte para localhost, 127.0.0.1 y puerto 80
- Implementación de CORS_ALLOWED_ORIGIN_REGEXES para permitir dinámicamente IPs de redes locales (192.168.x.x, 10.x.x.x, 172.16-31.x.x)
- Habilitación de CORS_ALLOW_CREDENTIALS para soporte de autenticación con cookies
- Configuración completa de CORS_ALLOW_HEADERS incluyendo authorization, content-type, y x-csrftoken
- Definición de todos los métodos HTTP permitidos en CORS_ALLOW_METHODS (GET, POST, PUT, DELETE, PATCH, OPTIONS)

Frontend: Se ha implementado detección automática de entorno para usar URLs de API correctas:
- Creación de función getBaseUrl() en api.ts que detecta si el acceso es a través de nginx (puerto 80) o directo (puerto 3000)
- Uso de rutas relativas (/api) cuando se accede a través de nginx para evitar problemas de CORS
- Fallback a http://localhost:8000/api para desarrollo local sin nginx
- Soporte para Server-Side Rendering con detección de entorno servidor/cliente

Frontend: Se ha actualizado el componente LewisStructureGenerator para usar URLs dinámicas:
- Implementación de función helper getApiUrl() para determinar la URL base correcta
- Actualización de todas las llamadas fetch para usar URLs dinámicas en lugar de hardcodeadas
- Soporte completo para acceso desde dispositivos externos sin errores de CORS

Documentation: Se ha creado documentación completa para la configuración de Nginx:
- README.md en docker/nginx/ con instrucciones detalladas de uso
- Guía de acceso desde dispositivos externos con ejemplos de IPs
- Instrucciones de configuración de firewall para Windows, Linux y macOS
- Tabla de rutas y endpoints disponibles a través del proxy
- Sección de solución de problemas comunes
- Recomendaciones de seguridad para producción

Improved
Docker: Se ha actualizado docker-compose.yml para incluir el servicio de nginx:
- Definición del servicio nginx con build desde docker/nginx/
- Mapeo del puerto 80 del host al puerto 80 del contenedor
- Configuración de dependencias para asegurar que backend y frontend estén listos
- Montaje de volúmenes para configuración y logs
- Política de reinicio unless-stopped para alta disponibilidad

Frontend: Se ha mejorado la robustez del servicio de API:
- Detección inteligente del entorno de ejecución (desarrollo vs producción)
- Manejo automático de diferentes configuraciones de red
- Compatibilidad mejorada con dispositivos móviles y tablets

Changed
Backend: Se ha modificado la configuración de CORS de una lista estática a un sistema dinámico que acepta orígenes basados en patrones regex, permitiendo mayor flexibilidad para redes locales.

Frontend: Se han actualizado todas las llamadas a la API para usar URLs dinámicas en lugar de URLs hardcodeadas a localhost:8000, mejorando la portabilidad del código.

Fixed
Frontend: Se ha corregido el error "Failed to fetch" que ocurría al acceder desde dispositivos externos debido a que el frontend intentaba conectarse a localhost:8000 en lugar de usar rutas relativas.

Infrastructure: Se ha solucionado el problema de configuración de nginx donde la directiva add_header dentro del bloque if causaba errores de sintaxis, moviendo los headers CORS al contexto correcto.

Security
Backend: Se han agregado notas y comentarios en settings.py indicando que las configuraciones permisivas de CORS y ALLOWED_HOSTS son solo para desarrollo y deben ser restringidas en producción.

Documentation: Se han incluido advertencias de seguridad en el README de nginx sobre la importancia de restringir accesos y usar HTTPS en entornos de producción.

[2.3.0-alpha] - 2025-08-13

Added
Backend: Se ha expandido significativamente el generador de estructuras de Lewis con soporte para más de 100 moléculas incluyendo:
- Moléculas inorgánicas simples (H2O, NH3, CO2, SO2, NO2, etc.)
- Serie completa de alcanos (CH4 hasta C6H14)
- Alcenos y alquinos (C2H4, C2H2, C3H4, etc.)
- Alcoholes y éteres (CH3OH, C2H5OH, dimethyl ether, etc.)
- Aldehídos, cetonas y ácidos carboxílicos
- Compuestos halogenados (CF4, CHCl3, CCl4, etc.)
- Compuestos aromáticos (benceno, tolueno, fenol, anilina)
- Compuestos de fósforo (PCl3, PCl5, PF3, PF5, POCl3)
- Compuestos de boro (BF3, BCl3, BH3, B2H6)
- Compuestos de azufre (SF4, SF6, H2SO4, SCl2)
- Compuestos de gases nobles (XeF2, XeF4, XeF6, XeO3)
- Compuestos interesantes (ClF3, IF5, IF7, N2O, O3, H2O2)

Backend: Se ha añadido soporte para entrada directa de notación SMILES, permitiendo a usuarios avanzados generar estructuras de Lewis para cualquier molécula compatible introduciendo su cadena SMILES.

Backend: Se ha implementado generación automática de coordenadas 2D usando RDKit AllChem.Compute2DCoords() para mejor visualización de las estructuras moleculares.

Frontend: Se ha refactorizado completamente el componente LewisStructureGenerator para conectar con el backend real:
- Eliminación de datos mock hardcodeados (solo 3 moléculas) 
- Conexión directa con el endpoint `/api/structures/lewis-generator/` que usa RDKit
- Transformación automática de respuestas del backend al formato esperado por el frontend
- Manejo robusto de errores con mensajes informativos para el usuario

Frontend: Se ha implementado un sistema de categorías para selección rápida de moléculas:
- Moléculas Simples (H2O, NH3, CH4, CO2, HCl, HF, H2S)
- Hidrocarburos (C2H6, C2H4, C2H2, C3H8, C6H6)
- Alcoholes y Éteres (CH3OH, C2H5OH, CH2O, C3H6O)
- Compuestos de P/S (PH3, PCl3, SO2, SF6, H2SO4)
- Compuestos de Halógenos (BF3, ClF3, CF4, XeF4, IF5)
- Otros (NO2, N2O, O3, H2O2)

Frontend: Se ha añadido visualización de estructuras recientes generadas:
- Fetch automático de las últimas 5 estructuras desde `/api/structures/`
- Botones de acceso rápido con fecha de creación
- Carga instantánea de estructuras previamente generadas
- Actualización dinámica de la lista tras cada nueva generación

Frontend: Se ha integrado completamente el sistema de notificaciones en los componentes de structures y reactions:
- LewisStructureGenerator: notificaciones para validación, generación exitosa/fallida, selección de moléculas
- ReactionSimulator: notificaciones para balanceo, errores, limpieza y selección de ejemplos
- Dispatch de acciones Redux con addNotification para feedback consistente

Testing: Se ha creado script test_lewis_structures.py para validación exhaustiva del sistema:
- Pruebas automatizadas de más de 25 moléculas diferentes por categorías
- Verificación de generación exitosa con datos completos (peso molecular, electrones de valencia, átomos, enlaces)
- Detección de estructuras cacheadas vs nuevas generaciones
- Prueba de entrada SMILES directa
- Resumen detallado con tasas de éxito y estadísticas

Backend: Se ha implementado soporte completo para compuestos iónicos en el generador de estructuras:
- Detección automática de compuestos iónicos (NaCl, CaCO3, Fe2O3, CuSO4, etc.)
- Generación especializada de estructuras sin enlaces covalentes para compuestos iónicos
- Manejo robusto de variantes de fórmulas de PubChem (ej: CCaO3 para CaCO3)
- Soporte para más de 40 compuestos iónicos comunes incluidos óxidos metálicos, carbonatos, sulfatos, nitrates e hidróxidos

Frontend: Se ha integrado la API de PubChem para búsqueda avanzada de compuestos:
- Búsqueda multiidioma con traducción automática de nombres (español/inglés)
- Detección automática del tipo de consulta (nombre, fórmula, SMILES, InChI)
- Cache local de búsquedas frecuentes para mejorar rendimiento
- Visualización de nombres comunes y propiedades de compuestos desde PubChem
- Sistema de compuestos recientes y cacheados con acceso rápido

Frontend: Se ha mejorado significativamente el renderizado de estructuras de Lewis:
- Algoritmo inteligente de posicionamiento de pares solitarios que evita superposiciones
- Soporte para renderizado con Kekule.js como opción avanzada
- Diferenciación visual entre enlaces simples, dobles y triples
- Visualización de cargas formales en átomos
- Layouts optimizados para moléculas simples con coordenadas hardcodeadas

Backend: Se han agregado estructuras hardcodeadas para moléculas simples comunes:
- Más de 20 moléculas simples con coordenadas optimizadas (H2O, NH3, CH4, CO2, etc.)
- Mapeo de variantes de fórmulas (H3N → NH3, ClH → HCl, O2S → SO2)
- Generación rápida sin cálculos de RDKit para estructuras conocidas
- Mejora significativa en tiempo de respuesta para moléculas frecuentes

Frontend: Se ha implementado el sistema de notificaciones global en todos los juegos:
- Integración completa en BalanceChallengeGame con notificaciones para inicios, intentos, pistas y completado
- Integración en PeriodicSpeedGame con feedback para selecciones correctas/incorrectas y pistas
- Tipos de notificación diferenciados (success, error, info) con estilos visuales únicos
- Sistema centralizado de Redux para gestión de notificaciones en toda la aplicación

Improved
Documentación: Se han mejorado significativamente los docstrings de todas las vistas del backend:
- games/views.py: documentación detallada de endpoints de Quiz, ChemWordle, Memory, BalanceChallenge y PeriodicSpeed
- structures/views.py: documentación completa de endpoints de generación de estructuras de Lewis
- reactions/views.py: documentación mejorada de endpoints de balanceo de ecuaciones
- Formato consistente con descripción, parámetros, respuestas JSON esperadas y errores posibles
- Ejemplos de uso y notas importantes para cada endpoint

Performance: Se ha optimizado el sistema de generación de estructuras:
- Caché automático en base de datos para estructuras ya generadas
- Respuesta instantánea (200 OK) para estructuras existentes
- Generación nueva (201 Created) solo cuando es necesario
- Reducción significativa de carga computacional para moléculas frecuentes

Changed
Arquitectura: Se ha eliminado la dependencia de datos mock en el frontend para estructuras de Lewis, estableciendo conexión directa con el backend basado en RDKit para cálculos químicos reales.

UX: Se ha reorganizado la interfaz de selección rápida de moléculas de una lista plana a categorías organizadas, mejorando la navegabilidad y descubrimiento de opciones.

Fixed
Backend: Se han corregido mensajes de error en el generador de estructuras para proporcionar feedback más útil, incluyendo lista de moléculas soportadas cuando se intenta generar una no disponible.

Frontend: Se ha corregido el manejo de estados para evitar conflictos entre estructuras cacheadas y nuevas generaciones, asegurando que la UI refleje correctamente el origen de los datos.

[2.2.5-alpha] - 2025-08-11

Added
Backend: Se ha implementado el sistema completo de Tabla Periódica Rápida mediante la expansión de la app games, proporcionando una experiencia de velocidad y precisión para identificar elementos químicos.

Frontend: Se ha desarrollado la interfaz completa del juego Periodic Speed en Next.js con los siguientes componentes:
- Página principal (/periodic-speed) integrada con el sistema de navegación de ChemsTools
- Componente principal PeriodicSpeedGame.tsx que gestiona todo el flujo del juego, estados y comunicación con la API
- Tabla periódica interactiva (PeriodicTable.tsx) con elementos seleccionables y efectos visuales de hover
- Display del elemento objetivo (ElementDisplay.tsx) mostrando símbolo, nombre y propiedades químicas
- Temporizador en tiempo real (GameTimer.tsx) con tracking preciso del tiempo de respuesta
- Panel de estadísticas (GameStats.tsx) con métricas de rendimiento del jugador
- Pantalla de resultados (GameResults.tsx) con feedback detallado tras cada intento

Frontend: Se ha implementado la lógica completa del juego en el cliente:
- Sistema de selección de dificultad (aleatorio, común, raro) antes de iniciar cada desafío
- Mecánica de selección de elementos mediante click en la tabla periódica interactiva
- Validación inmediata de respuestas con feedback visual (correcto/incorrecto)
- Sistema de pistas contextuales integrado con botón dedicado y display de información
- Gestión de estados de juego (inicio, jugando, completado) con transiciones suaves
- Cálculo y display del tiempo transcurrido con precisión de décimas de segundo
- Integración completa con el sistema de autenticación existente

Frontend: Se ha creado una experiencia de usuario optimizada:
- Interfaz responsive adaptable a diferentes tamaños de pantalla
- Animaciones fluidas con Framer Motion para transiciones y feedback visual
- Iconografía consistente con lucide-react (Trophy, Zap, Clock, Target, Brain)
- Diseño visual con gradientes temáticos y componentes modernos
- Estados de carga claros durante las operaciones asíncronas
- Manejo robusto de errores con mensajes informativos para el usuario

Backend: Se han creado 2 modelos especializados para el sistema Periodic Speed Challenge:
- PeriodicSpeedGame: Gestiona sesiones individuales con elemento objetivo, estado de finalización, tiempo de respuesta, elemento seleccionado por el usuario, y uso de pistas
- PeriodicSpeedStats: Sistema de estadísticas persistentes por usuario con métricas generales (precisión, mejores tiempos, rachas), estadísticas por categoría de elementos (metales, no metales, metaloides, gases nobles), y tiempos récord por tipo de elemento

Backend: Se ha desarrollado la clase PeriodicSpeedEngine que implementa la lógica completa del juego de velocidad periódica:
- Sistema de generación de desafíos categorizados por dificultad (aleatorio: todos los elementos, común: primeros 20 + elementos conocidos, raro: elementos pesados y lantánidos/actínidos)
- Algoritmo de validación de selecciones con verificación de elemento correcto y medición precisa de tiempo de respuesta
- Sistema de puntuación y gestión de rachas con límites configurables y tracking de mejores tiempos
- Gestión automática de finalización de desafíos y actualización de estadísticas al completar intentos
- Sistema de pistas contextuales basadas en propiedades químicas (categoría, período, rango de número atómico)

Backend: Se han implementado 8 endpoints REST especializados para Periodic Speed Challenge:
- POST /api/games/periodic-speed/start_challenge/: Inicia nuevo desafío con selección de dificultad y generación de elemento objetivo aleatorio
- POST /api/games/periodic-speed/submit_selection/: Valida selección del usuario con verificación de elemento correcto y registro de tiempo
- POST /api/games/periodic-speed/get_hint/: Sistema de pistas contextuales basadas en propiedades del elemento objetivo
- GET /api/games/periodic-speed/current_challenge/: Obtiene desafío activo del usuario con información del elemento objetivo
- GET /api/games/periodic-speed/stats/: Estadísticas detalladas del usuario (precisión, rachas, tiempos por categoría)
- GET /api/games/periodic-speed/leaderboard/: Clasificación global basada en mejor tiempo y tasa de precisión
- GET /api/games/periodic-speed/periodic_table/: Datos completos de la tabla periódica para referencia del frontend
- GET /api/games/periodic-speed/practice_elements/: Elementos aleatorios para práctica con filtrado por dificultad
- DELETE /api/games/periodic-speed/end_challenge/: Permite abandonar desafío activo con actualización de estadísticas

Backend: Se ha integrado el sistema de Periodic Speed Challenge con los datos existentes de la tabla periódica de la app data para:
- Reutilización de los datos de elementos químicos del archivo periodic_table.json
- Validación robusta de elementos seleccionados usando número atómico como identificador único
- Generación automática de pistas basadas en propiedades químicas (categoría, posición en tabla)
- Clasificación inteligente de elementos por categorías para estadísticas detalladas

Testing: Se ha implementado una suite exhaustiva de 25+ pruebas unitarias y de integración que valida:
- Carga correcta de datos de tabla periódica y funcionamiento del motor de juego con diferentes dificultades
- Algoritmo de validación de selecciones y detección de elementos correctos con casos edge complejos
- Funcionamiento correcto de todos los endpoints de la API con validación de respuestas JSON
- Flujo completo desde inicio hasta finalización de desafío con actualización de estadísticas
- Manejo de errores para casos inválidos (números de elemento fuera de rango, juegos completados, tiempos inválidos)
- Sistema de pistas progresivas y gestión de hints utilizados por usuario
- Continuación de desafíos existentes y prevención de duplicados activos

Testing: Se han implementado 2 comandos de management para debugging y testing:
- debug_periodic_speed: Valida funcionamiento completo del sistema con creación de usuario de prueba y ejecución de flujo completo
- test_periodic_elements: Verifica carga y categorización correcta de elementos de la tabla periódica

Changed
Arquitectura: Se ha expandido el patrón modular de la app games para soportar Periodic Speed Challenge como quinto tipo de juego, manteniendo separación clara entre motores de juego, modelos y presentación API.

Backend: Se ha optimizado la reutilización de los datos de tabla periódica existentes para crear un sistema de validación robusto que aprovecha la información química ya implementada sin duplicar código.

Infrastructure: Se ha actualizado la configuración de routing para soportar Quiz, ChemWordle, Memory, Balance Challenge y Periodic Speed de manera independiente, expandiendo el router de games sin conflictos.

Performance: Se ha implementado gestión de estado de elementos optimizada que minimiza consultas a datos y proporciona respuesta inmediata para validación de selecciones del usuario.

Fixed
Backend: Se han corregido problemas en la validación de elementos para manejar correctamente casos edge como números atómicos fuera de rango y elementos inexistentes.

Testing: Se han corregido 2 fallos en las pruebas unitarias relacionados con validación de tiempos de respuesta y manejo de estadísticas para usuarios nuevos en Periodic Speed Challenge.

Backend: Se ha corregido el manejo de estadísticas para usuarios nuevos en Periodic Speed Challenge, implementando valores por defecto apropiados y evitando errores de referencia nula en consultas de leaderboard.

Security: Se ha implementado validación adicional en endpoints de Periodic Speed Challenge para verificar ownership de desafíos y prevenir acceso no autorizado a datos de juegos de otros usuarios.

UX: Se han corregido problemas de categorización de elementos para proporcionar estadísticas precisas por tipo de elemento (metales, no metales, metaloides, gases nobles) basadas en las categorías químicas estándar.

[2.2.4-alpha] - 2025-08-10

Added
Backend: Se ha implementado el sistema completo de Balance Challenge (Desafío de Balanceo) mediante la expansión de la app games, proporcionando una experiencia interactiva de drag & drop para balancear ecuaciones químicas.

Backend: Se han creado 3 modelos especializados para el sistema Balance Challenge:
- BalanceChallengeGame: Gestiona sesiones individuales con ecuación original, coeficientes objetivo, estado de finalización, número de intentos, dificultad seleccionada, y sistema de pistas utilizadas
- BalanceChallengeAttempt: Registra cada intento individual con coeficientes enviados, validación de corrección, resultado detallado de balanceo, y tiempo de respuesta
- BalanceChallengeStats: Sistema de estadísticas persistentes por usuario con métricas por dificultad (fácil/medio/difícil), rachas actuales y mejores, tiempos promedio y mejores por nivel, y tasa de precisión global

Backend: Se ha desarrollado la clase BalanceChallengeEngine que implementa la lógica completa del juego de balanceo:
- Sistema de generación de ecuaciones químicas categorizadas por dificultad (fácil: síntesis simple, medio: combustión y ácido-base, difícil: redox y complejas)
- Algoritmo de validación de coeficientes con verificación de balance químico y coincidencia exacta con solución objetivo
- Sistema de puntuación y gestión de intentos con límites configurables por dificultad
- Gestión automática de finalización de partidas y actualización de estadísticas al completar desafíos
- Sistema de pistas progresivas (elemento, coeficiente, método) con tracking de uso

Backend: Se han implementado 7 endpoints REST especializados para Balance Challenge:
- POST /api/games/balance-challenge/start_challenge/: Inicia nuevo desafío con selección de dificultad y generación de ecuación aleatoria
- POST /api/games/balance-challenge/submit_coefficients/: Valida coeficientes del usuario con verificación de balance químico completo
- POST /api/games/balance-challenge/get_hint/: Sistema de pistas contextuales (general, coeficiente específico, método de balanceo)
- GET /api/games/balance-challenge/current_challenge/: Obtiene desafío activo del usuario con estado completo
- GET /api/games/balance-challenge/stats/: Estadísticas detalladas del usuario (precisión, rachas, tiempos por dificultad)
- GET /api/games/balance-challenge/leaderboard/: Clasificación global basada en tasa de precisión y rachas
- DELETE /api/games/balance-challenge/end_challenge/: Permite abandonar desafío activo con actualización de estadísticas

Backend: Se ha integrado el sistema de Balance Challenge con ChemicalEquationBalancer existente para:
- Reutilización de la lógica de balanceo de ecuaciones químicas de la app reactions
- Validación robusta de ecuaciones balanceadas usando SymPy para cálculos algebraicos
- Generación automática de ecuaciones objetivo con coeficientes mínimos
- Parsing inteligente de compuestos químicos para extracción de reactivos y productos

Frontend: Se ha desarrollado el componente BalanceChallengeGame.tsx con mecánicas completas de drag & drop:
- Sistema de drag & drop nativo sin dependencias externas para coeficientes numéricos
- Pool de números disponibles (1-10) con múltiples copias para reutilización flexible
- Interfaz visual de ecuaciones químicas con slots para coeficientes arrastrables
- Feedback visual inmediato con colores diferenciados (verde=correcto, azul=arrastrable, gris=vacío)
- Estados de juego diferenciados (menú, jugando, completado, estadísticas) con transiciones suaves

Frontend: Se ha implementado el componente de estadísticas avanzadas con visualización completa:
- Dashboard de estadísticas personales con métricas clave (precisión, rachas, tiempos)
- Distribución de rendimiento por dificultad con estadísticas detalladas de fácil/medio/difícil
- Visualización de mejores tiempos por nivel y tiempo promedio general
- Interface responsive con diseño de tarjetas informativas y gradientes temáticos

Frontend: Se ha creado el store slice balanceChallengeSlice.ts con gestión de estado completa:
- Estado global reactivo para desafío actual, estadísticas, clasificación y progreso
- Thunks asíncronos para todas las operaciones de API con manejo robusto de errores y loading states
- Reducers especializados para gestión de pistas, feedback y estados de juego
- Integración automática con el sistema de autenticación y manejo de tokens JWT
- Estados de error centralizados con funciones de limpieza y reset

Frontend: Se ha desarrollado la página completa /balance-challenge con:
- Sistema de navegación integrado en el header principal de ChemsTools
- Protección de ruta que requiere autenticación con manejo de estados de carga
- Diseño responsive con gradientes temáticos y componentes modernos accesibles
- Integración completa con Redux para gestión de estado persistente
- Experiencia de usuario fluida con transiciones y animaciones CSS

Testing: Se ha implementado una suite exhaustiva de 25+ pruebas unitarias y de integración que valida:
- Creación y configuración correcta de desafíos de balance con diferentes dificultades
- Algoritmo de validación de coeficientes y detección de ecuaciones balanceadas con casos edge complejos
- Funcionamiento correcto de todos los endpoints de la API con validación de respuestas JSON
- Flujo completo desde inicio hasta finalización de desafío con actualización de estadísticas
- Manejo de errores para casos inválidos (coeficientes negativos, longitud incorrecta, juegos completados)
- Sistema de pistas progresivas y gestión de hints utilizados por usuario
- Continuación de desafíos existentes y prevención de duplicados activos

Changed
Arquitectura: Se ha expandido el patrón modular de la app games para soportar Balance Challenge como cuarto tipo de juego, manteniendo separación clara entre motores de juego, modelos y presentación API.

Frontend: Se ha actualizado el sistema de navegación global para incluir Balance Challenge como juego independiente, diferenciándolo visualmente de Quiz, ChemWordle y Memory con iconografía específica (⚖️).

Backend: Se ha optimizado la reutilización del ChemicalEquationBalancer existente para crear un sistema de validación robusto que aprovecha la lógica de balanceo ya implementada sin duplicar código.

Infrastructure: Se ha actualizado la configuración de routing para soportar Quiz, ChemWordle, Memory y Balance Challenge de manera independiente, expandiendo el router de games sin conflictos.

Performance: Se ha implementado gestión de estado de drag & drop optimizada que minimiza re-renders innecesarios y proporciona feedback visual inmediato durante las interacciones del usuario.

Fixed
Backend: Se han corregido problemas en la validación de coeficientes para manejar correctamente casos edge como ecuaciones ya balanceadas con múltiplos y coeficientes mínimos vs. equivalentes.

Frontend: Se han solucionado conflictos potenciales de estado entre diferentes juegos de la app games, asegurando que el estado de Balance Challenge se mantenga aislado y consistente.

Testing: Se han corregido 3 fallos en las pruebas unitarias relacionados con validación de ecuaciones complejas y manejo de respuestas de API en endpoints de estadísticas y clasificación.

Backend: Se ha corregido el manejo de estadísticas para usuarios nuevos en Balance Challenge, implementando valores por defecto apropiados y evitando errores de referencia nula en consultas de leaderboard.

Frontend: Se han solucionado problemas de tipado TypeScript en componentes de Balance Challenge, asegurando compatibilidad completa con las interfaces definidas en el store slice y tipos del backend.

Security: Se ha implementado validación adicional en endpoints de Balance Challenge para verificar ownership de desafíos y prevenir acceso no autorizado a datos de juegos de otros usuarios.

UX: Se han corregido interacciones de drag & drop para proporcionar mejor feedback visual durante el proceso de arrastrar coeficientes, incluyendo hover states y animaciones de transición suaves.

[2.2.3-alpha] - 2025-08-10

Added
Backend: Se ha implementado el sistema completo de Memory Molecular mediante la expansión de la app games, proporcionando una experiencia de memoria química educativa e interactiva.

Backend: Se han creado 2 modelos especializados para el sistema Memory Molecular:
- MemoryGame: Gestiona sesiones individuales con configuración de dificultad, tracking de progreso (pares encontrados, intentos, puntuación), datos de cartas con posiciones y estados, y sistema de tiempo de juego
- MemoryStats: Sistema de estadísticas persistentes por usuario con métricas de rendimiento (partidas jugadas, tasa de finalización, precisión promedio), mejores tiempos por dificultad, y tracking de progreso general

Backend: Se ha desarrollado la clase MemoryGameEngine que implementa la lógica completa del juego de memoria:
- Sistema de generación de cartas con datos químicos categorizados por dificultad (fácil: compuestos básicos, medio: compuestos comunes, difícil: moléculas complejas)
- Algoritmo de emparejamiento nombre-fórmula con validación de coincidencias y gestión de estados de cartas (oculta/revelada/emparejada)
- Sistema de puntuación diferenciado por dificultad (100/200/300 puntos por par en fácil/medio/difícil)
- Gestión automática de finalización de partidas y actualización de estadísticas al completar juegos
- Prevención de acciones inválidas (revelar cartas ya emparejadas, posiciones fuera de rango)

Backend: Se han implementado 7 endpoints REST especializados para Memory Molecular:
- POST /api/games/memory/start_game/: Inicia nueva partida con configuración de dificultad y número de pares
- POST /api/games/memory/reveal_card/: Revela cartas individuales con validación de coincidencias tipo memoria
- POST /api/games/memory/hide_cards/: Oculta cartas no emparejadas después del período de visualización
- GET /api/games/memory/current_game/: Obtiene partida activa del usuario con estado completo
- GET /api/games/memory/stats/: Estadísticas detalladas del usuario (rendimiento, mejores tiempos, precisión)
- GET /api/games/memory/leaderboard/: Clasificación global basada en tasa de finalización y precisión
- DELETE /api/games/memory/end_game/: Permite abandonar partida activa con actualización de estadísticas

Backend: Se ha creado un sistema de datos químicos incorporado con más de 24 compuestos distribuidos por dificultad:
- Fácil: Compuestos básicos (H₂O, CH₄, NH₃, CO₂, NaCl, HCl) con fórmulas simples y nombres conocidos
- Medio: Compuestos comunes (C₆H₁₂O₆, C₂H₅OH, H₂SO₄, NaOH, CaCO₃) con mayor complejidad química
- Difícil: Moléculas complejas (C₈H₁₀N₄O₂, C₉H₈O₄, C₆H₈O₆) incluyendo biomoléculas y fármacos

Frontend: Se ha desarrollado el componente MemoryGame.tsx con mecánicas completas de juego de memoria:
- Grid dinámico de cartas adaptativo según número de pares seleccionados
- Sistema de cartas volteables con animaciones suaves usando Framer Motion
- Diferenciación visual por tipo de carta (nombre en morado, fórmula en naranja, emparejadas en verde)
- Temporizador en tiempo real con formateo MM:SS y tracking de tiempo por partida
- Barra de progreso animada mostrando pares encontrados vs total
- Estados de juego diferenciados (configuración, jugando, verificando coincidencias, completado)

Frontend: Se ha implementado el componente MemoryGameStats.tsx con analíticas avanzadas:
- Dashboard de estadísticas personales con métricas clave (partidas, finalización, precisión)
- Tabla de mejores tiempos por dificultad con formateo inteligente de tiempo
- Clasificación global interactiva con medallas para top 3 jugadores
- Visualización de progreso con barras de progreso animadas para tasa de finalización y precisión
- Sección de ayuda integrada explicando mecánicas de juego y sistema de puntuación

Frontend: Se ha creado el store slice memorySlice.ts con gestión de estado completa:
- Estado global reactivo para partida actual, estadísticas, clasificación y progreso
- Thunks asíncronos para todas las operaciones de API con manejo robusto de errores
- Reducers especializados para gestión de cartas seleccionadas y estados de verificación
- Integración automática con el sistema de autenticación y manejo de tokens
- Estados de carga y error centralizados para toda la funcionalidad Memory

Frontend: Se ha desarrollado la página completa /memory con:
- Sistema de navegación por pestañas entre juego y estadísticas
- Protección de ruta que requiere autenticación con integración al sistema de auth
- Diseño responsive con gradientes temáticos y componentes modernos
- Callback de finalización de juego con transición automática a estadísticas
- Header actualizado con enlace dedicado a Memory Molecular

Testing: Se ha implementado una suite exhaustiva de 20+ pruebas unitarias y de integración que valida:
- Creación y configuración correcta de partidas de memory con diferentes dificultades
- Algoritmo de revelado de cartas y detección de coincidencias con casos edge complejos
- Funcionamiento correcto de todos los endpoints de la API con validación de respuestas
- Flujo completo desde inicio hasta finalización de partida con actualización de estadísticas
- Manejo de errores para casos inválidos (cartas ya emparejadas, posiciones fuera de rango)
- Continuación de partidas existentes y prevención de duplicados activos

Changed
Arquitectura: Se ha expandido el patrón modular de la app games para soportar múltiples tipos de juegos de memoria, manteniendo separación clara entre motores de juego, modelos y presentación API.

Frontend: Se ha actualizado el sistema de navegación global para incluir Memory Molecular como juego independiente, diferenciándolo visualmente de Quiz y ChemWordle con iconografía específica.

Backend: Se ha optimizado el sistema de generación de cartas mediante algoritmo de shuffle inteligente que mantiene balance entre tipos de cartas (nombre/fórmula) y asegura distribución equitativa.

Infrastructure: Se ha actualizado la configuración de routing para soportar Quiz, ChemWordle y Memory de manera independiente, expandiendo el router de games sin conflictos.

Performance: Se ha implementado gestión de estado de cartas optimizada que minimiza re-renders innecesarios y proporciona feedback visual inmediato en revelado de cartas.

Fixed
Backend: Se han corregido problemas en la validación de posiciones de cartas para manejar correctamente casos de índices fuera de rango y prevenir errores de acceso a arrays.

Frontend: Se han solucionado conflictos potenciales de estado entre diferentes componentes de Memory, asegurando que el estado de cartas se mantenga consistente durante las transiciones.

Testing: Se han corregido 2 fallos en las pruebas unitarias relacionados con generación de datos de prueba y validación de respuestas de API en endpoints de estadísticas.

Backend: Se ha corregido el manejo de estadísticas para usuarios nuevos en Memory, implementando valores por defecto apropiados y evitando errores de referencia nula.

Frontend: Se han solucionado problemas de tipado TypeScript en componentes de Memory, asegurando compatibilidad completa con las interfaces definidas en el store slice.

Security: Se ha implementado validación adicional en endpoints de Memory para verificar ownership de partidas y prevenir acceso no autorizado a datos de juegos.

UX: Se han corregido animaciones de cartas para proporcionar mejor feedback visual durante el proceso de revelado y ocultado, mejorando la experiencia de juego.

[2.2.2-alpha] - 2025-08-10
Added
Backend: Se ha implementado el sistema completo de ChemWordle (Wordle Químico) mediante la expansión de la app games, proporcionando una experiencia de adivinanza de palabras químicas educativa y entretenida.

Backend: Se han creado 4 modelos especializados para el sistema ChemWordle:
- ChemicalWord: Almacena palabras químicas categorizadas (elemento/compuesto/ion/molécula) con metadatos científicos completos (número atómico, grupo, período, estado STP, fórmula química, peso molecular)
- ChemWordleGame: Gestiona sesiones individuales con tracking de intentos, estado de finalización y sistema de pistas reveladas
- ChemWordleAttempt: Registra cada intento individual con evaluación detallada de letras (correcto/presente/ausente) y tiempo de respuesta
- ChemWordleStats: Sistema de estadísticas persistentes por usuario con distribución de victorias, rachas y clasificación global

Backend: Se ha desarrollado la clase ChemWordleEngine que implementa la lógica completa del juego estilo Wordle:
- Algoritmo de evaluación de letras fiel al estándar Wordle con manejo correcto de letras repetidas
- Sistema de validación robusta de adivinanzas (longitud, caracteres alfabéticos)
- Generación automática de pistas progresivas basadas en metadatos químicos
- Prevención de repetición de palabras mediante cache de 30 días por usuario
- Actualización automática de estadísticas y clasificaciones al completar partidas

Backend: Se han implementado 6 endpoints REST especializados para ChemWordle:
- GET /api/games/chemwordle/start_game/: Inicia nueva partida con filtrado opcional por dificultad
- POST /api/games/chemwordle/submit_guess/: Procesa adivinanzas con evaluación completa tipo Wordle
- POST /api/games/chemwordle/get_hint/: Sistema de pistas progresivas contextuales
- GET /api/games/chemwordle/stats/: Estadísticas detalladas del usuario (partidas, victorias, rachas, distribución)
- GET /api/games/chemwordle/leaderboard/: Clasificación global con criterios de desempate
- Todos los endpoints incluyen validación exhaustiva, manejo de errores y respuestas JSON estructuradas

Backend: Se ha creado el comando de management populate_chemwordle_words con más de 35 palabras químicas cuidadosamente seleccionadas:
- Elementos químicos: desde básicos (H, O, C) hasta avanzados (Cs, Ga, Re) categorizados por dificultad
- Compuestos: desde esenciales (Agua, Sal) hasta complejos (Cafeína, Aspirina, Benceno)
- Iones poliatómicos: Sulfato, Nitrato, Fosfato con información estructural
- Moléculas especiales: Ozono, con propiedades y aplicaciones detalladas

Frontend: Se ha desarrollado el componente ChemWordle.tsx con mecánicas de juego completas:
- Interfaz tipo Wordle con grid de 6 intentos y evaluación visual por colores
- Teclado virtual interactivo que refleja el estado de cada letra utilizada
- Sistema de badges por categoría química con colores distintivos
- Temporizador por intento y tracking de tiempo total de partida
- Animaciones de feedback (shake para intentos inválidos, transiciones suaves)
- Estados de juego diferenciados (inicio, jugando, completado, error) con interfaces específicas

Frontend: Se ha implementado el componente ChemWordleStats.tsx con análticas avanzadas:
- Dashboard de estadísticas personales con métricas clave (partidas, porcentaje victoria, rachas)
- Gráfico de distribución de victorias por número de intentos con barras proporcionales
- Tabla de clasificación global interactiva con medallas para top 3 jugadores
- Información educativa sobre mecánicas de juego y categorías químicas
- Formateo inteligente de tiempos y porcentajes con precisión decimal

Frontend: Se ha creado el store slice chemWordleSlice.ts con gestión de estado completa:
- Estado global reactivo para sesión actual, progreso, teclado y estadísticas
- Thunks asíncronos para todas las operaciones de API con manejo robusto de errores
- Reducers especializados para input de letras, validación y feedback visual
- Sincronización automática del estado del teclado basado en intentos previos
- Manejo de casos edge como tiempo agotado y validación de entrada

Frontend: Se ha desarrollado la página completa /chemwordle con:
- Sistema de navegación por pestañas entre juego y estadísticas
- Protección de ruta que requiere autenticación con mensaje informativo
- Diseño responsive con gradientes temáticos y componentes modernos
- Integración completa con el sistema de navegación principal de ChemsTools
- Header actualizado con enlace dedicado a ChemWordle

Testing: Se ha implementado una suite exhaustiva de 16 pruebas unitarias y de integración que valida:
- Algoritmo de evaluación Wordle con casos complejos (letras repetidas, posiciones mixtas)
- Funcionamiento correcto de todos los endpoints de la API con casos edge
- Validación de entrada robusta (longitud, caracteres, sesiones inválidas)
- Lógica de pistas progresivas y manejo de metadatos químicos
- Flujo completo desde inicio hasta finalización de partida con estadísticas
- Comando de debugging para verificación de estado del sistema

Changed
Arquitectura: Se ha expandido el patrón modular de la app games para soportar múltiples tipos de juegos químicos, manteniendo separación clara entre motores de juego, modelos y presentación API.

Frontend: Se ha actualizado el sistema de navegación global para incluir ChemWordle como juego independiente, diferenciándolo visualmente del Quiz tradicional con iconografía específica.

Backend: Se ha optimizado el sistema de selección de palabras mediante algoritmo de cache inteligente que evita repeticiones recientes mientras mantiene distribución equitativa por dificultad.

Infrastructure: Se ha actualizado la configuración de routing para soportar tanto Quiz como ChemWordle de manera independiente, resolviendo conflictos entre App Router y Pages Router en Next.js 15.

Performance: Se ha implementado evaluación de letras optimizada con complejidad O(n) que maneja eficientemente palabras con múltiples letras repetidas.

Fixed
Backend: Se han corregido problemas en el algoritmo de evaluación de letras para manejar correctamente todos los casos de Wordle, incluyendo escenarios complejos con múltiples instancias de la misma letra.

Frontend: Se han solucionado conflictos de routing entre App Router (/app/chemwordle/page.tsx) y Pages Router (/pages/chemwordle.tsx), manteniendo únicamente la implementación de App Router para compatibilidad con Next.js 15.

Testing: Se han corregido 3 fallos en las pruebas unitarias relacionados con casos de evaluación de letras parciales, formato de requests HTTP y referencias de modelos en endpoints de estadísticas.

Backend: Se ha corregido el manejo de estadísticas para usuarios nuevos, implementando valores por defecto apropiados y evitando errores de referencia nula en consultas de clasificación.

Frontend: Se han solucionado problemas de tipado TypeScript en componentes de ChemWordle, asegurando compatibilidad completa con las interfaces definidas en el store slice.

Security: Se ha implementado validación adicional en endpoints de pistas para prevenir solicitud de pistas en juegos completados y verificar ownership de sesiones de juego.

UX: Se han corregido animaciones de feedback visual para proporcionar mejor retroalimentación cuando se intentan adivinanzas de longitud incorrecta o con caracteres inválidos.

[2.2.1-alpha] - 2025-08-10
Added
Backend: Se ha implementado el sistema completo de Quiz Rápido de Química mediante la nueva app games, proporcionando una experiencia de aprendizaje gamificada e interactiva.

Backend: Se han creado 4 modelos principales para el sistema de quiz:
- QuizQuestion: Almacena preguntas de opción múltiple categorizadas por dificultad (fácil/medio/difícil) y tema (nomenclatura, tabla periódica, reacciones, estructura atómica, estructuras de Lewis, disoluciones, pH)
- QuizSession: Gestiona sesiones individuales de quiz con tracking de progreso, puntuación y tiempo
- QuizAnswer: Registra respuestas individuales con validación de corrección, tiempo de respuesta y puntos obtenidos
- QuizLeaderboard: Sistema de clasificación global con estadísticas por usuario (mejor puntuación, promedio, tiempo más rápido, total de partidas)

Backend: Se ha desarrollado la clase QuizGameEngine que encapsula toda la lógica del motor de juego:
- Creación de sesiones con selección aleatoria de preguntas filtradas por dificultad y categoría
- Validación robusta de respuestas incluyendo manejo de casos especiales (tiempo agotado, opciones inválidas)
- Sistema de puntuación dinámica basado en dificultad de pregunta y corrección de respuesta
- Actualización automática de estadísticas y clasificaciones al completar sesiones

Backend: Se han implementado 6 endpoints REST completos para el sistema de quiz:
- POST /api/games/quiz/start_session/: Inicia nuevas sesiones con parámetros opcionales de filtrado
- GET /api/games/quiz/get_question/: Obtiene la pregunta actual de una sesión activa
- POST /api/games/quiz/submit_answer/: Procesa respuestas con validación completa y feedback inmediato
- GET /api/games/quiz/leaderboard/: Consulta clasificación global top 10
- GET /api/games/quiz/my_stats/: Obtiene estadísticas personales del usuario autenticado
- Todos los endpoints incluyen validación de datos, manejo de errores robusto y respuestas JSON estructuradas

Backend: Se ha creado el comando de management populate_quiz_questions que incluye más de 30 preguntas de ejemplo cuidadosamente diseñadas, cubriendo todos los temas principales de química con explicaciones educativas detalladas.

Frontend: Se ha desarrollado el componente QuizGame.tsx con funcionalidades avanzadas:
- Sistema de temporizador visual con alertas cuando quedan menos de 30 segundos
- Selección de modalidades de juego (aleatorio, por dificultad: fácil/medio/difícil)
- Interfaz de selección de respuestas con feedback visual inmediato
- Barra de progreso animada mostrando avance a través de las preguntas
- Estados de UI diferenciados (inicio, carga, jugando, respondiendo, completado, error)
- Feedback educativo después de cada respuesta con explicación de la respuesta correcta
- Pantalla de resultados finales con resumen de puntuación y opciones de continuación

Frontend: Se ha implementado el componente QuizLeaderboard.tsx que presenta:
- Tabla de clasificación interactiva con top 10 jugadores globales
- Medallas visuales (🥇🥈🥉) para los primeros 3 lugares
- Panel de estadísticas personales del usuario con métricas detalladas (mejor puntuación, promedio, partidas jugadas, tiempo más rápido)
- Formateo inteligente de tiempo en formato MM:SS
- Design responsive con grillas adaptativas

Frontend: Se ha creado el store slice quizSlice.ts con Redux Toolkit que gestiona:
- Estado global completo del quiz (sesión actual, pregunta, progreso, puntuación, temporizador)
- Thunks asíncronos para todas las operaciones de API con manejo robusto de errores
- Estados de UI reactivos que se sincronizan automáticamente con las acciones del usuario
- Reducers para operaciones locales (reset, actualización de tiempo, cambio de estados)

Frontend: Se ha desarrollado la página completa /quiz con:
- Sistema de navegación por pestañas entre juego y clasificación
- Protección de ruta que requiere autenticación
- Integración completa con el sistema de navegación existente
- Design consistente con el resto de la aplicación ChemsTools

Testing: Se ha implementado una suite exhaustiva de 8 pruebas unitarias y de integración para el backend que valida:
- Funcionamiento correcto de todos los endpoints de la API
- Flujo completo desde inicio de sesión hasta finalización de quiz
- Manejo apropiado de casos de error (sesiones inválidas, preguntas inexistentes, datos malformados)
- Validación de lógica de puntuación y actualización de estadísticas
- Casos edge como tiempo agotado y respuestas fuera de rango

Changed
Arquitectura: Se ha adoptado un patrón de separación clara entre motor de juego (QuizGameEngine), modelos de datos, y presentación de API, facilitando futuras extensiones del sistema de quiz.

Frontend: Se ha mejorado el manejo de estados asíncronos en Redux con verificaciones de seguridad para evitar errores de propiedades undefined, incluyendo logging detallado para debugging.

Backend: Se ha optimizado el sistema de validación de respuestas para soportar casos especiales como tiempo agotado (-1) manteniendo la integridad de datos.

Infrastructure: Se ha actualizado la configuración del proyecto para incluir la nueva app games en INSTALLED_APPS y routing de URLs.

Fixed
Backend: Se han corregido problemas de validación en la lógica de selección de respuestas, asegurando que todos los índices de opciones sean válidos antes del procesamiento.

Frontend: Se han solucionado errores de tipado TypeScript relacionados con importaciones de store y manejo de propiedades de componentes, garantizando compilación sin warnings.

Frontend: Se ha corregido el manejo de respuestas de API en el frontend para adaptarse correctamente a la estructura de respuesta del backend ({ success: boolean, data: {...} }).

Testing: Se han resuelto fallos en las pruebas relacionados con validación de datos de entrada y formato de respuestas JSON, alcanzando 100% de éxito en la suite de pruebas.

Performance: Se ha optimizado la consulta de preguntas aleatorias utilizando random.sample() en lugar de operaciones de base de datos múltiples, mejorando significativamente los tiempos de respuesta.

[2.2.0-alpha] - 2025-08-09
Added
Backend: Se ha implementado la funcionalidad completa del Simulador de Reacciones Químicas en la nueva app reactions.
Backend: Se ha creado el modelo BalancedReaction para actuar como caché y historial en la base de datos, almacenando las ecuaciones balanceadas para optimizar peticiones futuras y permitir análisis de uso.
Backend: Se ha desarrollado la clase ChemicalEquationBalancer en reactions/utils.py, que encapsula toda la lógica de balanceo algebraico utilizando SymPy para:

Parsing inteligente de ecuaciones químicas con soporte para compuestos complejos con paréntesis (ej. Ca(OH)2)
Balanceo automático mediante resolución de sistemas de ecuaciones lineales
Clasificación automática del tipo de reacción (síntesis, descomposición, combustión, sustitución)
Cálculo y normalización de coeficientes estequiométricos

Backend: Se ha implementado el endpoint POST /api/reactions/balance-equation/ que recibe ecuaciones no balanceadas y devuelve:

Ecuación balanceada completa
Coeficientes organizados por reactivos y productos
Tipo de reacción detectado automáticamente
Mapeo detallado de coeficientes por compuesto

Backend: Se han añadido endpoints auxiliares:

GET /api/reactions/health/ para verificación del estado del servicio
GET /api/reactions/balanced-reactions/ para consultar el historial de reacciones procesadas

Backend: Se ha implementado una suite exhaustiva de 19 pruebas unitarias y de integración que validan:

Parsing correcto de compuestos simples y complejos
Balanceo preciso para los tres tipos principales de reacciones químicas
Manejo robusto de errores y validaciones de entrada
Funcionamiento completo de todos los endpoints de la API
Almacenamiento correcto en base de datos

Frontend: Se ha desarrollado el componente avanzado ReactionSimulator.tsx con TypeScript completo, que incluye:

Interfaz de usuario intuitiva y responsive con TailwindCSS
Validación de ecuaciones en tiempo real con mensajes de error específicos
Botones de selección rápida para tipos de reacciones comunes (síntesis, descomposición, combustión)
Estados visuales claros para carga, éxito y error con animaciones suaves
Visualización detallada de resultados incluyendo ecuación balanceada, coeficientes por compuesto, y tipo de reacción
Manejo robusto de errores de red y respuestas del servidor
Funcionalidad de limpieza y reset completo del formulario

Frontend: Se ha integrado la configuración completa de Axios con interceptores para:

Logging automático de requests y responses para debugging
Manejo centralizado de timeouts (10 segundos)
Headers estándar y configuración de base URL por ambiente

Changed
Arquitectura: Se ha adoptado un enfoque de separación clara entre lógica de negocio (utils.py), modelos de datos (models.py) y presentación (views.py), mejorando la mantenibilidad y testabilidad del código.
Dependencias: Se ha integrado SymPy como nueva dependencia del backend para cálculo simbólico avanzado, permitiendo el balanceo algebraico preciso de ecuaciones químicas complejas.
API Design: Se ha establecido un patrón consistente de respuestas JSON estructuradas que incluyen:

Campo success booleano para identificación rápida del estado
Datos originales y procesados para trazabilidad completa
Información de metadata (tipo de reacción, ID de base de datos)
Manejo unificado de errores con mensajes descriptivos

Fixed
Backend: Se ha corrigido el parsing de compuestos químicos complejos con paréntesis mediante la implementación de un algoritmo recursivo que expande correctamente grupos como (OH)2, (NO3)3, etc.
Testing: Se han solucionado problemas de importación relativa en la suite de pruebas, migrando de imports relativos (..models) a imports absolutos (reactions.models) para mayor compatibilidad con pytest.

[2.1.0-alpha] - 2025-08-09
Added
Backend: Se ha implementado la funcionalidad completa del Generador de Estructuras de Lewis en la nueva app structures.

Backend: Se ha creado el modelo MolecularStructure para actuar como caché en la base de datos, almacenando las estructuras generadas para optimizar peticiones futuras.

Backend: Se ha desarrollado la clase LewisStructureGenerator en structures/utils.py, que encapsula toda la lógica de negocio con RDKit para el análisis de fórmulas, cálculo de propiedades y generación de estructuras.

Backend: Se ha implementado el endpoint POST /api/structures/lewis-generator/ que devuelve una representación JSON detallada de la estructura de Lewis, incluyendo átomos, enlaces, cargas formales y pares libres.

Backend: Se ha añadido una suite de pruebas unitarias y de integración exhaustiva para el nuevo módulo, validando la lógica de RDKit, el modelo de datos y los endpoints de la API.

Frontend: Se ha desarrollado un nuevo componente LewisStructureGenerator.tsx con una interfaz de usuario avanzada, incluyendo:

Validación de fórmulas en tiempo real.

Botones de selección rápida para moléculas comunes.

Un renderizador de canvas personalizado para visualizar las estructuras de Lewis, mostrando átomos, enlaces y pares de electrones.

Una vista detallada de las propiedades moleculares y atómicas calculadas.

Changed
Arquitectura: Se ha adoptado un enfoque basado en un servicio (utils.py) y un modelo de caché (models.py) para el generador de estructuras, en lugar de una lógica puramente transitoria, mejorando el rendimiento y la organización del código.

[2.0.0-alpha] - 2025-07-28
Added
Backend: Se han creado dos nuevas aplicaciones de Django, structures y reactions, para organizar la lógica de las futuras funcionalidades de análisis molecular y de reacciones.

Backend: Se han integrado las librerías científicas rdkit-pypi (para manipulación de moléculas) y sympy (para cálculo simbólico) al proyecto.

Frontend: Se ha añadido la librería kekule al proyecto como dependencia de npm, seleccionada para la futura visualización de estructuras químicas en 2D.

Changed
Backend: Se actualizó requirements.txt para incluir las nuevas dependencias rdkit-pypi y sympy.

Backend: Se modificó chems_tools/settings.py para registrar las nuevas aplicaciones structures y reactions.

DevOps: Se ha verificado que el pipeline de CI existente en GitHub Actions maneja correctamente la instalación de las nuevas dependencias del backend.

[1.3.0-alpha] - 2025-07-27
Added
Documentación: Se ha añadido una nueva sección a USER_GUIDE.md que explica en detalle el funcionamiento del Glosario de Términos Químicos, la Calculadora de pH/pOH y la Calculadora de Disoluciones.

Documentación: Se han mejorado los docstrings en las vistas del backend (calculators/views.py) para enriquecer la documentación autogenerada de la API en Swagger/Redoc, haciéndola más clara para los desarrolladores.

Changed
Frontend: Se ha integrado el sistema de notificaciones global (basado en Redux) en los componentes PHCalculator y SolutionCalculator. Ahora, los usuarios reciben un feedback visual consistente (éxito o error) después de cada operación.

Backend: Se ha revisado el código de los nuevos módulos (calculators) para asegurar la adherencia a los estándares del proyecto. El rendimiento de los endpoints se considera óptimo para la carga actual y no ha requerido optimizaciones adicionales.

UI/UX: Se ha realizado una revisión general de la usabilidad de las nuevas herramientas, confirmando que el diseño actual es intuitivo y no requiere ajustes mayores en esta fase.

[1.2.0-alpha] - 2025-07-27
Added
Backend: Se desarrolló el endpoint calculators/solution-calculator/ con lógica para calcular % m/m y % m/v, incluyendo derivaciones a partir de la densidad.

Backend: Se implementó una validación robusta en la SolutionCalculatorView para manejar entradas numéricas inválidas (negativas, cero donde no corresponde) y datos insuficientes.

Backend: Se ampliaron las pruebas unitarias en calculators/tests/test_views.py para cubrir todos los casos de uso y de error de la nueva calculadora de disoluciones.

Frontend: Se creó un nuevo slice de Redux (calculatorsSlice.ts) para gestionar de forma centralizada el estado de los formularios de las calculadoras.

Frontend: Se diseñó y desarrolló el componente interactivo SolutionCalculator.tsx, conectándolo al nuevo slice de Redux y al endpoint del backend.

Fixed
Backend: Se corrigió la estructura del archivo de pruebas calculators/tests/test_views.py, moviendo los métodos de prueba de la calculadora de disoluciones dentro de la clase CalculatorsAPITests para resolver los errores de fixture 'self' not found.

Backend: Se refactorizó la prueba test_get_glossary_list para crear sus propios datos de prueba en setUpTestData, haciéndola independiente de las migraciones de datos y solucionando el fallo de aserción.

[1.1.0-alpha] - 2025-07-27
Added
Backend: Se implementó un BaseModel abstracto en la app core con campos de auditoría (created_at, updated_at) para estandarizar los modelos.

Backend: Se creó el modelo GlossaryTerm y su correspondiente Serializer y ViewSet para la nueva funcionalidad de Glosario.

Backend: Se añadió un endpoint para la pHCalculatorView, capaz de realizar conversiones entre pH, pOH, [H+] y [OH-].

Backend: Se implementó caché con Redis en el endpoint del glosario para optimizar el rendimiento.

Backend: Se añadieron pruebas unitarias para los nuevos endpoints de la app calculators.

Frontend: Se desarrolló la página del Glosario (/glossary) con funcionalidad de búsqueda y filtrado en el cliente.

Frontend: Se creó el componente PHCalculator y se integró en el dashboard principal.

Changed
Frontend: Se refactorizó completamente el servicio api.ts para exportar un objeto api con métodos por cada verbo HTTP (get, post, etc.), mejorando la claridad y el tipado.

Frontend: Se actualizaron los componentes LoginForm, RegisterForm, AddMoleculeForm y MolarMassCalculator para que sean compatibles con el nuevo servicio de API refactorizado.

Fixed
Backend: Se corrigió un problema de desincronización con la base de datos generando y aplicando las migraciones necesarias para añadir las columnas faltantes (created_at, updated_at) a la tabla calculators_glossaryterm.

Frontend: Se solucionó un error en el componente PHCalculator que impedía mostrar los resultados al manejar incorrectamente el objeto de respuesta de la API.

[1.0.0-alpha] - 2025-07-19
Added
Backend: Se integró Redis al stack de docker-compose para ser utilizado como backend de caché.

Backend: Se creó la nueva app calculators en Django para alojar la lógica de las futuras herramientas de cálculo.

Frontend: Se desarrolló un conjunto inicial de componentes de UI base y reutilizables en src/components/common, incluyendo Button, Input, Card y Modal.

Frontend: Se añadió la dependencia @headlessui/react para la creación de componentes de UI accesibles como el Modal.

Changed
Infraestructura: Se actualizó docker-compose.yml para incluir el nuevo servicio de redis y se añadió como dependencia del servicio backend.

Backend: Se modificó chems_tools/settings.py para configurar django-redis como el sistema de caché por defecto.

Backend: Se actualizó requirements.txt para incluir la dependencia django-redis.

DevOps: Se revisó el pipeline de CI (.github/workflows/ci.yml) para asegurar que pytest ejecute las pruebas de todas las aplicaciones del backend, incluyendo la futura app calculators.

[0.3.1] - 2025-07-18
Added
Funcionalidad: Se completó el ciclo CRUD para las moléculas en el frontend, añadiendo la funcionalidad de eliminar y sentando las bases para la edición.

Seguridad: Se realizó una revisión integral de seguridad en el backend, añadiendo cabeceras de seguridad (XSS, nosniff) mediante django-secure.

Seguridad: Se implementó una política de rate limiting más estricta y específica para los endpoints de autenticación (5/min), protegiéndolos contra ataques de fuerza bruta.

Rendimiento: Se estableció un sistema para pruebas de carga y rendimiento básicas utilizando locust, incluyendo un locustfile.py para simular el comportamiento de usuarios reales.

Documentación: Se creó una guía de usuario inicial (USER_GUIDE.md) para facilitar la incorporación de nuevos usuarios y la preparación para demostraciones internas.

Changed
Frontend: El estado global de Redux (moleculesSlice) fue expandido para manejar las acciones de deleteMolecule y updateMolecule.

UI/UX: La interfaz de la lista de moléculas fue mejorada para incluir botones de "Editar" y "Eliminar", mejorando la interactividad.

Fixed
Rendimiento: Se corrigió un problema de configuración en locust que impedía el inicio de la interfaz web, asegurando que las pruebas de carga se puedan ejecutar correctamente.

[0.3.0] - 2025-07-12
Added
Funcionalidad: Se ha reintegrado la Calculadora de Masa Molar al dashboard principal, restaurando una de las herramientas clave del prototipo inicial.

Telemetría: Se implementó un sistema de telemetría básica con un endpoint y modelo en el backend para registrar eventos de usuario clave (ej. login_success, molecule_created), sentando las bases para la analítica de uso futuro.

Testing: Se amplió la cobertura de pruebas del frontend con una nueva suite de pruebas para el componente MolarMassCalculator.

Changed
UI/UX: Se realizó una mejora visual completa de la aplicación, ajustando los estilos de todos los componentes para mejorar drásticamente el contraste, la legibilidad y la estética general, resultando en una interfaz más moderna y profesional.

UI/UX: Se rediseñó el layout del dashboard principal para una mejor organización del contenido, utilizando un sistema de columnas para las diferentes herramientas.

Navegación: Se mejoró la navegación global al añadir un Header consistente en todas las páginas, permitiendo al usuario volver fácilmente al Dashboard desde la Tabla Periódica.

Componentes: El formulario de registro (RegisterForm) fue refactorizado para utilizar el sistema de notificaciones global, unificando la experiencia de feedback al usuario.

Fixed
UI/UX: Se corrigió un problema de layout en la Tabla Periódica donde la última fila de elementos se cortaba, ajustando la altura del contenedor SVG.

Frontend: Se solucionó un error crítico de renderizado del lado del servidor (Turbopack error) en el componente MoleculeList al hacerlo más robusto frente a estados iniciales no definidos.

[0.2.1] - 2025-07-11
Added
Frontend: Se implementó el componente PeriodicTable utilizando D3.js para renderizar una tabla periódica interactiva y estática.

Frontend: Se creó una nueva página (/periodic-table) para alojar la tabla periódica.

Backend: Se añadió una nueva app data y un endpoint (/api/data/periodic-table/) para servir los datos de los elementos químicos desde un archivo JSON.

Backend: Se implementó una validación de datos en el MoleculeSerializer para asegurar que las estructuras guardadas en formato SMILES sean químicamente válidas, utilizando RDKit.

Testing: Se expandió la cobertura de pruebas del backend con tests unitarios para la nueva lógica de validación del MoleculeSerializer.

Changed
Frontend: Se mejoró la interfaz de usuario del formulario AddMoleculeForm para incluir estados visuales de carga y error, proporcionando un feedback más claro al usuario durante el envío de datos.

Frontend: Se actualizó el componente Header para incluir un enlace de navegación a la nueva página de la Tabla Periódica.

[0.2.0] - 2025-07-11
Added
Backend: Se creó la app molecules para encapsular toda la lógica de negocio relacionada con la gestión de moléculas.

Backend: Se definió el modelo de datos Molecule en la base de datos, vinculado a un owner (usuario), y se generaron las migraciones correspondientes.

Backend: Se implementó un MoleculeViewSet que expone una API RESTful completa con operaciones CRUD (/api/molecules/) para las moléculas del usuario autenticado.

Frontend: Se añadió un moleculesSlice a Redux para gestionar el estado de la lista de moléculas, incluyendo acciones asíncronas (fetchMolecules) para obtener los datos del backend.

Frontend: Se desarrollaron los componentes de interfaz de usuario MoleculeList para mostrar las moléculas del usuario y AddMoleculeForm para permitir la creación de nuevas moléculas.

Changed
Frontend: La página principal (Home) ahora funciona como un "Dashboard" para usuarios autenticados, mostrando el formulario de creación y la lista de moléculas.

Frontend: El servicio apiService fue mejorado para manejar de forma más robusta los errores del servidor, clonando la respuesta para poder inspeccionarla como JSON y como texto, evitando así el error body stream already read.

Fixed
Backend: Se solucionó el error crítico relation "molecules_molecule" does not exist al asegurar que las migraciones de la app molecules se apliquen correctamente para crear la tabla en la base de datos.

Frontend: Se corrigió el error Unexpected token '<' que ocurría cuando el frontend intentaba interpretar una página de error HTML del backend como si fuera JSON.

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