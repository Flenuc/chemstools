"""
Utilidades para exportación de cálculos de pH.
"""

import os
import csv
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Tuple
from io import StringIO, BytesIO

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.legends import Legend

from django.conf import settings
from django.utils import timezone


def export_to_csv(calculations, include_steps=False, include_warnings=True) -> Tuple[str, int]:
    """
    Exporta cálculos a formato CSV usando pandas.
    
    Args:
        calculations: QuerySet de PHCalculationHistory
        include_steps: Incluir pasos detallados
        include_warnings: Incluir warnings
        
    Returns:
        Tuple[str, int]: (ruta_archivo, tamaño_bytes)
    """
    # Preparar datos
    data = []
    for calc in calculations:
        row = {
            'ID': str(calc.id),
            'Tipo_Calculo': calc.get_calculation_type_display(),
            'Fecha': calc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Usuario': calc.user.username if calc.user else 'Anónimo',
            'Temperatura_C': calc.temperature,
            'Fuerza_Ionica': calc.ionic_strength or 'N/A',
            'Tiempo_Calculo_ms': calc.calculation_time_ms,
        }
        
        # Agregar resultados principales
        if calc.results:
            row.update({
                'pH': calc.results.get('ph', 'N/A'),
                'pOH': calc.results.get('poh', 'N/A'),
                'Concentracion_H': calc.results.get('h_concentration', 'N/A'),
                'Concentracion_OH': calc.results.get('oh_concentration', 'N/A'),
                'Coef_Actividad_H': calc.results.get('activity_coefficient_h', 'N/A'),
                'Coef_Actividad_OH': calc.results.get('activity_coefficient_oh', 'N/A'),
                'Kw_Corregido': calc.results.get('corrected_kw', 'N/A'),
                'Capacidad_Buffer': calc.results.get('buffer_capacity', 'N/A'),
            })
        
        # Agregar datos de entrada
        if calc.input_data:
            row.update({
                'Valor_Entrada': calc.input_data.get('input_value', 'N/A'),
                'Tipo_Entrada': calc.input_data.get('input_type', 'N/A'),
                'Incluye_Actividad': calc.input_data.get('include_activity', False),
            })
        
        # Agregar warnings si se solicita
        if include_warnings and calc.warnings:
            row['Warnings'] = '; '.join(calc.warnings)
        
        # Agregar pasos si se solicita
        if include_steps and calc.calculation_steps:
            row['Pasos_Calculo'] = '; '.join(calc.calculation_steps)
        
        data.append(row)
    
    # Crear DataFrame
    df = pd.DataFrame(data)
    
    # Generar archivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'ph_calculations_{timestamp}.csv'
    file_path = os.path.join(settings.MEDIA_ROOT, 'exports', filename)
    
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Guardar con encoding UTF-8 con BOM para Excel
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    
    # Obtener tamaño del archivo
    file_size = os.path.getsize(file_path)
    
    return file_path, file_size


