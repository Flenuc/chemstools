"use client";

import React, { useState, useCallback, useRef } from 'react';
import { Layout, Row, Col, Tabs, Breadcrumb, Typography, FloatButton, Card, message, Segmented } from 'antd';
import { HomeOutlined, ExperimentOutlined, HistoryOutlined, BarChartOutlined, QuestionCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { BeakerIcon } from '@heroicons/react/24/outline';

// Importación de componentes
import AdvancedPHCalculator from '../../../components/calculators/AdvancedPHCalculator';
import PHVisualization from '../../../components/calculators/PHVisualization';
import PHPresets from '../../../components/calculators/PHPresets';
import PHHistory from '../../../components/calculators/PHHistory';
import PHStats from '../../../components/calculators/PHStats';
import BufferDesigner from '../../../components/calculators/BufferDesigner';
import { useAppDispatch } from '../../../store/hooks';
import { calculateAdvancedPH } from '../../../store/advancedPHSlice';
import { CalculationType, InputType, CalculationInput } from '../../../types/advancedPH';

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
    const [activeTab, setActiveTab] = useState('calculator');
    const [selectedPresetData, setSelectedPresetData] = useState<CalculationInput | null>(null);
    const [calculationResults, setCalculationResults] = useState<any[]>([]);
    const [lastCalculationId, setLastCalculationId] = useState<string | null>(null);
    const [visualizationType, setVisualizationType] = useState<'bar' | 'line' | 'radial' | 'comparison'>('bar');
    const calculationCompleteRef = useRef<boolean>(false);
    const visualizationSectionRef = useRef<HTMLDivElement>(null);
    const dispatch = useAppDispatch();

    const handleBufferDesigned = (buffer: any) => {
        const payload: CalculationInput = {
            calculation_type: CalculationType.Buffer,
            input_type: InputType.PH,
            input_value: buffer.finalPH,
            temperature: 25,
            show_steps: true,
            buffer_components: [
                { compound: buffer.acid.formula, concentration: buffer.acid.concentration, pka: buffer.acid.pKa },
                { compound: buffer.base.formula, concentration: buffer.base.concentration }
            ]
        };
        // Establecer los datos para sincronizar con la calculadora
        setSelectedPresetData(payload);
        setActiveTab('calculator');
    };

    // Manejar cuando se selecciona un preset
    const handlePresetSelect = useCallback((preset: any) => {
        console.log('Preset seleccionado:', preset);
        
        // Determinar el tipo de cálculo basado en el preset
        let calculationType = CalculationType.ConcentrationToPH;
        let inputType = InputType.HConcentration;
        let inputValue = 0.1;
        
        if (preset.values) {
            // Si el preset tiene estructura de valores específica
            if (preset.values.mode === 'concentration_to_ph') {
                calculationType = CalculationType.ConcentrationToPH;
                inputType = preset.values.solute?.includes('OH') ? InputType.OHConcentration : InputType.HConcentration;
                inputValue = preset.values.concentration || 0.1;
            } else if (preset.values.mode === 'ph_to_all') {
                calculationType = CalculationType.PHToAll;
                inputType = preset.values.inputType === 'pOH' ? InputType.POH : InputType.PH;
                inputValue = preset.values.inputValue || 7.0;
            } else if (preset.values.mode === 'buffer') {
                calculationType = CalculationType.Buffer;
                inputType = InputType.PH;
                inputValue = preset.values.targetPH || 7.0;
            }
        } else {
            // Estructura simple de preset
            if (preset.type === 'acid') {
                inputType = InputType.HConcentration;
            } else if (preset.type === 'base') {
                inputType = InputType.OHConcentration;
            }
            inputValue = preset.concentration || 0.1;
        }
        
        // Convertir el preset a CalculationInput
        const calculationInput: CalculationInput = {
            calculation_type: calculationType,
            input_type: inputType,
            input_value: inputValue,
            temperature: preset.values?.temperature || preset.temperature || 25,
            show_steps: true,
        };

        // Si es un buffer, agregar los componentes
        if (preset.values?.buffer) {
            calculationInput.buffer_components = [
                {
                    compound: preset.values.buffer.acidName || 'CH3COOH',
                    concentration: preset.values.buffer.acidConcentration || 0.1,
                    pka: preset.values.buffer.pka || 4.76
                },
                {
                    compound: preset.values.buffer.baseName || 'CH3COO-',
                    concentration: preset.values.buffer.baseConcentration || 0.1
                }
            ];
        } else if (preset.buffer_components) {
            calculationInput.buffer_components = preset.buffer_components;
        }

        setSelectedPresetData(calculationInput);
        message.success(`Preset "${preset.name}" aplicado a la calculadora`);
    }, []);

    // Manejar duplicación de cálculo desde el historial
    const handleDuplicateCalculation = useCallback((calculation: any) => {
        console.log('Duplicando cálculo:', calculation);
        
        // Extraer los datos de entrada del cálculo original
        const inputData = calculation.input_data || calculation.inputData || {};
        const calcType = calculation.calculation_type || calculation.calculationType || CalculationType.ConcentrationToPH;
        
        // Crear el objeto CalculationInput desde los datos del historial
        const duplicatedInput: CalculationInput = {
            calculation_type: calcType,
            input_type: inputData.input_type || InputType.PH,
            input_value: inputData.input_value || 7.0,
            temperature: inputData.temperature || 25,
            show_steps: true,
            ionic_strength: inputData.ionic_strength,
            include_activity: inputData.include_activity,
            buffer_components: inputData.buffer_components
        };
        
        // Establecer los datos duplicados en la calculadora
        setSelectedPresetData(duplicatedInput);
        message.success('Cálculo duplicado en la calculadora');
    }, []);

    // Manejar cuando se completa un cálculo
    const handleCalculationComplete = useCallback((result: any) => {
        // Evitar loops verificando si ya procesamos este resultado
        const resultId = result?.metadata?.calculation_id || result?.timestamp || Date.now().toString();
        
        if (result && result.results && resultId !== lastCalculationId) {
            setLastCalculationId(resultId);
            
            // Agregar el resultado a la lista para visualización
            const newDataPoint = {
                id: resultId,
                name: `Cálculo ${calculationResults.length + 1}`,
                ph: result.results.ph,
                poh: result.results.poh,
                h_concentration: result.results.h_concentration,
                oh_concentration: result.results.oh_concentration,
                is_acid: result.results.ph < 7,
                timestamp: new Date().toISOString(),
                calculation_type: result.calculation_type,
                temperature: result.temperature || 25,
                warnings: result.warnings,
                ...result.results
            };
            
            setCalculationResults(prev => {
                // Evitar duplicados
                if (prev.some(item => item.id === resultId)) {
                    return prev;
                }
                return [...prev, newDataPoint];
            });
            
            message.success('Cálculo completado y agregado a la visualización');
        }
    }, [lastCalculationId, calculationResults.length]);

    const renderCalculatorLayout = () => (
        <Row justify="center">
            {/* Contenedor principal centrado y con ancho máximo */}
            <Col xs={24} lg={22} xl={20} xxl={18}>
                <Row gutter={[24, 24]}>
                    {/* --- Sección Principal: Calculadora y Presets --- */}
                    <Col span={24}>
                        <AdvancedPHCalculator 
                            initialData={selectedPresetData}
                            onCalculationComplete={handleCalculationComplete}
                            onViewGraphs={() => {
                                // Hacer scroll a la sección de visualización
                                if (visualizationSectionRef.current) {
                                    visualizationSectionRef.current.scrollIntoView({ 
                                        behavior: 'smooth',
                                        block: 'start'
                                    });
                                    message.info('Desplazándose a la sección de visualización');
                                }
                            }}
                        />
                    </Col>
                    <Col span={24}>
                        <PHPresets onPresetSelect={handlePresetSelect} />
                    </Col>

                    {/* --- Sección Secundaria: Visualización e Historial --- */}
                    <Col span={24}>
                        <div ref={visualizationSectionRef}>
                        <Card 
                            title="Visualización de Resultados"
                            extra={
                                <Segmented
                                    value={visualizationType}
                                    onChange={(value) => setVisualizationType(value as any)}
                                    options={[
                                        { label: 'Barras', value: 'bar' },
                                        { label: 'Líneas', value: 'line' },
                                        { label: 'Radial', value: 'radial' },
                                        { label: 'Comparación', value: 'comparison', disabled: calculationResults.length < 2 }
                                    ]}
                                />
                            }
                        >
                            <PHVisualization 
                                data={calculationResults.length > 0 ? calculationResults : mockVisualizationData} 
                                chartType={visualizationType}
                                key={`viz-${calculationResults.length}-${visualizationType}`}
                            />
                        </Card>
                        </div>
                    </Col>
                    <Col span={24}>
                         <PHHistory 
                            userId="mock-user-123" 
                            onDuplicateCalculation={handleDuplicateCalculation}
                         />
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
            children: <BufferDesigner onBufferDesigned={handleBufferDesigned} />
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