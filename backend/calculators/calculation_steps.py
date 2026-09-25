"""
Módulo para generar pasos detallados de cálculos de pH con fórmulas.
"""
import math
from typing import List, Dict, Any, Optional


def generate_concentration_to_ph_steps(
    input_type: str,
    input_value: float,
    temperature: float = 25.0,
    include_activity: bool = False,
    ionic_strength: Optional[float] = None
) -> List[str]:
    """
    Genera pasos detallados para cálculo de concentración a pH.
    """
    steps = []
    
    # Paso 1: Identificar el tipo de entrada
    if input_type in ['h_concentration', 'H+']:
        steps.append(
            f"Paso 1: Identificación de datos\n"
            f"• Concentración de H⁺ = {input_value:.4e} M\n"
            f"• Temperatura = {temperature}°C"
        )
        
        # Paso 2: Aplicar fórmula de pH
        ph = -math.log10(input_value)
        steps.append(
            f"Paso 2: Cálculo del pH\n"
            f"• Fórmula: pH = -log₁₀[H⁺]\n"
            f"• pH = -log₁₀({input_value:.4e})\n"
            f"• pH = {ph:.2f}"
        )
        
        # Paso 3: Calcular pOH
        poh = 14.0 - ph
        steps.append(
            f"Paso 3: Cálculo del pOH\n"
            f"• Fórmula: pH + pOH = 14 (a 25°C)\n"
            f"• pOH = 14 - pH\n"
            f"• pOH = 14 - {ph:.2f}\n"
            f"• pOH = {poh:.2f}"
        )
        
        # Paso 4: Calcular [OH-]
        oh_concentration = 10**(-poh)
        steps.append(
            f"Paso 4: Cálculo de [OH⁻]\n"
            f"• Fórmula: [OH⁻] = 10^(-pOH)\n"
            f"• [OH⁻] = 10^(-{poh:.2f})\n"
            f"• [OH⁻] = {oh_concentration:.4e} M"
        )
        
    elif input_type in ['oh_concentration', 'OH-']:
        steps.append(
            f"Paso 1: Identificación de datos\n"
            f"• Concentración de OH⁻ = {input_value:.4e} M\n"
            f"• Temperatura = {temperature}°C"
        )
        
        # Paso 2: Calcular pOH
        poh = -math.log10(input_value)
        steps.append(
            f"Paso 2: Cálculo del pOH\n"
            f"• Fórmula: pOH = -log₁₀[OH⁻]\n"
            f"• pOH = -log₁₀({input_value:.4e})\n"
            f"• pOH = {poh:.2f}"
        )
        
        # Paso 3: Calcular pH
        ph = 14.0 - poh
        steps.append(
            f"Paso 3: Cálculo del pH\n"
            f"• Fórmula: pH + pOH = 14 (a 25°C)\n"
            f"• pH = 14 - pOH\n"
            f"• pH = 14 - {poh:.2f}\n"
            f"• pH = {ph:.2f}"
        )
        
        # Paso 4: Calcular [H+]
        h_concentration = 10**(-ph)
        steps.append(
            f"Paso 4: Cálculo de [H⁺]\n"
            f"• Fórmula: [H⁺] = 10^(-pH)\n"
            f"• [H⁺] = 10^(-{ph:.2f})\n"
            f"• [H⁺] = {h_concentration:.4e} M"
        )
    
    # Paso 5: Corrección por actividad si aplica
    if include_activity and ionic_strength is not None and ionic_strength > 0:
        steps.append(
            f"Paso 5: Corrección por actividad\n"
            f"• Fuerza iónica = {ionic_strength:.4f} M\n"
            f"• Se aplica la ecuación de Debye-Hückel para calcular coeficientes de actividad\n"
            f"• γ(H⁺) ≈ {math.exp(-0.51 * math.sqrt(ionic_strength)):.3f}\n"
            f"• pH corregido = -log₁₀(γ × [H⁺])"
        )
    
    # Paso 6: Clasificación
    if 'ph' in locals():
        if ph < 7:
            clasificacion = "ÁCIDA (pH < 7)"
        elif ph > 7:
            clasificacion = "BÁSICA (pH > 7)"
        else:
            clasificacion = "NEUTRA (pH = 7)"
        
        steps.append(
            f"Paso 6: Clasificación de la solución\n"
            f"• pH = {ph:.2f}\n"
            f"• La solución es {clasificacion}"
        )
    
    return steps


