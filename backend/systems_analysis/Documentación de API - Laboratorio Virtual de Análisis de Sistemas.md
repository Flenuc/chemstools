# Documentación de API - Laboratorio Virtual de Análisis de Sistemas

Información General
Base URL: https://api.chemstools.com/api/systems/
Versión: 1.0.
Autenticación: Bearer Token (JWT)
Rate Limiting: Variable por endpoint (especificado en cada sección)
Formato: JSON
Autenticación
Todos los endpoints requieren autenticación mediante token JWT en el header:
Endpoints

1. Análisis de Sistema Químico
Analiza una mezcla química y sugiere métodos de separación óptimos.
Endpoint: POST /analyze/
Rate Limit: 20 solicitudes/minuto
Request
Body Parameters:
    Campo Tipo Requerido Descripción
    name string Sí Nombre descriptivo del sistema
    components array Sí Lista de componentes de la mezcla
    components[].substance_id string Sí ID o nombre de la sustancia
    components[].mass_fraction float Sí Fracción másica (0-1)
    components[].particle_size float NO Tamaño de partícula en μm
    components[].phase string NO Fase: solid/liquid/gas
    total_mass float Sí Masa total en gramos
    analysis_conditions object NO Condiciones del análisis
    analysis_conditions.temperature float NO Temperatura en °C (default: 25)
    analysis_conditions.pressure float NO Presión en atm (default: 1)
    
http
Authorization: Bearer {token}
http
POST /api/systems/analyze/
Content-Type: application/json
Authorization: Bearer {token}


Response
Status Code: 201 Created
Errores Comunes
Código Descripción Ejemplo
400 Datos inválidos Fracciones no suman 1.
401 No autorizado Token inválido o expirado
429 Rate limit excedido Demasiadas solicitudes
500 Error interno Error en el motor de análisis
json
{
"success": true,
"analysis_id": "550e8400-e29b-41d4-a716-446655440000",
"results": {
"system_type": "heterogeneous",
"phases_detected": [
{
"phase": "solid",
"components": ["arena", "hierro"],
"total_fraction": 0.
},
{
"phase": "liquid",
"components": ["agua"],
"total_fraction": 0.
}
],
"recommended_methods": [
{
"method": "magnetic_separation",
"target": ["hierro"],
"efficiency": 0.98,
"difficulty": "basic"
}
],
"overall_separability": 0.95,
"estimated_time": 1.5,
"complexity_level": "basic"
}
}


2. Métodos de Separación Disponibles
Obtiene la lista de métodos de separación disponibles.
Endpoint: GET /separation-methods/
Rate Limit: 100 solicitudes/minuto
Query Parameters
    Parámetro Tipo Descripción
    type string Filtrar por tipo: mechanical/physical/chemical/magnetic/thermal
    complexity string Filtrar por complejidad: basic/intermediate/advanced
Response
    json
       {
       "success": true,
       "methods": [
       {
       "id": 1 ,
       "name": "Tamización",
       "method_type": "mechanical",
       "description": "Separación por tamaño de partícula usando tamices",
       "principle": "Diferencia en el tamaño de partícula",
       "equipment_required": ["Tamices", "Agitador"],
       "efficiency_range": {"min": 90 , "max": 99 },
       "cost_factor": 1 ,
       "complexity_level": "basic",
       "applicable_phases": ["solid"],
       "property_criteria": {"particle_size_ratio": 10 }
       }
       ]
       }


3. Generar Diagrama de Separación
Genera un diagrama de flujo optimizado para el proceso de separación.
Endpoint: POST /generate-separation-flow/
Rate Limit: 10 solicitudes/minuto
Request
Response
    json
       {
       "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
       "selected_methods": ["magnetic_separation", "filtration"],
       "optimization_criteria": {
       "priority": "efficiency",
       "max_time": 4.0,
       "max_complexity": "intermediate"
       }
       }
    json
       {
       "success": true,
       "process_id": "660e8400-e29b-41d4-a716-446655440001",
       "separation_flow": {
       "steps": [
       {
       "step": 1 ,
       "method": "magnetic_separation",
       "description": "Separar limaduras de hierro",
       "input": ["all_components"],
       "output": {
       "magnetic": ["hierro"],
       "non_magnetic": ["arena", "agua"]
       },
       "efficiency": 0.98,
       "time": 0.3,
       "equipment": ["Imán permanente"]
       }
       ],
       "final_products": [
       {
       "name": "Hierro puro",
       "purity": 0.98,
       "recovery": 0.98,
       "separated_in_step": 1
       }
       ],
       "overall_efficiency": 0.97,
       "total_time": 1.0,
       "total_cost": 15.5,
       "diagram_data": {
       "nodes": [...],
       "edges": [...],
       "layout": "hierarchical"
       }
       }
       }


