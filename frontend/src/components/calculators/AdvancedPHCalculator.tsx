import React, { useState, useEffect, useRef } from 'react';
import {
    Form,
    Input,
    Select,
    Button,
    Switch,
    Tooltip,
    Card,
    Row,
    Col,
    Typography,
    Collapse,
    Spin,
    Alert,
    theme,
    message,
} from 'antd';
import { motion, AnimatePresence, Variants } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';
import { BeakerIcon, CalculatorIcon, InformationCircleIcon, SunIcon, MoonIcon, ChartBarIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import { useAppDispatch, useAppSelector } from '../../store/hooks'; // Hooks de Redux reales
import { calculateAdvancedPH } from '../../store/advancedPHSlice';
import { CalculationInput, CalculationType, InputType } from '../../types/advancedPH';
import { exportPHResultsToPDF } from '../../utils/pdfExport';

// Define missing types and constants
interface CalculationStep {
    title: string;
    explanation: string;
    formula: string;
}

const cardVariants: Variants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1 }
};

const itemVariants: Variants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
};

// Mock de presets, ya que no vienen del store por ahora
const mockPresets = [
    { label: 'Ácido Clorhídrico (HCl) 0.1M', value: 'hcl_0.1' },
    { label: 'Hidróxido de Sodio (NaOH) 0.1M', value: 'naoh_0.1' },
    { label: 'Buffer Acetato 0.1M/0.1M', value: 'acetate_buffer_0.1' },
];

