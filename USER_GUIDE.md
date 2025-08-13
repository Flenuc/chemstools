# Guía de Usuario de ChemsTools (Alphas 1 y 2)

Bienvenido a ChemsTools. Esta guía cubre todas las funcionalidades disponibles desde Alpha 1 hasta Alpha 2, incluyendo herramientas de cálculo, simuladores, generador de estructuras, búsqueda avanzada y juegos de química.

Sugerencia: La aplicación utiliza un sistema global de notificaciones. Presta atención a los avisos de éxito, error e información que aparecen al realizar acciones.

## 1. Autenticación
- Registro: Completa usuario, email y contraseña en la pantalla principal.
- Inicio de sesión: Accede con tus credenciales. El encabezado mostrará tu estado y opción para cerrar sesión.

## 2. Navegación general
- Menú principal: Acceso a Dashboard, Tabla Periódica, Calculadoras, Estructuras de Lewis, Reacciones y Juegos (Quiz, ChemWordle, Memory, Balance Challenge, Periodic Speed).
- Protección de rutas: Algunas secciones requieren sesión iniciada.

## 3. Dashboard y gestión de moléculas
- Añadir moléculas: Usa “Añadir Nueva Molécula” (formato SMILES válido).
- Lista “Mis Moléculas”: Visualiza y gestiona tus moléculas guardadas.
- Borrado: Puedes eliminar moléculas desde la lista.

## 4. Tabla Periódica interactiva
- Acceso: Enlace “Tabla Periódica”.
- Interacciones:
  - Ver detalles: Clic en un elemento para ver su ficha.
  - Filtro cruzado: Al volver al Dashboard, la lista de moléculas se puede filtrar por el elemento seleccionado.

## 5. Calculadora de Masa Molar
- Introduce una fórmula química y pulsa “Calcular” para obtener la masa molar.

## 6. Calculadoras químicas
### 6.1 Glosario de Términos Químicos
- Busca definiciones por nombre mediante la barra de búsqueda.

### 6.2 Calculadora de pH/pOH
- Convierte entre pH, pOH, [H+] y [OH−].
- Selecciona el tipo de entrada (por ejemplo pH), ingresa el valor y pulsa “Calcular”.

### 6.3 Calculadora de Disoluciones
- Calcula % m/m y % m/v.
- Rellena al menos dos campos entre: masa de soluto (g), masa de disolvente (g), volumen de disolución (mL).
- Opcional: Densidad (g/mL) para derivar un porcentaje a partir del otro.

## 7. Generador de Estructuras de Lewis
El generador usa RDKit en el backend y representa la estructura en el frontend. Está optimizado con caché y admite entrada por fórmula y SMILES.

- Acceso: Desde el menú “Estructuras de Lewis”.
- Entrada:
  - Fórmula química (por ejemplo H2O, CO2, NH3, BF3, SF6, XeF4, etc.).
  - SMILES: pega una cadena SMILES válida para moléculas compatibles.
- Categorías de selección rápida: Elige entre grupos como Moléculas Simples, Hidrocarburos, Alcoholes/Éteres, P/S, Halógenos y Otros.
- Compuestos iónicos: Detección y tratamiento especializado de sales y óxidos (p.ej., NaCl, CaCO3, Fe2O3, CuSO4). La visualización refleja la ausencia de enlaces covalentes donde corresponda.
- Visualización:
  - Átomos, enlaces simples/dobles/triples y pares libres.
  - Cargas formales cuando aplica.
  - Posicionamiento mejorado de pares solitarios para evitar solapamientos.
  - Opcional: Render con Kekule.js.
- Estructuras recientes: Acceso rápido a las últimas generadas; se actualiza automáticamente al crear nuevas.
- Rendimiento: Caché en base de datos; respuestas instantáneas si la estructura ya existe.
- Errores comunes: Si la molécula no está soportada, se mostrará un mensaje con sugerencias o una lista de ejemplos válidos.

