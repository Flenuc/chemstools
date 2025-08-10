Changelog
Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en Keep a Changelog (https://keepachangelog.com/en/1.0.0/), 
y este proyecto se adhiere al Versionamiento Semántico (https://semver.org/spec/v2.0.0.html).

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