def export_to_pdf(calculations, include_steps=False, include_warnings=True) -> Tuple[str, int]:
    """
    Exporta cálculos a formato PDF usando reportlab.
    
    Args:
        calculations: QuerySet de PHCalculationHistory
        include_steps: Incluir pasos detallados
        include_warnings: Incluir warnings
        
    Returns:
        Tuple[str, int]: (ruta_archivo, tamaño_bytes)
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'ph_calculations_report_{timestamp}.pdf'
    file_path = os.path.join(settings.MEDIA_ROOT, 'exports', filename)
    
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Crear PDF
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=20,
        spaceAfter=30,
        textColor=colors.darkblue
    )
    story.append(Paragraph("Reporte de Cálculos de pH/pOH", title_style))
    story.append(Spacer(1, 20))
    
    # Información del reporte
    info_style = styles['Normal']
    story.append(Paragraph(f"<b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", info_style))
    story.append(Paragraph(f"<b>Total de cálculos:</b> {calculations.count()}", info_style))
    story.append(Spacer(1, 20))
    
    # Estadísticas generales
    story.append(Paragraph("Estadísticas Generales", styles['Heading2']))
    stats = _generate_pdf_statistics(calculations)
    for stat in stats:
        story.append(Paragraph(f"• {stat}", info_style))
    story.append(Spacer(1, 20))
    
    # Tabla de cálculos
    story.append(Paragraph("Detalle de Cálculos", styles['Heading2']))
    table_data = _generate_pdf_table_data(calculations, include_steps, include_warnings)
    
    if table_data:
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
    
    # Generar PDF
    doc.build(story)
    
    # Obtener tamaño del archivo
    file_size = os.path.getsize(file_path)
    
    return file_path, file_size


def export_to_json(calculations, include_steps=True, include_warnings=True) -> Tuple[str, int]:
    """
    Exporta cálculos a formato JSON estructurado.
    
    Args:
        calculations: QuerySet de PHCalculationHistory
        include_steps: Incluir pasos detallados
        include_warnings: Incluir warnings
        
    Returns:
        Tuple[str, int]: (ruta_archivo, tamaño_bytes)
    """
    # Preparar datos
    export_data = {
        'export_info': {
            'generated_at': timezone.now().isoformat(),
            'total_calculations': calculations.count(),
            'includes_steps': include_steps,
            'includes_warnings': include_warnings,
            'format_version': '1.0'
        },
        'calculations': []
    }
    
    for calc in calculations:
        calc_data = {
            'id': str(calc.id),
            'calculation_type': calc.calculation_type,
            'calculation_type_display': calc.get_calculation_type_display(),
            'created_at': calc.created_at.isoformat(),
            'user': calc.user.username if calc.user else None,
            'input_data': calc.input_data,
            'results': calc.results,
            'temperature': calc.temperature,
            'ionic_strength': calc.ionic_strength,
            'calculation_time_ms': calc.calculation_time_ms,
        }
        
        if include_steps and calc.calculation_steps:
            calc_data['calculation_steps'] = calc.calculation_steps
        
        if include_warnings and calc.warnings:
            calc_data['warnings'] = calc.warnings
        
        export_data['calculations'].append(calc_data)
    
    # Generar archivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'ph_calculations_{timestamp}.json'
    file_path = os.path.join(settings.MEDIA_ROOT, 'exports', filename)
    
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Guardar JSON con formato legible
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    # Obtener tamaño del archivo
    file_size = os.path.getsize(file_path)
    
    return file_path, file_size


def create_download_url(file_path: str, expires_in_hours: int = 24) -> Tuple[str, datetime]:
    """
    Crea una URL temporal de descarga con expiración automática.
    
    Args:
        file_path: Ruta del archivo
        expires_in_hours: Horas hasta expiración
        
    Returns:
        Tuple[str, datetime]: (url_descarga, fecha_expiracion)
    """
    # Obtener nombre del archivo
    filename = os.path.basename(file_path)
    
    # Crear URL relativa al MEDIA_URL
    relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
    download_url = f"/media/exports/{filename}"
    
    # Calcular fecha de expiración
    expires_at = timezone.now() + timedelta(hours=expires_in_hours)
    
    return download_url, expires_at


class PHCalculationPDFGenerator:
    """
    Generador de PDFs profesionales para cálculos de pH.
    """
    
    def __init__(self, calculations):
        self.calculations = calculations
        self.styles = getSampleStyleSheet()
        
    def generate_detailed_report(self, file_path: str):
        """Genera un reporte PDF detallado."""
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        story = []
        
        # Header con logo
        story.extend(self._create_header())
        
        # Resumen ejecutivo
        story.extend(self._create_executive_summary())
        
        # Análisis detallado
        story.extend(self._create_detailed_analysis())
        
        # Gráficos y visualizaciones
        story.extend(self._create_visualizations())
        
        # Anexos con datos completos
        story.extend(self._create_appendix())
        
        # Footer
        story.extend(self._create_footer())
        
        doc.build(story)
    
    def _create_header(self):
        """Crea el header del PDF."""
        elements = []
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.darkblue,
            spaceAfter=30
        )
        
        elements.append(Paragraph("ChemsTools - Reporte de Análisis de pH", title_style))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_executive_summary(self):
        """Crea resumen ejecutivo."""
        elements = []
        elements.append(Paragraph("Resumen Ejecutivo", self.styles['Heading1']))
        
        summary_stats = self._calculate_summary_stats()
        for stat in summary_stats:
            elements.append(Paragraph(f"• {stat}", self.styles['Normal']))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _calculate_summary_stats(self):
        """Calcula estadísticas para el resumen."""
        stats = []
        count = self.calculations.count()
        
        if count > 0:
            # Estadísticas básicas
            stats.append(f"Total de cálculos analizados: {count}")
            
            # Rango de pH
            ph_values = [calc.results.get('ph') for calc in self.calculations 
                        if calc.results and calc.results.get('ph')]
            if ph_values:
                ph_values = [ph for ph in ph_values if ph is not None]
                if ph_values:
                    min_ph = min(ph_values)
                    max_ph = max(ph_values)
                    avg_ph = sum(ph_values) / len(ph_values)
                    stats.append(f"Rango de pH: {min_ph:.1f} - {max_ph:.1f} (promedio: {avg_ph:.1f})")
            
            # Tipos de cálculo más frecuentes
            from collections import Counter
            calc_types = [calc.calculation_type for calc in self.calculations]
            most_common = Counter(calc_types).most_common(3)
            if most_common:
                types_str = ", ".join([f"{t[0]} ({t[1]})" for t in most_common])
                stats.append(f"Tipos de cálculo más frecuentes: {types_str}")
        
        return stats
    
    def _create_detailed_analysis(self):
        """Crea análisis detallado."""
        elements = []
        elements.append(Paragraph("Análisis Detallado", self.styles['Heading1']))
        
        # Tabla con datos principales
        table_data = [['Fecha', 'Tipo', 'pH', 'Temperatura', 'Tiempo (ms)']]
        
        for calc in self.calculations[:20]:  # Limitar a 20 para el PDF
            row = [
                calc.created_at.strftime('%d/%m/%Y'),
                calc.get_calculation_type_display()[:20],
                f"{calc.results.get('ph', 'N/A'):.2f}" if calc.results and calc.results.get('ph') else 'N/A',
                f"{calc.temperature}°C",
                str(calc.calculation_time_ms)
            ]
            table_data.append(row)
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_visualizations(self):
        """Crea gráficos y visualizaciones."""
        elements = []
        elements.append(Paragraph("Visualizaciones", self.styles['Heading1']))
        
        # Placeholder para gráficos futuros
        elements.append(Paragraph("Gráficos de tendencias y distribuciones serán incluidos en futuras versiones.", self.styles['Normal']))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_appendix(self):
        """Crea anexos con datos completos."""
        elements = []
        elements.append(Paragraph("Anexos - Datos Completos", self.styles['Heading1']))
        
        for i, calc in enumerate(self.calculations, 1):
            elements.append(Paragraph(f"Cálculo #{i}", self.styles['Heading2']))
            
            # Información básica
            info = [
                f"ID: {calc.id}",
                f"Fecha: {calc.created_at.strftime('%d/%m/%Y %H:%M')}",
                f"Tipo: {calc.get_calculation_type_display()}",
                f"Temperatura: {calc.temperature}°C",
                f"Tiempo de cálculo: {calc.calculation_time_ms}ms"
            ]
            
            for line in info:
                elements.append(Paragraph(line, self.styles['Normal']))
            
            # Resultados
            if calc.results:
                elements.append(Paragraph("Resultados:", self.styles['Heading3']))
                for key, value in calc.results.items():
                    if isinstance(value, (int, float)):
                        elements.append(Paragraph(f"• {key}: {value:.4f}", self.styles['Normal']))
                    else:
                        elements.append(Paragraph(f"• {key}: {value}", self.styles['Normal']))
            
            # Warnings
            if calc.warnings:
                elements.append(Paragraph("Advertencias:", self.styles['Heading3']))
                for warning in calc.warnings:
                    elements.append(Paragraph(f"⚠ {warning}", self.styles['Normal']))
            
            elements.append(Spacer(1, 15))
            
            # Limitar a 10 cálculos detallados para evitar PDFs muy largos
            if i >= 10:
                remaining = self.calculations.count() - 10
                if remaining > 0:
                    elements.append(Paragraph(f"... y {remaining} cálculos adicionales", self.styles['Normal']))
                break
        
        return elements
    
    def _create_footer(self):
        """Crea footer del PDF."""
        elements = []
        elements.append(Spacer(1, 30))
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1  # Center
        )
        
        elements.append(Paragraph(
            f"Generado por ChemsTools el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            footer_style
        ))
        
        return elements


class CSVExporter:
    """
    Exportador CSV optimizado con formato científico.
    """
    
    def __init__(self, calculations):
        self.calculations = calculations
    
    def export_optimized(self, file_path: str, include_steps: bool = False):
        """Exporta con formato científico optimizado."""
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            # Headers descriptivos
            headers = [
                'ID_Calculo', 'Fecha_Hora', 'Usuario', 'Tipo_Calculo',
                'pH', 'pOH', 'Concentracion_H_Plus_M', 'Concentracion_OH_Minus_M',
                'Temperatura_Celsius', 'Fuerza_Ionica_M', 'Tiempo_Calculo_ms',
                'Coeficiente_Actividad_H', 'Coeficiente_Actividad_OH',
                'Kw_Corregido', 'Capacidad_Buffer_mol_L_pH'
            ]
            
            if include_steps:
                headers.append('Pasos_Calculo')
            
            headers.append('Warnings')
            
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            # Datos
            for calc in self.calculations:
                row = [
                    str(calc.id),
                    calc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    calc.user.username if calc.user else 'Anónimo',
                    calc.get_calculation_type_display(),
                ]
                
                # Resultados con formato científico
                if calc.results:
                    row.extend([
                        self._format_number(calc.results.get('ph')),
                        self._format_number(calc.results.get('poh')),
                        self._format_scientific(calc.results.get('h_concentration')),
                        self._format_scientific(calc.results.get('oh_concentration')),
                        self._format_number(calc.temperature),
                        self._format_number(calc.ionic_strength),
                        calc.calculation_time_ms,
                        self._format_number(calc.results.get('activity_coefficient_h')),
                        self._format_number(calc.results.get('activity_coefficient_oh')),
                        self._format_scientific(calc.results.get('corrected_kw')),
                        self._format_scientific(calc.results.get('buffer_capacity'))
                    ])
                else:
                    row.extend([''] * 11)
                
                # Pasos si se incluyen
                if include_steps:
                    steps = '; '.join(calc.calculation_steps) if calc.calculation_steps else ''
                    row.append(steps)
                
                # Warnings
                warnings = '; '.join(calc.warnings) if calc.warnings else ''
                row.append(warnings)
                
                writer.writerow(row)
    
    def _format_number(self, value, precision: int = 4):
        """Formatea números con precisión controlada."""
        if value is None:
            return ''
        try:
            return f"{float(value):.{precision}f}"
        except (ValueError, TypeError):
            return str(value)
    
    def _format_scientific(self, value, precision: int = 3):
        """Formatea números en notación científica."""
        if value is None:
            return ''
        try:
            return f"{float(value):.{precision}e}"
        except (ValueError, TypeError):
            return str(value)


def _generate_pdf_statistics(calculations):
    """Genera estadísticas para el PDF."""
    stats = []
    count = calculations.count()
    
    if count == 0:
        return ["No hay cálculos para analizar"]
    
    # Distribución por tipo
    from collections import Counter
    calc_types = [calc.get_calculation_type_display() for calc in calculations]
    type_dist = Counter(calc_types)
    
    stats.append(f"Distribución por tipo de cálculo:")
    for calc_type, count in type_dist.most_common():
        percentage = (count / len(calc_types)) * 100
        stats.append(f"  - {calc_type}: {count} ({percentage:.1f}%)")
    
    # Estadísticas de tiempo
    times = [calc.calculation_time_ms for calc in calculations]
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        stats.append(f"Tiempo de cálculo: promedio {avg_time:.1f}ms (rango: {min_time}-{max_time}ms)")
    
    # Estadísticas de pH
    ph_values = []
    for calc in calculations:
        if calc.results and 'ph' in calc.results and calc.results['ph'] is not None:
            ph_values.append(calc.results['ph'])
    
    if ph_values:
        avg_ph = sum(ph_values) / len(ph_values)
        min_ph = min(ph_values)
        max_ph = max(ph_values)
        stats.append(f"Valores de pH: promedio {avg_ph:.2f} (rango: {min_ph:.2f}-{max_ph:.2f})")
    
    return stats


def _generate_pdf_table_data(calculations, include_steps, include_warnings):
    """Genera datos para la tabla del PDF."""
    headers = ['Fecha', 'Tipo', 'pH', 'Temp.', 'Tiempo']
    
    if include_warnings:
        headers.append('Warnings')
    
    table_data = [headers]
    
    for calc in calculations[:50]:  # Limitar para PDF
        row = [
            calc.created_at.strftime('%d/%m'),
            calc.get_calculation_type_display()[:15],
            f"{calc.results.get('ph', 'N/A'):.2f}" if calc.results and calc.results.get('ph') else 'N/A',
            f"{calc.temperature}°C",
            f"{calc.calculation_time_ms}ms"
        ]
        
        if include_warnings:
            warnings_text = ', '.join(calc.warnings[:2]) if calc.warnings else '-'
            if len(warnings_text) > 30:
                warnings_text = warnings_text[:27] + '...'
            row.append(warnings_text)
        
        table_data.append(row)
    
    return table_data


def cleanup_expired_exports():
    """
    Función utilitaria para limpiar archivos de exportación expirados.
    Se puede llamar desde un cron job o tarea programada.
    """
    export_dir = os.path.join(settings.MEDIA_ROOT, 'exports')
    
    if not os.path.exists(export_dir):
        return
    
    # Archivos más antiguos de 48 horas se consideran expirados
    expiry_time = timezone.now() - timedelta(hours=48)
    
    for filename in os.listdir(export_dir):
        file_path = os.path.join(export_dir, filename)
        
        if os.path.isfile(file_path):
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            file_time = timezone.make_aware(file_time)
            
            if file_time < expiry_time:
                try:
                    os.remove(file_path)
                    print(f"Removed expired export file: {filename}")
                except OSError as e:
                    print(f"Error removing file {filename}: {e}")


def generate_calculation_report(calculation_id: str, detailed: bool = True) -> str:
    """
    Genera un reporte individual detallado para un cálculo específico.
    
    Args:
        calculation_id: ID del cálculo
        detailed: Si incluir análisis detallado
        
    Returns:
        str: Ruta del archivo generado
    """
    from .models import PHCalculationHistory
    
    try:
        calculation = PHCalculationHistory.objects.get(id=calculation_id)
    except PHCalculationHistory.DoesNotExist:
        raise ValueError(f"Cálculo con ID {calculation_id} no encontrado")
    
    # Preparar datos para reporte individual
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'calculation_report_{calculation_id}_{timestamp}.pdf'
    file_path = os.path.join(settings.MEDIA_ROOT, 'exports', filename)
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Crear PDF individual
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Título
    story.append(Paragraph(f"Reporte de Cálculo Individual - {calculation.id}", styles['Title']))
    story.append(Spacer(1, 20))
    
    # Información básica
    info_data = [
        ['Campo', 'Valor'],
        ['ID del Cálculo', str(calculation.id)],
        ['Fecha y Hora', calculation.created_at.strftime('%d/%m/%Y %H:%M:%S')],
        ['Usuario', calculation.user.username if calculation.user else 'Anónimo'],
        ['Tipo de Cálculo', calculation.get_calculation_type_display()],
        ['Temperatura', f"{calculation.temperature}°C"],
        ['Fuerza Iónica', f"{calculation.ionic_strength} M" if calculation.ionic_strength else 'N/A'],
        ['Tiempo de Cálculo', f"{calculation.calculation_time_ms} ms"],
    ]
    
    info_table = Table(info_data)
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Resultados
    if calculation.results:
        story.append(Paragraph("Resultados del Cálculo", styles['Heading2']))
        
        results_data = [['Parámetro', 'Valor', 'Unidad']]
        
        result_mappings = {
            'ph': ('pH', ''),
            'poh': ('pOH', ''),
            'h_concentration': ('Concentración H+', 'M'),
            'oh_concentration': ('Concentración OH-', 'M'),
            'activity_coefficient_h': ('Coef. Actividad H+', ''),
            'activity_coefficient_oh': ('Coef. Actividad OH-', ''),
            'corrected_kw': ('Kw Corregido', ''),
            'buffer_capacity': ('Capacidad Buffer', 'mol/L/pH')
        }
        
        for key, (name, unit) in result_mappings.items():
            if key in calculation.results and calculation.results[key] is not None:
                value = calculation.results[key]
                if isinstance(value, float):
                    if value < 0.001 or value > 1000:
                        formatted_value = f"{value:.3e}"
                    else:
                        formatted_value = f"{value:.4f}"
                else:
                    formatted_value = str(value)
                
                results_data.append([name, formatted_value, unit])
        
        results_table = Table(results_data)
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(results_table)
        story.append(Spacer(1, 20))
    
    # Pasos del cálculo
    if detailed and calculation.calculation_steps:
        story.append(Paragraph("Pasos del Cálculo", styles['Heading2']))
        for step in calculation.calculation_steps:
            story.append(Paragraph(f"• {step}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Warnings
    if calculation.warnings:
        story.append(Paragraph("Advertencias", styles['Heading2']))
        for warning in calculation.warnings:
            story.append(Paragraph(f"⚠ {warning}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Generar PDF
    doc.build(story)
    
    return file_path