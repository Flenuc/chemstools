import React, { useState, useEffect } from 'react';
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
    AutoComplete,
    Spin,
    Alert,
    theme,
} from 'antd';
import { motion, AnimatePresence } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';
import { BeakerIcon, CalculatorIcon, ChartBarIcon, ArrowDownTrayIcon, InformationCircleIcon, SunIcon, MoonIcon } from '@heroicons/react/24/outline';

// --- Tipos de Datos ---
interface CalculationStep {
    title: string;
    explanation: string;
    formula: string;
}

export interface CalculationInput {
    mode: 'ph_to_all' | 'concentration_to_ph' | 'buffer' | 'activity_correction';
    inputType: 'pH' | 'pOH' | '[H+]' | '[OH-]';
    inputValue: number;
    solute: string;
    concentration: number;
    temperature: number;
    ionicStrength?: number;
    buffer: {
        acidName: string;
        acidConcentration: number;
        baseName: string;
        baseConcentration: number;
    };
}

interface CalculationResult {
    ph: number;
    poh: number;
    h_concentration: number;
    oh_concentration: number;
    is_acid: boolean;
    steps: CalculationStep[];
    warnings: string[];
}

// Mock de integración con Redux - Reemplazar con el store real
const useAppDispatch = () => (action: any) => console.log('Dispatching action:', action);
const useAppSelector = (selector: any): {
    history: any[];
    presets: { label: string; value: string }[];
    theme: 'light' | 'dark';
    loading: boolean;
    error: string | null;
    result: CalculationResult | null;
} => {
    // Simula el estado del store
    return {
        history: [],
        presets: [
            { label: 'Ácido Clorhídrico (HCl) 0.1M', value: 'hcl_0.1' },
            { label: 'Hidróxido de Sodio (NaOH) 0.1M', value: 'naoh_0.1' },
            { label: 'Buffer Acetato 0.1M/0.1M', value: 'acetate_buffer_0.1' },
        ],
        theme: 'light',
        loading: false,
        error: null,
        result: null, // Inicialmente nulo, pero con tipo definido
    };
};


interface AdvancedPHCalculatorProps {
    onCalculationComplete?: (result: CalculationResult) => void;
    defaultValues?: Partial<CalculationInput>;
    showAdvancedOptions?: boolean;
}