def generate_ph_to_all_steps(
    input_type: str,
    input_value: float,
    temperature: float = 25.0
) -> List[str]:
    """
    Genera pasos detallados para conversión de pH/pOH a todas las concentraciones.
    """
    steps = []
    
    if input_type == 'pH':
        ph = input_value
        steps.append(
            f"Paso 1: Dato inicial\n"
            f"• pH = {ph:.2f}\n"
            f"• Temperatura = {temperature}°C"
        )
        
        # Calcular [H+]
        h_concentration = 10**(-ph)
        steps.append(
            f"Paso 2: Cálculo de [H⁺]\n"
            f"• Fórmula: [H⁺] = 10^(-pH)\n"
            f"• [H⁺] = 10^(-{ph:.2f})\n"
            f"• [H⁺] = {h_concentration:.4e} M"
        )
        
        # Calcular pOH
        poh = 14.0 - ph
        steps.append(
            f"Paso 3: Cálculo del pOH\n"
            f"• Fórmula: pH + pOH = 14 (a 25°C)\n"
            f"• pOH = 14 - {ph:.2f}\n"
            f"• pOH = {poh:.2f}"
        )
        
        # Calcular [OH-]
        oh_concentration = 10**(-poh)
        steps.append(
            f"Paso 4: Cálculo de [OH⁻]\n"
            f"• Fórmula: [OH⁻] = 10^(-pOH)\n"
            f"• [OH⁻] = 10^(-{poh:.2f})\n"
            f"• [OH⁻] = {oh_concentration:.4e} M"
        )
        
    elif input_type == 'pOH':
        poh = input_value
        steps.append(
            f"Paso 1: Dato inicial\n"
            f"• pOH = {poh:.2f}\n"
            f"• Temperatura = {temperature}°C"
        )
        
        # Calcular [OH-]
        oh_concentration = 10**(-poh)
        steps.append(
            f"Paso 2: Cálculo de [OH⁻]\n"
            f"• Fórmula: [OH⁻] = 10^(-pOH)\n"
            f"• [OH⁻] = 10^(-{poh:.2f})\n"
            f"• [OH⁻] = {oh_concentration:.4e} M"
        )
        
        # Calcular pH
        ph = 14.0 - poh
        steps.append(
            f"Paso 3: Cálculo del pH\n"
            f"• Fórmula: pH + pOH = 14 (a 25°C)\n"
            f"• pH = 14 - {poh:.2f}\n"
            f"• pH = {ph:.2f}"
        )
        
        # Calcular [H+]
        h_concentration = 10**(-ph)
        steps.append(
            f"Paso 4: Cálculo de [H⁺]\n"
            f"• Fórmula: [H⁺] = 10^(-pH)\n"
            f"• [H⁺] = 10^(-{ph:.2f})\n"
            f"• [H⁺] = {h_concentration:.4e} M"
        )
    
    # Verificación con Kw
    if 'h_concentration' in locals() and 'oh_concentration' in locals():
        kw = h_concentration * oh_concentration
        steps.append(
            f"Paso 5: Verificación con Kw\n"
            f"• Fórmula: Kw = [H⁺] × [OH⁻]\n"
            f"• Kw = ({h_concentration:.4e}) × ({oh_concentration:.4e})\n"
            f"• Kw = {kw:.4e}\n"
            f"• Valor esperado a 25°C: 1.0 × 10⁻¹⁴"
        )
    
    return steps


