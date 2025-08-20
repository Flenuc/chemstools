import React, { useMemo } from 'react';
import { Card, Statistic, Row, Col, Typography, Select, Button, Tag } from 'antd';
import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    Legend,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    ResponsiveContainer,
    BarChart,
    Bar,
} from 'recharts';
import { ChartBarIcon, LightBulbIcon, ArrowTrendingUpIcon, DocumentArrowDownIcon } from '@heroicons/react/24/outline';

// --- Tipos de Datos ---
interface PHStatsProps {
    userId: string;
    timeRange?: '7d' | '30d' | '90d' | '1y';
    showComparisons?: boolean;
}

// --- Mock Data ---
// En una aplicación real, estos datos vendrían de una API (ej: /api/calculators/stats?userId=...&range=7d)
const mockStatsData = {
    totalCalculations: 128,
    avgCalculationTime: 23, // ms
    warningRate: 0.15, // 15%
    typeDistribution: [
        { name: 'Concentración', value: 80 },
        { name: 'Buffer', value: 35 },
        { name: 'pH Inverso', value: 13 },
    ],
    activityLast7Days: [
        { date: 'Día -6', calculations: 5 },
        { date: 'Día -5', calculations: 8 },
        { date: 'Día -4', calculations: 12 },
        { date: 'Día -3', calculations: 7 },
        { date: 'Día -2', calculations: 15 },
        { date: 'Día -1', calculations: 20 },
        { date: 'Hoy', calculations: 25 },
    ],
    globalAverages: {
        avgCalculationTime: 35, // ms
    }
};

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

const PHStats: React.FC<PHStatsProps> = ({
    userId,
    timeRange = '7d',
    showComparisons = true,
}) => {

    const warningRatePercent = (mockStatsData.warningRate * 100).toFixed(1);

    const comparisonData = [
        { name: 'Tiempo de Cálculo (ms)', 'Tu Promedio': mockStatsData.avgCalculationTime, 'Promedio Global': mockStatsData.globalAverages.avgCalculationTime },
    ];

    return (
        <Card>
            <div className="flex justify-between items-center mb-4">
                <Typography.Title level={4} className="!mb-0">
                    <ChartBarIcon className="h-6 w-6 inline-block mr-2" />
                    Estadísticas de Uso
                </Typography.Title>
                <Select defaultValue={timeRange} style={{ width: 120 }}>
                    <Select.Option value="7d">Últimos 7 días</Select.Option>
                    <Select.Option value="30d">Últimos 30 días</Select.Option>
                    <Select.Option value="90d">Últimos 90 días</Select.Option>
                    <Select.Option value="1y">Último año</Select.Option>
                </Select>
            </div>

            {/* Métricas Clave */}
            <Row gutter={[16, 16]} className="mb-6">
                <Col xs={12} sm={6}><Statistic title="Cálculos Totales" value={mockStatsData.totalCalculations} /></Col>
                <Col xs={12} sm={6}><Statistic title="Tiempo Promedio" value={mockStatsData.avgCalculationTime} suffix="ms" /></Col>
                <Col xs={12} sm={6}><Statistic title="Tasa de Warnings" value={warningRatePercent} suffix="%" /></Col>
                <Col xs={12} sm={6}>
                    <Button icon={<DocumentArrowDownIcon className="h-4 w-4 mr-1" />}>Exportar Resumen</Button>
                </Col>
            </Row>

            {/* Gráficos */}
            <Row gutter={[24, 24]}>
                <Col xs={24} md={12} lg={8}>
                    <Card title="Distribución por Tipo">
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie data={mockStatsData.typeDistribution} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                                    {mockStatsData.typeDistribution.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </Card>
                </Col>
                <Col xs={24} md={12} lg={16}>
                    <Card title="Actividad Reciente">
                        <ResponsiveContainer width="100%" height={300}>
                            <AreaChart data={mockStatsData.activityLast7Days}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="date" />
                                <YAxis />
                                <Tooltip />
                                <Area type="monotone" dataKey="calculations" name="Cálculos" stroke="#8884d8" fill="#8884d8" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </Card>
                </Col>
                {showComparisons && (
                    <Col xs={24} lg={12}>
                        <Card title="Comparación de Rendimiento">
                             <ResponsiveContainer width="100%" height={300}>
                                <BarChart data={comparisonData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="Tu Promedio" fill="#8884d8" />
                                    <Bar dataKey="Promedio Global" fill="#82ca9d" />
                                </BarChart>
                            </ResponsiveContainer>
                        </Card>
                    </Col>
                )}
                 <Col xs={24} lg={12}>
                    <Card title="Insights y Recomendaciones">
                        <div style={{height: 300}} className="flex flex-col justify-around">
                            <div className="flex items-start">
                                <ArrowTrendingUpIcon className="h-6 w-6 mr-3 text-green-500" />
                                <div>
                                    <Typography.Text strong>Insight Químico:</Typography.Text>
                                    <p>La mayoría de tus cálculos son sobre ácidos y bases fuertes. ¡Gran dominio de los fundamentos!</p>
                                </div>
                            </div>
                            <div className="flex items-start">
                                <LightBulbIcon className="h-6 w-6 mr-3 text-yellow-500" />
                                <div>
                                    <Typography.Text strong>Recomendación de Aprendizaje:</Typography.Text>
                                    <p>Notamos que usas poco la calculadora de buffers. ¿Por qué no pruebas un preset de buffer acetato para explorar cómo resisten cambios de pH?</p>
                                </div>
                            </div>
                        </div>
                    </Card>
                </Col>
            </Row>
        </Card>
    );
};

export default PHStats;