// --- Componente Principal ---
const AdvancedPHCalculator: React.FC<AdvancedPHCalculatorProps> = ({
    onCalculationComplete,
    defaultValues,
    showAdvancedOptions = true,
}) => {
    const [form] = Form.useForm();
    const dispatch = useAppDispatch();
    const { result, loading, error, presets, theme: currentTheme } = useAppSelector((state: any) => state.calculators);
    
    const [calculationMode, setCalculationMode] = useState<CalculationInput['mode']>('concentration_to_ph');
    const [isDarkMode, setIsDarkMode] = useState(currentTheme === 'dark');
    const [chemicalOptions, setChemicalOptions] = useState<{ value: string }[]>([]);
    
    // Simulación de resultado para desarrollo
    const [mockResult, setMockResult] = useState<CalculationResult | null>(null);


    const { token } = theme.useToken();

    useEffect(() => {
        if (defaultValues) {
            form.setFieldsValue(defaultValues);
            if (defaultValues.mode) {
                setCalculationMode(defaultValues.mode);
            }
        }
    }, [defaultValues, form]);

    // --- Lógica de Auto-completado ---
    const handleChemicalSearch = (searchText: string) => {
        // Simulación de búsqueda en backend
        const mockChemicals = ['HCl', 'H2SO4', 'HNO3', 'NaOH', 'KOH', 'NH3', 'CH3COOH', 'C6H5COOH'];
        if (!searchText) {
            setChemicalOptions([]);
        } else {
            setChemicalOptions(
                mockChemicals
                    .filter(chem => chem.toLowerCase().includes(searchText.toLowerCase()))
                    .map(chem => ({ value: chem }))
            );
        }
    };

    // --- Manejo de Presets ---
    const handlePresetChange = (value: string) => {
        switch (value) {
            case 'hcl_0.1':
                form.setFieldsValue({
                    mode: 'concentration_to_ph',
                    solute: 'HCl',
                    concentration: 0.1,
                });
                setCalculationMode('concentration_to_ph');
                break;
            case 'naoh_0.1':
                form.setFieldsValue({
                    mode: 'concentration_to_ph',
                    solute: 'NaOH',
                    concentration: 0.1,
                });
                setCalculationMode('concentration_to_ph');
                break;
            case 'acetate_buffer_0.1':
                form.setFieldsValue({
                    mode: 'buffer',
                    buffer: {
                        acidName: 'CH3COOH',
                        acidConcentration: 0.1,
                        baseName: 'CH3COONa',
                        baseConcentration: 0.1,
                    },
                });
                setCalculationMode('buffer');
                break;
        }
    };

    // --- Envío del Formulario ---
    const onFinish = (values: any) => {
        console.log('Calculating with values:', values);
        // Aquí se haría el dispatch a un thunk de Redux para llamar al backend
        // dispatch(calculateAdvancedPh(values));
        // Simulación de respuesta
        const simulatedResult: CalculationResult = {
            ph: 1.0,
            poh: 13.0,
            h_concentration: 0.1,
            oh_concentration: 1e-13,
            is_acid: true,
            steps: [
                { title: 'Paso 1: Identificar el soluto', explanation: 'HCl es un ácido fuerte.', formula: 'HCl -> H+ + Cl-' },
                { title: 'Paso 2: Calcular [H+]', explanation: 'Al ser fuerte, se disocia completamente.', formula: '[H+] = [HCl] = 0.1 M' },
                { title: 'Paso 3: Calcular pH', explanation: 'El pH es el logaritmo negativo de la concentración de H+.', formula: 'pH = -log(0.1) = 1.0' },
            ],
            warnings: ['La concentración es alta, la actividad puede diferir.'],
        };
        
        setMockResult(simulatedResult); // Usamos estado local para la simulación

        if (onCalculationComplete) {
            onCalculationComplete(simulatedResult);
        }
    };

    // --- Renderizado de Campos Dinámicos ---
    const renderDynamicFields = () => {
        switch (calculationMode) {
            case 'ph_to_all':
                return (
                    <Row gutter={16}>
                        <Col xs={24} md={12}>
                            <Form.Item name="inputType" label="Tipo de Entrada" initialValue="pH">
                                <Select>
                                    <Select.Option value="pH">pH</Select.Option>
                                    <Select.Option value="pOH">pOH</Select.Option>
                                    <Select.Option value="[H+]">[H+]</Select.Option>
                                    <Select.Option value="[OH-]">[OH-]</Select.Option>
                                </Select>
                            </Form.Item>
                        </Col>
                        <Col xs={24} md={12}>
                            <Form.Item
                                name="inputValue"
                                label="Valor de Entrada"
                                rules={[{ required: true, message: 'Por favor, ingrese un valor' }]}
                            >
                                <Input type="number" step="0.01" />
                            </Form.Item>
                        </Col>
                    </Row>
                );
            case 'buffer':
                return (
                    <>
                        <Typography.Title level={5}>Componente Ácido</Typography.Title>
                        <Row gutter={16}>
                            <Col xs={24} md={12}>
                                <Form.Item name={['buffer', 'acidName']} label="Fórmula" rules={[{ required: true, message: 'Requerido' }]}>
                                    <AutoComplete options={chemicalOptions} onSearch={handleChemicalSearch} placeholder="Ej: CH3COOH" />
                                </Form.Item>
                            </Col>
                            <Col xs={24} md={12}>
                                <Form.Item name={['buffer', 'acidConcentration']} label="Concentración (M)" rules={[{ required: true, message: 'Requerido' }]}>
                                    <Input type="number" step="0.001" />
                                </Form.Item>
                            </Col>
                        </Row>
                        <Typography.Title level={5}>Componente Básico</Typography.Title>
                        <Row gutter={16}>
                            <Col xs={24} md={12}>
                                <Form.Item name={['buffer', 'baseName']} label="Fórmula" rules={[{ required: true, message: 'Requerido' }]}>
                                    <AutoComplete options={chemicalOptions} onSearch={handleChemicalSearch} placeholder="Ej: CH3COONa" />
                                </Form.Item>
                            </Col>
                            <Col xs={24} md={12}>
                                <Form.Item name={['buffer', 'baseConcentration']} label="Concentración (M)" rules={[{ required: true, message: 'Requerido' }]}>
                                    <Input type="number" step="0.001" />
                                </Form.Item>
                            </Col>
                        </Row>
                    </>
                );
            case 'activity_correction':
            case 'concentration_to_ph':
            default:
                return (
                    <Row gutter={16}>
                        <Col xs={24} md={12}>
                            <Form.Item
                                name="solute"
                                label="Soluto"
                                rules={[{ required: true, message: 'Por favor ingrese el soluto' }]}
                            >
                                <AutoComplete
                                    options={chemicalOptions}
                                    onSearch={handleChemicalSearch}
                                    placeholder="Ej: HCl, NaOH"
                                />
                            </Form.Item>
                        </Col>
                        <Col xs={24} md={12}>
                            <Form.Item
                                name="concentration"
                                label="Concentración (M)"
                                rules={[{ required: true, message: 'Por favor ingrese la concentración' }]}
                            >
                                <Input type="number" step="0.001" placeholder="Ej: 0.1" />
                            </Form.Item>
                        </Col>
                        {calculationMode === 'activity_correction' && (
                             <Col xs={24} md={12}>
                                <Form.Item
                                    name="ionicStrength"
                                    label={
                                        <Tooltip title="La fuerza iónica afecta la actividad de los iones.">
                                            <span>Fuerza Iónica (M) <InformationCircleIcon className="h-4 w-4 inline-block" /></span>
                                        </Tooltip>
                                    }
                                    rules={[{ required: true, message: 'Requerido para corrección' }]}
                                >
                                    <Input type="number" step="0.01" placeholder="Ej: 0.05" />
                                </Form.Item>
                            </Col>
                        )}
                    </Row>
                );
        }
    };

    const cardVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0, transition: { staggerChildren: 0.1 } },
    };

    const itemVariants = {
        hidden: { opacity: 0, scale: 0.95 },
        visible: { opacity: 1, scale: 1 },
    };
    
    const finalResult = result || mockResult; // Usar resultado de Redux o el mock local

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
                        onValuesChange={(changedValues) => {
                            if (changedValues.mode) {
                                setCalculationMode(changedValues.mode);
                            }
                        }}
                    >
                        <Row gutter={24}>
                            {/* Columna de Entradas */}
                            <Col xs={24} lg={12}>
                                <motion.div initial="hidden" animate="visible" variants={cardVariants}>
                                    <Card title="Parámetros de Cálculo" className="mb-6 shadow-lg dark:bg-gray-800">
                                        <Form.Item name="mode" label="Modo de Cálculo" initialValue="concentration_to_ph">
                                            <Select>
                                                <Select.Option value="concentration_to_ph">Concentración → pH</Select.Option>
                                                <Select.Option value="ph_to_all">pH/pOH → Todos</Select.Option>
                                                <Select.Option value="buffer">Solución Buffer</Select.Option>
                                                {showAdvancedOptions && <Select.Option value="activity_correction">Corrección por Actividad</Select.Option>}
                                            </Select>
                                        </Form.Item>

                                        <Form.Item label="Presets de Soluciones Comunes">
                                            <Select placeholder="Cargar un ejemplo..." onChange={handlePresetChange}>
                                                {presets.map((p) => <Select.Option key={p.value} value={p.value}>{p.label}</Select.Option>)}
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
                                    {error && (
                                        <motion.div key="error" initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                                            <Alert message="Error de Cálculo" description={error} type="error" showIcon />
                                        </motion.div>
                                    )}
                                    {finalResult && !loading && (
                                        <motion.div key="results" initial="hidden" animate="visible" variants={cardVariants}>
                                            <Card title="Resultados del Cálculo" className="shadow-lg dark:bg-gray-800">
                                                <Row gutter={[16, 16]}>
                                                    <Col xs={12} sm={6}>
                                                        <motion.div variants={itemVariants}>
                                                            <Card size="small" className={`text-center ${finalResult.is_acid ? 'border-red-500' : 'border-blue-500'} dark:bg-gray-700`}>
                                                                <Typography.Text strong>pH</Typography.Text>
                                                                <Typography.Title level={4}>{finalResult.ph.toFixed(2)}</Typography.Title>
                                                            </Card>
                                                        </motion.div>
                                                    </Col>
                                                    <Col xs={12} sm={6}>
                                                        <motion.div variants={itemVariants}>
                                                            <Card size="small" className="text-center dark:bg-gray-700">
                                                                <Typography.Text strong>pOH</Typography.Text>
                                                                <Typography.Title level={4}>{finalResult.poh.toFixed(2)}</Typography.Title>
                                                            </Card>
                                                        </motion.div>
                                                    </Col>
                                                    <Col xs={12} sm={6}>
                                                         <motion.div variants={itemVariants}>
                                                            <Card size="small" className="text-center dark:bg-gray-700">
                                                                <Typography.Text strong>[H+]</Typography.Text>
                                                                <Typography.Title level={4}>{finalResult.h_concentration.toExponential(2)}</Typography.Title>
                                                            </Card>
                                                        </motion.div>
                                                    </Col>
                                                    <Col xs={12} sm={6}>
                                                         <motion.div variants={itemVariants}>
                                                            <Card size="small" className="text-center dark:bg-gray-700">
                                                                <Typography.Text strong>[OH-]</Typography.Text>
                                                                <Typography.Title level={4}>{finalResult.oh_concentration.toExponential(2)}</Typography.Title>
                                                            </Card>
                                                        </motion.div>
                                                    </Col>
                                                </Row>
                                                
                                                {finalResult.warnings && finalResult.warnings.length > 0 && (
                                                    <Alert message="Advertencias" description={finalResult.warnings.join(' ')} type="warning" className="mt-4" />
                                                )}

                                                <div className="mt-4">
                                                    <Button icon={<ArrowDownTrayIcon className="h-5 w-5 mr-2" />} className="mr-2">Exportar PDF</Button>
                                                    <Button icon={<ChartBarIcon className="h-5 w-5 mr-2" />}>Ver Gráficos</Button>
                                                </div>

                                                <Collapse className="mt-4 dark:bg-gray-700" ghost>
                                                    <Collapse.Panel header="Ver Proceso Paso a Paso" key="1">
                                                        {finalResult.steps.map((step: CalculationStep, index: number) => (
                                                            <div key={index} className="mb-2 p-2 border-l-4 border-blue-500">
                                                                <Typography.Text strong>{step.title}</Typography.Text>
                                                                <p>{step.explanation}</p>
                                                                <Typography.Text code>{step.formula}</Typography.Text>
                                                            </div>
                                                        ))}
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
