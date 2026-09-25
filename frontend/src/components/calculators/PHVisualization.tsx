import React, { useRef, useEffect, useState } from 'react';
import {
    ResponsiveContainer,
    BarChart,
    Bar,
    LineChart,
    Line,
    RadialBarChart,
    RadialBar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    PolarAngleAxis,
    Cell,
} from 'recharts';
import { Card, Typography, Button, Row, Col, Empty, notification } from 'antd';
import { motion } from 'framer-motion';
import { CameraIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import { toPng, toSvg } from 'html-to-image';
// Asumiendo que los tipos están en un archivo compartido, si no, importarlos desde AdvancedPHCalculator
import  CalculationResult  from './AdvancedPHCalculator';

// --- Tipos de Datos (Extendidos para comparación) ---
interface PHCalculationResult {
    id: string; // Identificador único para cada cálculo
    name: string; // Nombre descriptivo, ej: "HCl 0.1M"
    ph: number;
    poh: number;
    h_concentration: number;
    oh_concentration: number;
    is_acid: boolean;
}

interface PHVisualizationProps {
    data: PHCalculationResult[];
    chartType?: 'bar' | 'line' | 'radial' | 'comparison';
    showLegend?: boolean;
    height?: number;
}

// --- Helper Functions ---

/**
 * Devuelve un color HSL basado en el valor de pH.
 * @param ph - El valor de pH (0-14).
 * @returns Una cadena de color HSL.
 */
const getColorForPH = (ph: number): string => {
    // Mapeo de pH a HUE (0=rojo, 60=amarillo, 120=verde, 240=azul)
    const hue = Math.max(0, Math.min(240, 240 - (ph * 17)));
    return `hsl(${hue}, 80%, 50%)`;
};

/**
 * Formateador para tooltips de Recharts.
 */
const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        return (
            <div className="p-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded shadow-lg">
                <p className="font-bold">{label || payload[0].payload.name}</p>
                {payload.map((entry: any, index: number) => (
                    <p key={`item-${index}`} style={{ color: entry.color }}>
                        {`${entry.name}: ${entry.value.toExponential(2)}`}
                    </p>
                ))}
            </div>
        );
    }
    return null;
};