def generate_buffer_steps(
    target_ph: float,
    buffer_components: List[Dict],
    temperature: float = 25.0
) -> List[str]:
    """
    Genera pasos detallados para cálculos de buffer.
    """
    steps = []
    
    if not buffer_components or len(buffer_components) < 2:
        return ["Error: Se requieren al menos dos componentes para un buffer"]
    
    # Obtener datos del buffer
    acid_component = buffer_components[0]
    base_component = buffer_components[1]
    
    acid_name = acid_component.get('compound', 'Ácido débil')
    acid_conc = acid_component.get('concentration', 0)
    pka = acid_component.get('pka', 0)
    
    base_name = base_component.get('compound', 'Base conjugada')
    base_conc = base_component.get('concentration', 0)
    
    steps.append(
        f"Paso 1: Identificación del sistema buffer\n"
        f"• Ácido débil: {acid_name} ({acid_conc:.3f} M)\n"
        f"• Base conjugada: {base_name} ({base_conc:.3f} M)\n"
        f"• pKa del sistema = {pka:.2f}\n"
        f"• pH objetivo = {target_ph:.2f}\n"
        f"• Temperatura = {temperature}°C"
    )
    
    # Aplicar ecuación de Henderson-Hasselbalch
    ratio = base_conc / acid_conc if acid_conc > 0 else 0
    ph_calculated = pka + math.log10(ratio) if ratio > 0 else pka
    
    steps.append(
        f"Paso 2: Aplicación de la ecuación de Henderson-Hasselbalch\n"
        f"• Fórmula: pH = pKa + log₁₀([A⁻]/[HA])\n"
        f"• pH = {pka:.2f} + log₁₀({base_conc:.3f}/{acid_conc:.3f})\n"
        f"• pH = {pka:.2f} + log₁₀({ratio:.3f})\n"
        f"• pH = {pka:.2f} + {math.log10(ratio) if ratio > 0 else 0:.3f}\n"
        f"• pH = {ph_calculated:.2f}"
    )
    
    # Calcular capacidad buffer
    h_concentration = 10**(-ph_calculated)
    ka = 10**(-pka)
    alpha = ka / (ka + h_concentration)
    
    total_concentration = acid_conc + base_conc
    buffer_capacity = 2.303 * alpha * (1 - alpha) * total_concentration
    
    steps.append(
        f"Paso 3: Cálculo de la capacidad buffer (β)\n"
        f"• Concentración total = {total_concentration:.3f} M\n"
        f"• Fracción disociada (α) = {alpha:.3f}\n"
        f"• Fórmula: β = 2.303 × α × (1-α) × C_total\n"
        f"• β = 2.303 × {alpha:.3f} × {1-alpha:.3f} × {total_concentration:.3f}\n"
        f"• β = {buffer_capacity:.4f} mol/L/pH"
    )
    
    # Evaluación de la eficacia del buffer
    distance_from_pka = abs(ph_calculated - pka)
    if distance_from_pka <= 1.0:
        eficacia = "EXCELENTE (pH dentro de ±1 unidad del pKa)"
    elif distance_from_pka <= 2.0:
        eficacia = "BUENA (pH dentro de ±2 unidades del pKa)"
    else:
        eficacia = "LIMITADA (pH fuera del rango óptimo)"
    
    steps.append(
        f"Paso 4: Evaluación de la eficacia del buffer\n"
        f"• Distancia del pKa: |{ph_calculated:.2f} - {pka:.2f}| = {distance_from_pka:.2f}\n"
        f"• Eficacia: {eficacia}\n"
        f"• Rango de trabajo óptimo: pH {pka-1:.2f} a {pka+1:.2f}"
    )
    
    # Concentraciones de especies en equilibrio
    fraction_acid = 1 / (1 + 10**(ph_calculated - pka))
    fraction_base = 1 - fraction_acid
    
    steps.append(
        f"Paso 5: Distribución de especies en equilibrio\n"
        f"• Fracción de {acid_name}: {fraction_acid:.1%}\n"
        f"• Fracción de {base_name}: {fraction_base:.1%}\n"
        f"• [H⁺] = {h_concentration:.4e} M\n"
        f"• [OH⁻] = {1e-14/h_concentration:.4e} M"
    )
    
    return steps


def generate_activity_correction_steps(
    ph_initial: float,
    ionic_strength: float,
    temperature: float = 25.0
) -> List[str]:
    """
    Genera pasos para corrección por actividad.
    """
    steps = []
    
    steps.append(
        f"Paso 1: Datos iniciales\n"
        f"• pH sin corregir = {ph_initial:.2f}\n"
        f"• Fuerza iónica (I) = {ionic_strength:.4f} M\n"
        f"• Temperatura = {temperature}°C"
    )
    
    # Calcular coeficiente de actividad usando Debye-Hückel
    A = 0.51  # Constante de Debye-Hückel a 25°C
    sqrt_I = math.sqrt(ionic_strength)
    
    # Para H+ (z = 1, a ≈ 9 Å)
    log_gamma = -A * sqrt_I / (1 + 1.5 * sqrt_I)
    gamma = 10**log_gamma
    
    steps.append(
        f"Paso 2: Cálculo del coeficiente de actividad (γ)\n"
        f"• Ecuación de Debye-Hückel extendida:\n"
        f"• log γ = -A × z² × √I / (1 + B × a × √I)\n"
        f"• Para H⁺: z = 1, a ≈ 9 Å\n"
        f"• log γ = -{A:.2f} × 1² × {sqrt_I:.3f} / (1 + 1.5 × {sqrt_I:.3f})\n"
        f"• log γ = {log_gamma:.4f}\n"
        f"• γ(H⁺) = {gamma:.4f}"
    )
    
    # Calcular pH corregido
    h_concentration = 10**(-ph_initial)
    activity_h = gamma * h_concentration
    ph_corrected = -math.log10(activity_h)
    
    steps.append(
        f"Paso 3: Corrección del pH\n"
        f"• [H⁺] = 10^(-{ph_initial:.2f}) = {h_concentration:.4e} M\n"
        f"• Actividad a(H⁺) = γ × [H⁺]\n"
        f"• a(H⁺) = {gamma:.4f} × {h_concentration:.4e}\n"
        f"• a(H⁺) = {activity_h:.4e}\n"
        f"• pH corregido = -log₁₀(a(H⁺))\n"
        f"• pH corregido = {ph_corrected:.2f}"
    )
    
    # Diferencia y análisis
    difference = ph_corrected - ph_initial
    steps.append(
        f"Paso 4: Análisis de la corrección\n"
        f"• Diferencia: ΔpH = {difference:+.3f}\n"
        f"• El pH {'disminuye' if difference < 0 else 'aumenta'} debido a la actividad iónica\n"
        f"• Efecto más significativo a mayor fuerza iónica"
    )
    
    return steps
