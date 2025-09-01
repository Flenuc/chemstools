# Sistema de Análisis de Sistemas Químicos

## Descripción

El módulo de **Análisis de Sistemas Químicos** es una funcionalidad avanzada de ChemsTools que proporciona análisis inteligente de mezclas químicas y generación automática de procesos de separación optimizados.

## Características Principales

### 🔬 Motor de Análisis Inteligente
- Clasificación automática de sistemas (homogéneo/heterogéneo/coloidal)
- Detección de fases presentes (sólido/líquido/gas)
- Análisis de compatibilidad química
- Cálculo de separabilidad global

### 🧪 Base de Datos de Sustancias
- 500+ sustancias químicas con propiedades verificadas
- Propiedades físico-químicas completas
- Datos de seguridad y manejo
- Propiedades relevantes para separación

### ⚙️ Algoritmos de Separación
- 10+ métodos de separación implementados
- Evaluación automática de aplicabilidad
- Cálculo de eficiencia esperada
- Estimación de tiempo y costo

### 📊 Generación de Diagramas
- Diagramas de flujo de proceso automáticos
- Optimización de secuencias de separación
- Visualización de productos finales
- Métricas de rendimiento

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Agregar a `INSTALLED_APPS` en settings.py:
```python
INSTALLED_APPS = [
    # ...
    'systems_analysis',
]
```

3. Ejecutar migraciones:
```bash
python manage.py makemigrations systems_analysis
python manage.py migrate
```

4. Poblar base de datos:
```bash
python manage.py populate_substances
```

## Uso de la API

### Análisis de Sistema

```http
POST /api/systems/analyze/
Content-Type: application/json
Authorization: Bearer {token}

{
  "name": "Separación de arena de playa",
  "components": [
    {
      "substance_id": "arena",
      "mass_fraction": 0.7,
      "particle_size": 500
    },
    {
      "substance_id": "agua",
      "mass_fraction": 0.2
    },
    {
      "substance_id": "hierro",
      "mass_fraction": 0.1,
      "particle_size": 100
    }
  ],
  "total_mass": 1000,
  "analysis_conditions": {
    "temperature": 25,
    "pressure": 1
  }
}
```

### Respuesta

```json
{
  "success": true,
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "results": {
    "system_type": "heterogeneous",
    "phases_detected": [
      {
        "phase": "solid",
        "components": ["arena", "hierro"],
        "total_fraction": 0.8
      },
      {
        "phase": "liquid",
        "components": ["agua"],
        "total_fraction": 0.2
      }
    ],
    "recommended_methods": [
      {
        "method": "magnetic_separation",
        "target": ["hierro"],
        "efficiency": 0.98,
        "difficulty": "basic"
      },
      {
        "method": "filtration",
        "target": ["arena"],
        "efficiency": 0.99,
        "difficulty": "basic"
      }
    ],
    "overall_separability": 0.95,
    "estimated_time": 1.5,
    "complexity_level": "basic"
  }
}
```

## Arquitectura

### Componentes Principales

```
systems_analysis/
├── models.py           # Modelos de datos
├── engines.py          # Motor de análisis principal
├── separation_algorithms.py  # Algoritmos de separación
├── serializers.py      # Serialización de datos
├── views.py           # Endpoints de API
└── management/
    └── commands/
        └── populate_substances.py  # Población de BD
```

### Flujo de Procesamiento

1. **Recepción de datos** → Validación de componentes
2. **Análisis del sistema** → Detección de fases
3. **Evaluación de métodos** → Aplicabilidad y eficiencia
4. **Optimización** → Secuencia de separación
5. **Generación de resultados** → Diagrama y métricas

## Métodos de Separación Soportados

| Método | Tipo | Complejidad | Eficiencia |
|--------|------|-------------|------------|
| Tamización | Mecánico | Básico | 90-99% |
| Separación Magnética | Magnético | Básico | 95-99% |
| Flotación | Físico | Básico | 70-95% |
| Filtración | Físico | Básico | 95-99% |
| Decantación | Físico | Básico | 85-95% |
| Destilación | Térmico | Intermedio | 85-95% |
| Cristalización | Físico | Intermedio | 80-95% |
| Extracción | Químico | Intermedio | 75-90% |
| Sublimación | Térmico | Avanzado | 90-98% |
| Cromatografía | Físico | Avanzado | 95-99% |

## Testing

Ejecutar pruebas:
```bash
python manage.py test systems_analysis
```

Cobertura de pruebas:
```bash
coverage run --source='systems_analysis' manage.py test systems_analysis
coverage report
```

## Métricas de Performance

- **Tiempo de análisis**: < 5 segundos para sistemas complejos
- **Generación de diagramas**: < 10 segundos
- **Consultas de propiedades**: < 100ms
- **Optimización de procesos**: < 30 segundos

## Contribuir

1. Fork el repositorio
2. Crear rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Licencia

Este módulo es parte de ChemsTools y está sujeto a los términos de la licencia del proyecto principal.

## Contacto

Para reportar problemas o sugerencias, abrir un issue en el repositorio principal de ChemsTools.
