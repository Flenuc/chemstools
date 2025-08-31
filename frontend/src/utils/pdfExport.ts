import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

// Declaración de tipos para autoTable
declare module 'jspdf' {
    interface jsPDF {
        lastAutoTable: {
            finalY: number;
        };
    }
}

interface PHCalculationResults {
    ph: number;
    poh: number;
    h_concentration: number;
    oh_concentration: number;
    temperature?: number;
    calculation_type?: string;
    warnings?: string[];
    calculation_steps?: string[];
}

export const exportPHResultsToPDF = (results: PHCalculationResults, filename: string = 'ph-calculation-results.pdf') => {
    const doc = new jsPDF();
    
    // Título
    doc.setFontSize(20);
    doc.text('Resultados de Cálculo de pH/pOH', 105, 20, { align: 'center' });
    
    // Fecha y hora
    doc.setFontSize(10);
    doc.text(`Fecha: ${new Date().toLocaleString()}`, 20, 35);
    
    // Línea separadora
    doc.setLineWidth(0.5);
    doc.line(20, 40, 190, 40);
    
    // Resultados principales
    doc.setFontSize(14);
    doc.text('Resultados Principales:', 20, 50);
    
    // Tabla de resultados
    const resultsData = [
        ['Parámetro', 'Valor', 'Unidad'],
        ['pH', results.ph.toFixed(2), ''],
        ['pOH', results.poh.toFixed(2), ''],
        ['[H+]', results.h_concentration.toExponential(3), 'M'],
        ['[OH-]', results.oh_concentration.toExponential(3), 'M'],
    ];
    
    if (results.temperature) {
        resultsData.push(['Temperatura', results.temperature.toString(), '°C']);
    }
    
    autoTable(doc, {
        startY: 55,
        head: [resultsData[0]],
        body: resultsData.slice(1),
        theme: 'striped',
        headStyles: { fillColor: [59, 130, 246] },
        columnStyles: {
            0: { fontStyle: 'bold' },
            1: { halign: 'center' },
            2: { halign: 'center' }
        }
    });
    
    let currentY = doc.lastAutoTable.finalY + 10;
    
    // Clasificación
    doc.setFontSize(12);
    const classification = results.ph < 7 ? 'Ácido' : results.ph > 7 ? 'Básico' : 'Neutro';
    const classificationColor: [number, number, number] = results.ph < 7 ? [239, 68, 68] : results.ph > 7 ? [59, 130, 246] : [34, 197, 94];
    doc.setTextColor(classificationColor[0], classificationColor[1], classificationColor[2]);
    doc.text(`Clasificación: ${classification}`, 20, currentY);
    doc.setTextColor(0, 0, 0);
    
    currentY += 10;
    
    // Advertencias si existen
    if (results.warnings && results.warnings.length > 0) {
        doc.setFontSize(12);
        doc.setTextColor(251, 146, 60);
        doc.text('Advertencias:', 20, currentY);
        doc.setTextColor(0, 0, 0);
        currentY += 7;
        
        doc.setFontSize(10);
        results.warnings.forEach(warning => {
            const lines = doc.splitTextToSize(warning, 170);
            doc.text(lines, 25, currentY);
            currentY += lines.length * 5;
        });
        
        currentY += 5;
    }
    
    // Pasos del cálculo si existen
    if (results.calculation_steps && results.calculation_steps.length > 0) {
        // Verificar si necesitamos una nueva página
        if (currentY > 240) {
            doc.addPage();
            currentY = 20;
        }
        
        doc.setFontSize(14);
        doc.text('Proceso de Cálculo:', 20, currentY);
        currentY += 10;
        
        doc.setFontSize(10);
        results.calculation_steps.forEach((step, index) => {
            // Verificar si necesitamos una nueva página
            if (currentY > 260) {
                doc.addPage();
                currentY = 20;
            }
            
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text(`Paso ${index + 1}:`, 20, currentY);
            doc.setFont('helvetica', 'normal');
            currentY += 7;
            
            doc.setFontSize(10);
            const lines = doc.splitTextToSize(step, 170);
            doc.text(lines, 25, currentY);
            currentY += lines.length * 5 + 5;
        });
    }
    
    // Pie de página
    const pageCount = doc.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.text(`Página ${i} de ${pageCount}`, 105, 285, { align: 'center' });
        doc.text('Generado por Calculadora Avanzada de pH - ChemsTools', 105, 290, { align: 'center' });
    }
    
    // Descargar el PDF
    doc.save(filename);
    
    return doc;
};

// Función para generar y mostrar preview del PDF
export const previewPHResultsPDF = (results: PHCalculationResults): string => {
    const doc = exportPHResultsToPDF(results, 'preview.pdf');
    return doc.output('datauristring');
};