4. Propiedades de Sustancia
Obtiene las propiedades detalladas de una sustancia específica.
Endpoint: GET /substance-properties/{id}/
Rate Limit: 200 solicitudes/minuto
Response
5. Búsqueda de Sustancias
Busca sustancias por múltiples criterios.
Endpoint: GET /substances/search/
Rate Limit: 100 solicitudes/minuto
Query Parameters
    Parámetro Tipo Descripción
    query String Búsqueda por nombre, fórmula o CAS
    phase String Filtrar por fase: solid/liquid/gas
    category String Categoría: organic/inorganic/metal/salt/oxide/acid/base/mineral
    min_density Float Densidad mínima en g/cm³
    max_density Float Densidad máxima en g/cm³
    magnetic Boolean Solo sustancias magnéticas
    soluble Boolean Solo sustancias solubles en agua
       json
          {
          "success": true,
          "substance": {
          "id": 1 ,
          "name": "Hierro",
          "formula": "Fe",
          "cas_number": "7439- 89 - 6",
          "molecular_weight": 55.845,
          "density": 7.874,
          "melting_point": 1538 ,
          "boiling_point": 2862 ,
          "solubility_water": null,
          "magnetic_susceptibility": 0.22,
          "particle_size_range": {"min": 50 , "max": 500 },
          "phase_at_stp": "solid",
          "chemical_category": "metal",
          "color": "Gris metálico",
          "separation_properties": {
          "density": 7.874,
          "magnetic": 0.22,
          "phase": "solid"
          }
          }
          }


Response

6. Historial de Análisis
Obtiene el historial de análisis del usuario autenticado.
Endpoint: GET /analysis-history/
Rate Limit: 100 solicitudes/minuto
Query Parameters
    Parámetro Tipo Descripción
    page integer Número de página (default: 1)
    page_size integer Elementos por página (default: 10, max: 100)
    ordering string Ordenamiento: created_at/-created_at
Response
    json
       {
       "success": true,
       "count": 3 ,
       "substances": [
       {
       "id": 1 ,
       "name": "Hierro",
       "formula": "Fe",
       "density": 7.874,
       "phase_at_stp": "solid",
       "chemical_category": "metal"
       }
       ]
       }
    json
       {
       "count": 25 ,
       "next": "http://api.chemstools.com/api/systems/analysis-history/?page=2",
       "previous": null,
       "results": [
       {
       "id": "550e8400-e29b-41d4-a716-446655440000",
       "name": "Separación de arena de playa",
       "system_type": "heterogeneous",
       "total_mass": 1000 ,
       "created_at": "2025- 08 - 31T10:30:00Z",
       "phases_detected": [...],
       "analysis_data": {...}
       }
       ]
       }


7. Estadísticas de Usuario
Obtiene estadísticas agregadas de los análisis del usuario.
Endpoint: GET /analysis-history/stats/
Rate Limit: 100 solicitudes/minuto
Response
Códigos de Estado HTTP
    Código Descripción
    200 Solicitud exitosa
    201 Recurso creado exitosamente
    400 Solicitud inválida
    401 No autorizado
    403 Prohibido
    404 Recurso no encontrado
    429 Rate limit excedido
    500 Error interno del servidor
Manejo de Errores
Todas las respuestas de error siguen el formato:
    json
       {
       "total_analyses": 42 ,
       "system_types": {
       "heterogeneous": 30 ,
       "homogeneous": 10 ,
       "colloidal": 2
       },
       "complexity_levels": {
       "basic": 25 ,
       "intermediate": 15 ,
       "advanced": 2
       },
       "average_separability": 0.
       }
json
{
"success": false,
"error": "Descripción del error",
"errors": {
"campo": ["Lista de errores de validación"]
}
}


Límites y Restricciones

- Máximo 100 componentes por análisis
- Masa total máxima: 1,000,000 gramos
- Tamaño de partícula: 0.001 - 10,000 μm
- Temperatura: -273 a 5000 °C
- Presión: 0.001 a 1000 atm
Webhooks (Próximamente)
Se planea implementar webhooks para notificar cuando:
- Un análisis largo termine
- Se genere un diagrama complejo
- Se actualice la base de datos de sustancias
SDKs y Librerías
- Python: pip install chemstools-sdk
- JavaScript: npm install @chemstools/api-client
- Postman Collection: Descargar
Versionado
La API usa versionado semántico. Los cambios breaking se anunciarán con 6 meses de anticipación.
