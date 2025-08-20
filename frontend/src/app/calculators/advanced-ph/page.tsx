"use client";

import React from 'react';
import { Layout, Row, Col, Tabs, Breadcrumb, Typography, FloatButton, Card } from 'antd';
import { HomeOutlined, ExperimentOutlined, HistoryOutlined, BarChartOutlined, QuestionCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { BeakerIcon } from '@heroicons/react/24/outline';

// Importación de componentes
import AdvancedPHCalculator from '../../../components/calculators/AdvancedPHCalculator';
import PHVisualization from '../../../components/calculators/PHVisualization';
import PHPresets from '../../../components/calculators/PHPresets';
import PHHistory from '../../../components/calculators/PHHistory';
import PHStats from '../../../components/calculators/PHStats';
import BufferDesigner from '../../../components/calculators/BufferDesigner';

const { Content } = Layout;
const { Title } = Typography;

// Mock de datos para visualización
const mockVisualizationData = [{
    id: '1',
    name: 'HCl 0.1M',
    ph: 1.0,
    poh: 13.0,
    h_concentration: 0.1,
    oh_concentration: 1e-13,
    is_acid: true,
}];

const AdvancedPHCalculatorPage: React.FC = () => {
    const [activeTab, setActiveTab] = React.useState('calculator');

    const renderCalculatorLayout = () => (
        <Row justify="center">
            {/* Contenedor principal centrado y con ancho máximo */}
            <Col xs={24} lg={22} xl={20} xxl={18}>
                <Row gutter={[24, 24]}>
                    {/* --- Sección Principal: Calculadora y Presets --- */}
                    <Col span={24}>
                        <AdvancedPHCalculator />
                    </Col>
                    <Col span={24}>
                        <PHPresets onPresetSelect={(preset) => console.log('Preset selected:', preset)} />
                    </Col>

                    {/* --- Sección Secundaria: Visualización e Historial --- */}
                    <Col span={24}>
                        <PHVisualization data={mockVisualizationData} />
                    </Col>
                    <Col span={24}>
                         <PHHistory userId="mock-user-123" />
                    </Col>
                </Row>
            </Col>
        </Row>
    );

    const tabItems = [
        {
            key: 'calculator',
            label: (<span><ExperimentOutlined /> Calculadora</span>),
            children: renderCalculatorLayout()
        },
        {
            key: 'buffer_designer',
            label: (<span><BeakerIcon className="h-4 w-4 inline-block mr-1" /> Diseñador de Buffer</span>),
            children: <BufferDesigner onBufferDesigned={(buffer) => console.log(buffer)} />
        },
        {
            key: 'stats',
            label: (<span><BarChartOutlined /> Estadísticas</span>),
            children: <PHStats userId="mock-user-123" />
        },
        {
            key: 'help',
            label: (<span><QuestionCircleOutlined /> Ayuda</span>),
            children: (
                <Card title="Guía de Uso">
                    <p>Utiliza el formulario en la pestaña 'Calculadora' para introducir los datos de tu cálculo.</p>
                    <p>Puedes usar los presets para cargar rápidamente soluciones comunes.</p>
                    <p>Los resultados, gráficos y el historial completo aparecerán debajo del formulario principal.</p>
                    <p>Usa la pestaña 'Diseñador de Buffer' para crear soluciones tampón personalizadas.</p>
                </Card>
            )
        }
    ];

    return (
        <Layout className="p-4 sm:p-6 bg-gray-50 dark:bg-gray-900">
            <Content>
                <Breadcrumb
                    items={[
                        { href: '/', title: <HomeOutlined /> },
                        { href: '/calculators', title: 'Calculadoras' },
                        { title: 'pH/pOH Avanzada' },
                    ]}
                    className="mb-4"
                />
                <Title level={2}>Calculadora de pH/pOH Avanzada</Title>
                
                <Tabs 
                    activeKey={activeTab} 
                    onChange={setActiveTab} 
                    items={tabItems} 
                    type="card"
                />

                <FloatButton.Group
                    trigger="hover"
                    type="primary"
                    style={{ right: 24 }}
                    icon={<PlusOutlined />}
                >
                    <FloatButton tooltip="Nuevo Cálculo" icon={<ExperimentOutlined />} onClick={() => setActiveTab('calculator')} />
                    <FloatButton tooltip="Diseñar Buffer" icon={<BeakerIcon className="h-5 w-5" />} onClick={() => setActiveTab('buffer_designer')} />
                </FloatButton.Group>
            </Content>
        </Layout>
    );
};

export default AdvancedPHCalculatorPage;