interface AdvancedPHCalculatorProps {
    initialData?: CalculationInput | null;
    onCalculationComplete?: (result: any) => void;
    onViewGraphs?: () => void;
}

 const AdvancedPHCalculator: React.FC<AdvancedPHCalculatorProps> = ({ 
    initialData,
    onCalculationComplete,
    onViewGraphs 
}) => {
    const [form] = Form.useForm();
    const dispatch = useAppDispatch();
    
    // Conexión al estado real de Redux
    const { calculationResult, isCalculating, errors } = useAppSelector((state) => state.advancedPH);
    
    // Estado local para el modo de cálculo y el tema
    const [calculationMode, setCalculationMode] = useState<CalculationType>(CalculationType.ConcentrationToPH);
    const [isDarkMode, setIsDarkMode] = useState(false); // Asumimos un tema claro por defecto

    // Declara showAdvancedOptions, presets, y funciones faltantes
    const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
    const [presets] = useState(mockPresets);

    // Estado para selección de sistemas buffer
    const [selectedBufferSystem, setSelectedBufferSystem] = useState<string | null>(null);
    const [showSteps, setShowSteps] = useState(false);
    const visualizationRef = useRef<HTMLDivElement>(null);

    // Efecto para sincronizar con initialData cuando cambie
    useEffect(() => {
        if (initialData) {
            // Establecer el modo de cálculo
            setCalculationMode(initialData.calculation_type);
            
            // Establecer valores del formulario
            const formValues: any = {
                calculation_type: initialData.calculation_type,
                input_type: initialData.input_type,
                input_value: initialData.input_value,
                temperature: initialData.temperature || 25,
            };

            // Si es un cálculo de buffer, manejar los componentes
            if (initialData.calculation_type === CalculationType.Buffer && initialData.buffer_components) {
                // Detectar sistema buffer predefinido o custom
                const firstComponent = initialData.buffer_components[0];
                const secondComponent = initialData.buffer_components[1];
                
                if (firstComponent?.compound === 'CH3COOH' && secondComponent?.compound === 'CH3COO-') {
                    setSelectedBufferSystem('acetate');
                    // Calcular concentración total
                    const totalConc = (firstComponent.concentration || 0) + (secondComponent?.concentration || 0);
                    formValues.buffer_concentration = totalConc;
                } else if (firstComponent?.compound === 'H2PO4-' && secondComponent?.compound === 'HPO4^2-') {
                    setSelectedBufferSystem('phosphate');
                    const totalConc = (firstComponent.concentration || 0) + (secondComponent?.concentration || 0);
                    formValues.buffer_concentration = totalConc;
                } else if (firstComponent?.compound === '(HOCH2)3CNH3+' && secondComponent?.compound === '(HOCH2)3CNH2') {
                    setSelectedBufferSystem('tris');
                    const totalConc = (firstComponent.concentration || 0) + (secondComponent?.concentration || 0);
                    formValues.buffer_concentration = totalConc;
                } else if (firstComponent?.compound === 'HCO3-' && secondComponent?.compound === 'CO3^2-') {
                    setSelectedBufferSystem('carbonate');
                    const totalConc = (firstComponent.concentration || 0) + (secondComponent?.concentration || 0);
                    formValues.buffer_concentration = totalConc;
                } else {
                    // Es un buffer personalizado
                    setSelectedBufferSystem('custom');
                    formValues.buffer_acid = {
                        compound: firstComponent?.compound,
                        concentration: firstComponent?.concentration,
                        pka: firstComponent?.pka
                    };
                    formValues.buffer_base = {
                        compound: secondComponent?.compound,
                        concentration: secondComponent?.concentration
                    };
                }
            }

            // Si hay corrección de actividad
            if (initialData.calculation_type === CalculationType.ActivityCorrection) {
                formValues.ionic_strength = initialData.ionic_strength;
                formValues.include_activity = initialData.include_activity !== false;
            }

            // Aplicar valores al formulario
            form.setFieldsValue(formValues);
        }
    }, [initialData, form]);

    // Efecto para llamar al callback cuando el cálculo se complete exitosamente
    useEffect(() => {
        // Solo ejecutar si hay un resultado nuevo y no estamos calculando
        if (calculationResult && !isCalculating && onCalculationComplete) {
            // Usar un timeout para evitar llamadas inmediatas que puedan causar loops
            const timeoutId = setTimeout(() => {
                onCalculationComplete(calculationResult);
            }, 100);
            
            return () => clearTimeout(timeoutId);
        }
    }, [calculationResult?.metadata?.calculation_id, isCalculating]); // Solo depender del ID del cálculo, no del objeto completo

    const handlePresetChange = (value: string) => {
        // Implementar lógica para actualizar valores basados en el preset
        console.log("Preset changed:", value);
    };

    const handleBufferSystemChange = (val: string) => {
        setSelectedBufferSystem(val);
        if (val !== 'custom') {
            // Precargar valores por defecto si no es personalizado
            form.setFieldsValue({
                buffer_concentration: 0.1,
            });
        }
    };

    const getBufferSystemInfo = (val: string | null) => {
        switch (val) {
            case 'acetate':
                return 'Acetato: Ácido acético/Acetato (pKa 4.76). Buen rango ~3.8-5.8.';
            case 'phosphate':
                return 'Fosfato: H2PO4-/HPO4^2- (pKa 7.21). Buen rango ~6.2-8.2.';
            case 'tris':
                return 'TRIS: Buen rango ~7.1-9.1 con pKa 8.07. Sensible a T.';
            case 'carbonate':
                return 'Carbonato: HCO3-/CO3^2- (pKa 10.33). Rango ~9.3-11.3.';
            default:
                return '';
        }
    };

    const renderDynamicFields = () => {
        switch (calculationMode) {
            case CalculationType.ConcentrationToPH:
                return (
                    <>
                        <Form.Item name="input_type" label="Tipo de Concentración" initialValue={InputType.HConcentration}>
                            <Select>
                                <Select.Option value={InputType.HConcentration}>Concentración [H+]</Select.Option>
                                <Select.Option value={InputType.OHConcentration}>Concentración [OH-]</Select.Option>
                            </Select>
                        </Form.Item>
                        <Form.Item name="input_value" label="Concentración (M)" rules={[{ required: true, message: 'Por favor ingrese un valor' }]}>
                            <Input type="number" step="0.0001" min="0" placeholder="Ej: 0.1" />
                        </Form.Item>
                    </>
                );
            case CalculationType.PHToAll:
                return (
                    <>
                        <Form.Item name="input_type" label="Tipo de Valor" initialValue={InputType.PH}>
                            <Select>
                                <Select.Option value={InputType.PH}>pH</Select.Option>
                                <Select.Option value={InputType.POH}>pOH</Select.Option>
                            </Select>
                        </Form.Item>
                        <Form.Item name="input_value" label="Valor" rules={[{ required: true, message: 'Por favor ingrese un valor' }]}>
                            <Input type="number" />
                        </Form.Item>
                    </>
                );
            case CalculationType.Buffer:
                return (
                    <>
                        <Form.Item name="input_type" label="Tipo de entrada" initialValue={InputType.PH}>
                            <Select disabled>
                                <Select.Option value={InputType.PH}>pH</Select.Option>
                            </Select>
                        </Form.Item>
                        <Form.Item name="input_value" label="pH Objetivo del Buffer" rules={[{ required: true, message: 'Por favor ingrese el pH objetivo' }]}>
                            <Input type="number" step="0.01" min="0" max="14" placeholder="Ej: 7.4" />
                        </Form.Item>
                        
                        {/* Componentes del buffer */}
                        <Form.Item label="Sistema Buffer" required>
                            <Select 
                                placeholder="Seleccione un sistema buffer"
                                onChange={handleBufferSystemChange}
                                value={selectedBufferSystem}
                            >
                                <Select.Option value="acetate">Buffer de Acetato (pKa = 4.76)</Select.Option>
                                <Select.Option value="phosphate">Buffer de Fosfato (pKa = 7.21)</Select.Option>
                                <Select.Option value="tris">Buffer TRIS (pKa = 8.07)</Select.Option>
                                <Select.Option value="carbonate">Buffer de Carbonato (pKa = 10.33)</Select.Option>
                                <Select.Option value="custom">Personalizado...</Select.Option>
                            </Select>
                        </Form.Item>
                        
                        {selectedBufferSystem === 'custom' && (
                            <>
                                <Form.Item name={['buffer_acid', 'compound']} label="Ácido" rules={[{ required: true }]}>
                                    <Input placeholder="Ej: CH3COOH" />
                                </Form.Item>
                                <Form.Item name={['buffer_acid', 'concentration']} label="Concentración del Ácido (M)" rules={[{ required: true }]}>
                                    <Input type="number" step="0.001" min="0" max="10" placeholder="Ej: 0.1" />
                                </Form.Item>
                                <Form.Item name={['buffer_acid', 'pka']} label="pKa del Ácido" rules={[{ required: true }]}>
                                    <Input type="number" step="0.01" min="-2" max="16" placeholder="Ej: 4.76" />
                                </Form.Item>
                                <Form.Item name={['buffer_base', 'compound']} label="Base Conjugada" rules={[{ required: true }]}>
                                    <Input placeholder="Ej: CH3COO-" />
                                </Form.Item>
                                <Form.Item name={['buffer_base', 'concentration']} label="Concentración de la Base (M)" rules={[{ required: true }]}>
                                    <Input type="number" step="0.001" min="0" max="10" placeholder="Ej: 0.1" />
                                </Form.Item>
                            </>
                        )}
                        
                        {selectedBufferSystem && selectedBufferSystem !== 'custom' && (
                            <>
                                <Form.Item name="buffer_concentration" label="Concentración Total del Buffer (M)" initialValue={0.1}>
                                    <Input type="number" step="0.01" min="0.01" max="2" />
                                </Form.Item>
                                <Alert 
                                    message="Información del Buffer"
                                    description={getBufferSystemInfo(selectedBufferSystem)}
                                    type="info"
                                    showIcon
                                    className="mb-3"
                                />
                            </>
                        )}
                        
                        <Button onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}>
                            {showAdvancedOptions ? 'Ocultar' : 'Mostrar'} Opciones Avanzadas
                        </Button>
                    </>
                );
            case CalculationType.ActivityCorrection:
                return (
                    <>
                        <Form.Item name="input_type" label="Tipo de Valor" initialValue={InputType.PH}>
                            <Select>
                                <Select.Option value={InputType.PH}>pH</Select.Option>
                                <Select.Option value={InputType.POH}>pOH</Select.Option>
                                <Select.Option value={InputType.HConcentration}>[H+]</Select.Option>
                                <Select.Option value={InputType.OHConcentration}>[OH-]</Select.Option>
                            </Select>
                        </Form.Item>
                        <Form.Item name="input_value" label="Valor" rules={[{ required: true, message: 'Por favor ingrese un valor' }]}>
                            <Input type="number" />
                        </Form.Item>
                        <Form.Item name="ionic_strength" label="Fuerza Iónica (M)">
                            <Input type="number" />
                        </Form.Item>
                        <Form.Item name="include_activity" valuePropName="checked" initialValue={true}>
                            <Switch checkedChildren="Con Corrección" unCheckedChildren="Sin Corrección" />
                        </Form.Item>
                    </>
                );
            default:
                return null;
        }
    };

    // Alias para claridad
    const loading = isCalculating;
    const finalResult = calculationResult;

    const { token } = theme.useToken();

    // --- Envío del Formulario ---
    const onFinish = (values: any) => {
        // Transformar entrada para cálculos de buffer
        if (values.calculation_type === CalculationType.Buffer) {
            // Validación: debe haber un sistema buffer seleccionado
            if (!selectedBufferSystem) {
                message.error('Por favor seleccione un sistema buffer');
                return;
            }

            let buffer_components: any[] = [];

            if (selectedBufferSystem !== 'custom') {
                const total = parseFloat(values.buffer_concentration ?? 0.1);
                const half = isNaN(total) || total <= 0 ? 0.05 : total / 2;
                
                if (selectedBufferSystem === 'acetate') {
                    buffer_components = [
                        { compound: 'CH3COOH', concentration: half, pka: 4.76 },
                        { compound: 'CH3COO-', concentration: half }
                    ];
                } else if (selectedBufferSystem === 'phosphate') {
                    buffer_components = [
                        { compound: 'H2PO4-', concentration: half, pka: 7.21 },
                        { compound: 'HPO4^2-', concentration: half }
                    ];
                } else if (selectedBufferSystem === 'tris') {
                    buffer_components = [
                        { compound: '(HOCH2)3CNH3+', concentration: half, pka: 8.07 },
                        { compound: '(HOCH2)3CNH2', concentration: half }
                    ];
                } else if (selectedBufferSystem === 'carbonate') {
                    buffer_components = [
                        { compound: 'HCO3-', concentration: half, pka: 10.33 },
                        { compound: 'CO3^2-', concentration: half }
                    ];
                }
            } else if (selectedBufferSystem === 'custom') {
                // Para custom, validar que se han ingresado los datos
                if (!values.buffer_acid || !values.buffer_base) {
                    message.error('Por favor complete los datos del buffer personalizado');
                    return;
                }
                buffer_components = [
                    {
                        compound: values.buffer_acid.compound,
                        concentration: parseFloat(values.buffer_acid.concentration),
                        pka: parseFloat(values.buffer_acid.pka)
                    },
                    {
                        compound: values.buffer_base.compound,
                        concentration: parseFloat(values.buffer_base.concentration)
                    }
                ];
            }

            // Validación final: debe haber componentes
            if (buffer_components.length === 0) {
                message.error('Error al configurar los componentes del buffer');
                return;
            }

            values.buffer_components = buffer_components;
            values.input_type = InputType.PH;

            // Limpiar campos auxiliares del formulario
            delete values.buffer_concentration;
            delete values.buffer_acid;
            delete values.buffer_base;
        }

        dispatch(calculateAdvancedPH(values as CalculationInput));
    };

    // --- Renderizado de Errores ---
    const renderError = () => {
        if (!errors.calculation) return null;
        
        if (typeof errors.calculation === 'object' && errors.calculation !== null) {
            return Object.entries(errors.calculation).map(([field, messages]) => (
                <Alert
                    key={field}
                    message={`Error en el campo: ${field}`}
                    description={Array.isArray(messages) ? messages.join(', ') : String(messages)}
                    type="error"
                    showIcon
                    className="mb-2"
                />
            )).flat();
        }

        return <Alert message="Error de Cálculo" description={(errors.calculation as any).message || 'Ocurrió un error inesperado.'} type="error" showIcon />;
    };

    return (
        <div className={isDarkMode ? 'dark' : ''}>
            <div className="p-4 sm:p-6 md:p-8 bg-gray-50 dark:bg-gray-900 transition-colors duration-500">
                <Card
                    title={
                        <div className="flex items-center">
                            <BeakerIcon className="h-8 w-8 mr-3 text-blue-500" />
                            <Typography.Title level={3} style={{ margin: 0 }}>Calculadora Avanzada de pH/pOH</Typography.Title>
                        </div>
                    }
                    extra={
                        <Tooltip title={isDarkMode ? 'Modo Claro' : 'Modo Oscuro'}>
                            <Switch
                                checked={isDarkMode}
                                onChange={setIsDarkMode}
                                checkedChildren={<MoonIcon className="h-4 w-4 text-white" />}
                                unCheckedChildren={<SunIcon className="h-4 w-4 text-yellow-500" />}
                            />
                        </Tooltip>
                    }
                    style={{ backgroundColor: isDarkMode ? token.colorBgContainer : '#fff' }}
                >
                    <Form
                    form={form}
                    layout="vertical"
                    onFinish={onFinish}
                    initialValues={{
                    
                        calculation_type: CalculationType.ConcentrationToPH,
                        temperature: 25,
                    }}
                    onValuesChange={(changedValues) => {
                        if (changedValues.calculation_type) {
                            setCalculationMode(changedValues.calculation_type);
                        }
                    }}
                >
                        <Row gutter={24}>
                            {/* Columna de Entradas */}
                            <Col xs={24} lg={12}>
                                <motion.div initial="hidden" animate="visible" variants={cardVariants}>
                                    <Card title="Parámetros de Cálculo" className="mb-6 shadow-lg dark:bg-gray-800">
                                        <Form.Item name="calculation_type" label="Modo de Cálculo">
                        <Select>
                            <Select.Option value={CalculationType.ConcentrationToPH}>Concentración → pH</Select.Option>
                            <Select.Option value={CalculationType.PHToAll}>pH/pOH → Todos</Select.Option>
                            <Select.Option value={CalculationType.Buffer}>Solución Buffer</Select.Option>
                            <Select.Option value={CalculationType.ActivityCorrection}>Corrección por Actividad</Select.Option>
                        </Select>
                    </Form.Item>

                                        <Form.Item label="Presets de Soluciones Comunes">
                                            <Select placeholder="Cargar un ejemplo..." onChange={handlePresetChange}>
                                                {presets.map((p: any) => <Select.Option key={p.value} value={p.value}>{p.label}</Select.Option>)}
                                            </Select>
                                        </Form.Item>

                                        {renderDynamicFields()}
                                        
                                        {showAdvancedOptions && (
                                            <Form.Item
                                                name="temperature"
                                                label={
                                                    <Tooltip title="La temperatura afecta la constante de autoionización del agua (Kw).">
                                                        <span>Temperatura (°C) <InformationCircleIcon className="h-4 w-4 inline-block" /></span>
                                                    </Tooltip>
                                                }
                                                initialValue={25}
                                            >
                                                <Input type="number" />
                                            </Form.Item>
                                        )}

                                        <Form.Item>
                                            <Button type="primary" htmlType="submit" loading={loading} icon={<CalculatorIcon className="h-5 w-5 mr-2" />} block size="large">
                                                Calcular
                                            </Button>
                                        </Form.Item>
                                    </Card>
                                </motion.div>
                            </Col>

                            {/* Columna de Resultados */}
                            <Col xs={24} lg={12}>
                                <AnimatePresence>
                                    {loading && (
                                        <motion.div key="loader" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex justify-center items-center h-full">
                                            <Spin size="large" tip="Realizando cálculos químicos..." />
                                        </motion.div>
                                    )}
                                    {errors.calculation && (
                                        <motion.div key="error" initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                                            <Alert message="Error de Cálculo" description={errors.calculation} type="error" showIcon />
                                        </motion.div>
                                    )}
                                    {finalResult && !loading && (
                                        <motion.div key="results" initial="hidden" animate="visible" variants={cardVariants}>
                                            <Card title="Resultados del Cálculo" className="shadow-lg dark:bg-gray-800">
                                                <Row gutter={[16, 16]}>
                                                    <Col xs={12} sm={6}>
                                                        <motion.div variants={itemVariants}>
                                                            <Card size="small" className={`text-center ${finalResult.results.ph < 7 ? 'border-red-500' : 'border-blue-500'} dark:bg-gray-700`}>
                                                                <Typography.Text strong>pH</Typography.Text>
                                                                <Typography.Title level={4}>{finalResult.results.ph.toFixed(2)}</Typography.Title>
                                                            </Card>
                                                        </motion.div>
                                                    </Col>
                                                    <Col xs={12} sm={6}>
                                                        <motion.div variants={itemVariants}>
                                                            <Card size="small" className="text-center dark:bg-gray-700">
                                                                <Typography.Text strong>pOH</Typography.Text>
                                                                <Typography.Title level={4}>{finalResult.results.poh.toFixed(2)}</Typography.Title>
                                                            </Card>
                                                        </motion.div>
                                                    </Col>
                                                    <Col xs={12} sm={6}>
                                                        <motion.div variants={itemVariants}>
                                                            <Card size="small" className="text-center dark:bg-gray-700">
                                                                <Typography.Text strong>[H+]</Typography.Text>
                                                                <Typography.Title level={4}>{finalResult.results.h_concentration.toExponential(2)}</Typography.Title>
                                                            </Card>
                                                        </motion.div>
                                                    </Col>
                                                    <Col xs={12} sm={6}>
                                                        <motion.div variants={itemVariants}>
                                                            <Card size="small" className="text-center dark:bg-gray-700">
                                                                <Typography.Text strong>[OH-]</Typography.Text>
                                                                <Typography.Title level={4}>{finalResult.results.oh_concentration.toExponential(2)}</Typography.Title>
                                                            </Card>
                                                        </motion.div>
                                                    </Col>
                                                </Row>
                                                
                                                {finalResult.warnings && finalResult.warnings.length > 0 && (
                                                    <Alert message="Advertencias" description={finalResult.warnings.join(' ')} type="warning" className="mt-4" />
                                                )}

                                                <div className="mt-4">
                                                    <Button 
                                                        icon={<ArrowDownTrayIcon className="h-5 w-5 mr-2" />} 
                                                        className="mr-2"
                                                        onClick={() => {
                                                            if (finalResult && finalResult.results) {
                                                                exportPHResultsToPDF({
                                                                    ...finalResult.results,
                                                                    temperature: finalResult.temperature || 25,
                                                                    calculation_type: finalResult.calculation_type,
                                                                    warnings: finalResult.warnings,
                                                                    calculation_steps: finalResult.calculation_steps
                                                                });
                                                                message.success('PDF exportado exitosamente');
                                                            }
                                                        }}
                                                    >
                                                        Exportar PDF
                                                    </Button>
                                                    <Button 
                                                        icon={<ChartBarIcon className="h-5 w-5 mr-2" />}
                                                        onClick={() => {
                                                            if (onViewGraphs) {
                                                                onViewGraphs();
                                                            } else {
                                                                // Scroll a la sección de visualización si existe
                                                                if (visualizationRef.current) {
                                                                    visualizationRef.current.scrollIntoView({ behavior: 'smooth' });
                                                                } else {
                                                                    message.info('Los gráficos se muestran en la sección de Visualización de Resultados');
                                                                }
                                                            }
                                                        }}
                                                    >
                                                        Ver Gráficos
                                                    </Button>
                                                </div>

                                                <Collapse 
                                                    className="mt-4 dark:bg-gray-700" 
                                                    ghost
                                                    activeKey={showSteps ? ['1'] : []}
                                                    onChange={(keys) => setShowSteps(keys.includes('1'))}
                                                >
                                                    <Collapse.Panel 
                                                        header={
                                                            <span className="font-semibold">
                                                                Ver Proceso Paso a Paso 
                                                                {finalResult.calculation_steps && `(${finalResult.calculation_steps.length} pasos)`}
                                                            </span>
                                                        } 
                                                        key="1"
                                                    >
                                                        {finalResult.calculation_steps && finalResult.calculation_steps.length > 0 ? (
                                                            <div className="space-y-3">
                                                                {finalResult.calculation_steps.map((step: string, index: number) => (
                                                                    <motion.div 
                                                                        key={index} 
                                                                        initial={{ opacity: 0, x: -20 }}
                                                                        animate={{ opacity: 1, x: 0 }}
                                                                        transition={{ delay: index * 0.1 }}
                                                                        className="p-3 border-l-4 border-blue-500 bg-blue-50 dark:bg-gray-800 rounded"
                                                                    >
                                                                        <Typography.Text strong className="text-blue-700 dark:text-blue-400">
                                                                            Paso {index + 1}
                                                                        </Typography.Text>
                                                                        <p className="mt-1 text-gray-700 dark:text-gray-300">{step}</p>
                                                                    </motion.div>
                                                                ))}
                                                            </div>
                                                        ) : (
                                                            <Typography.Text type="secondary">
                                                                No hay pasos detallados disponibles para este cálculo.
                                                            </Typography.Text>
                                                        )}
                                                    </Collapse.Panel>
                                                </Collapse>
                                            </Card>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </Col>
                        </Row>
                    </Form>
                </Card>
            </div>
        </div>
    );
};

export default AdvancedPHCalculator;