## 8. Simulador de Reacciones Químicas (Balanceo)
Balancea ecuaciones químicas automáticamente usando SymPy y muestra resultados detallados.

- Acceso: “Reacciones” o “Simulador de Reacciones”.
- Uso:
  - Introduce una ecuación sin balancear (p.ej., Fe + O2 -> Fe2O3, C3H8 + O2 -> CO2 + H2O).
  - Pulsa “Balancear”.
- Resultados:
  - Ecuación balanceada y coeficientes por compuesto (reactivos y productos).
  - Tipo de reacción detectado (síntesis, descomposición, combustión, sustitución).
  - Historial: Consulta reacciones balanceadas recientemente.
- Validación y errores: Mensajes claros ante entradas inválidas o mal formateadas.

## 9. Búsqueda avanzada de compuestos (PubChem)
- Busca por nombre (es/en), fórmula, SMILES o InChI.
- La aplicación detecta el tipo de consulta, traduce nombres cuando es necesario y cachea resultados frecuentes.
- Muestra nombres comunes y propiedades básicas del compuesto.

## 10. Juegos de Química
Todos los juegos guardan progreso, estadísticas y cuentan con clasificaciones globales cuando aplica. Algunos requieren autenticación.

### 10.1 Quiz Rápido de Química (/quiz)
- Inicia una sesión seleccionando aleatorio o dificultad (fácil/medio/difícil).
- Responde preguntas de opción múltiple con temporizador y feedback educativo tras cada respuesta.
- Consulta tu panel de estadísticas y la clasificación global.

### 10.2 ChemWordle (/chemwordle)
- Adivina la palabra química en hasta 6 intentos.
- El teclado virtual y el grid muestran feedback tipo Wordle (correcto/presente/ausente).
- Pistas progresivas basadas en metadatos químicos. Consulta estadísticas y leaderboard.

### 10.3 Memory Molecular (/memory)
- Empareja cartas de nombre y fórmula.
- Elige dificultad y número de pares. Seguimiento de tiempo, progreso y puntuación.
- Revisa estadísticas personales y clasificación global.

### 10.4 Balance Challenge (/balance-challenge)
- Balancea ecuaciones arrastrando y soltando coeficientes.
- Dificultades: fácil/medio/difícil con sistema de pistas progresivas.
- Panel de estadísticas por dificultad y clasificación global.

### 10.5 Periodic Speed (/periodic-speed)
- Identifica rápidamente el elemento objetivo haciendo clic en la tabla periódica.
- Dificultades: aleatorio, común, raro. Temporizador y pistas contextuales.
- Estadísticas detalladas (precisión, rachas, mejores tiempos) y leaderboard.

## 11. Notificaciones y estados
- La app muestra notificaciones de validación, éxito, error e información en estructuras, reacciones y todos los juegos.
- Tipos: success, error, info; se integran con el estado global para un feedback consistente.

## 12. Consejos y resolución de problemas
- Verifica formato: Fórmulas químicas válidas (mayúsculas/minúsculas, subíndices como números), SMILES correctos.
- Tiempo de espera: Las operaciones de red usan timeouts; reintenta si tu conexión es inestable.
- Autenticación: Si una página indica que requiere sesión, inicia sesión e inténtalo de nuevo.
- Soporte de compuestos: Si un compuesto no está soportado por el generador de Lewis, prueba con SMILES o verifica si es iónico.

## 13. Preguntas frecuentes (FAQ) rápidas
- ¿Puedo pegar SMILES? Sí, en el Generador de Lewis.
- ¿Hay historial de reacciones? Sí, en la sección de reacciones balanceadas.
- ¿Dónde veo mis estadísticas de juego? En cada juego, en la pestaña de estadísticas o la pantalla de resultados.
- ¿Qué pasa si cierro un juego a medias? Puedes abandonar desde la opción correspondiente y luego iniciar un nuevo desafío.