// --- Componente Principal ---
const PHVisualization: React.FC<PHVisualizationProps> = ({
    data,
    chartType = 'bar',
    showLegend = true,
    height = 400,
}) => {
    const chartRef = useRef<HTMLDivElement>(null);
    const [chartData, setChartData] = useState<PHCalculationResult[]>([]);
    const [forceUpdate, setForceUpdate] = useState(0);

    // Efecto para actualizar los datos cuando cambien
    useEffect(() => {
        if (data && data.length > 0) {
            setChartData([...data]);
            // Forzar actualización del gráfico
            setForceUpdate(prev => prev + 1);
        }
    }, [data]);

    // --- Lógica de Exportación ---
    const handleExport = async (format: 'png' | 'svg') => {
    if (!chartRef.current) return;
    
    try {
        const dataUrl = format === 'png' 
            ? await toPng(chartRef.current)
            : await toSvg(chartRef.current);
        
        const link = document.createElement('a');
        link.download = `ph-chart-${Date.now()}.${format}`;
        link.href = dataUrl;
        link.click();
        
        notification.success({
            message: 'Exportación Exitosa',
            description: `Gráfico exportado como ${format.toUpperCase()}`,
        });
    } catch (error) {
        console.error('Error:', error);
        notification.error({
            message: 'Error al exportar',
            description: 'No se pudo exportar el gráfico',
        });
    }
 };

    if (!chartData || chartData.length === 0) {
        return (
            <Card style={{ height }}>
                <Empty description="No hay datos para visualizar. Realice un cálculo primero." />
            </Card>
        );
    }

    // Usar el último resultado para gráficos simples
    const latestData = chartData[chartData.length - 1];
    const concentrationData = [
        { name: '[H+]', value: latestData.h_concentration, fill: '#ef4444' },
        { name: '[OH-]', value: latestData.oh_concentration, fill: '#3b82f6' },
    ];

    // Preparar datos para comparación múltiple
    const comparisonData = chartData.map((item, index) => ({
        ...item,
        index: index + 1,
        displayName: item.name || `Cálculo ${index + 1}`
    }));

    const renderChart = () => {
        switch (chartType) {
            case 'radial':
                return (
                     <RadialBarChart
                        innerRadius="20%"
                        outerRadius="80%"
                        data={[{ name: 'pH', value: latestData.ph, fill: getColorForPH(latestData.ph) }]}
                        startAngle={180}
                        endAngle={0}
                    >
                        <PolarAngleAxis type="number" domain={[0, 14]} angleAxisId={0} tick={false} />
                        <RadialBar background dataKey="value" angleAxisId={0} />
                        <Legend iconSize={10} layout="vertical" verticalAlign="middle" align="right" />
                        <Tooltip />
                    </RadialBarChart>
                );

            case 'comparison':
                 return (
                    <BarChart data={comparisonData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="displayName" />
                        <YAxis domain={[0, 14]} />
                        <Tooltip />
                        {showLegend && <Legend />}
                        <Bar dataKey="ph" name="pH">
                            {comparisonData.map((entry, index) => (
                                <Cell key={`cell-ph-${index}`} fill={getColorForPH(entry.ph)} />
                            ))}
                        </Bar>
                        <Bar dataKey="poh" name="pOH" fill="#8884d8" />
                    </BarChart>
                );

            case 'line':
                return (
                    <LineChart data={concentrationData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis scale="log" domain={['auto', 'auto']} />
                        <Tooltip content={<CustomTooltip />} />
                        {showLegend && <Legend />}
                        <Line type="monotone" dataKey="value" name="Concentración (M)" stroke="#8884d8" />
                    </LineChart>
                );

            case 'bar':
            default:
                return (
                    <BarChart data={concentrationData} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" scale="log" domain={[1e-15, 10]} />
                        <YAxis type="category" dataKey="name" width={60} />
                        <Tooltip content={<CustomTooltip />} />
                        {showLegend && <Legend />}
                        <Bar dataKey="value" name="Concentración (M)" />
                    </BarChart>
                );
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <Card 
                title={<Typography.Title level={4}>Visualización de Resultados</Typography.Title>}
                extra={
                    <div>
                        <Button onClick={() => handleExport('png')} icon={<CameraIcon className="h-4 w-4" />} className="mr-2">PNG</Button>
                        <Button onClick={() => handleExport('svg')} icon={<ArrowDownTrayIcon className="h-4 w-4" />}>SVG</Button>
                    </div>
                }
            >
                <Row align="middle" gutter={16}>
                    <Col xs={24} md={4}>
                        <div className="flex flex-col items-center">
                            <Typography.Text strong>Escala de pH</Typography.Text>
                             <div className="w-full h-8 my-2 rounded-md" style={{ background: 'linear-gradient(to right, #ef4444, #f59e0b, #84cc16, #3b82f6)' }} />
                             <div className="relative w-full h-4">
                                <div className="absolute top-0 h-4 w-1 bg-black dark:bg-white" style={{ left: `${(latestData.ph / 14) * 100}%` }} />
                             </div>
                             <Typography.Title level={5}>{latestData.ph.toFixed(2)}</Typography.Title>
                        </div>
                    </Col>
                    <Col xs={24} md={20}>
                        <div ref={chartRef} style={{ height, width: '100%' }} key={`chart-${forceUpdate}`}>
                            <ResponsiveContainer>
                                {renderChart()}
                            </ResponsiveContainer>
                        </div>
                    </Col>
                </Row>
            </Card>
        </motion.div>
    );
};

export default PHVisualization;