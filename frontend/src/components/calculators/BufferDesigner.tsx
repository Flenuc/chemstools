import React, { useState, useEffect, useMemo } from 'react';
import { Card, Form, Select, InputNumber, Slider, Button, Typography, Row, Col, Statistic, Tooltip as AntTooltip } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { BeakerIcon, CheckCircleIcon, InformationCircleIcon } from '@heroicons/react/24/outline';
import { BufferSystem, BufferConstraints } from '../../types/advancedPH';

// --- Props del Componente ---
interface BufferDesignerProps {
    targetPH?: number;
    onBufferDesigned: (buffer: BufferSystem) => void;
    constraints?: BufferConstraints;
}

// --- Mock Data / Templates ---
const bufferTemplates: Omit<BufferSystem, 'finalPH' | 'bufferCapacity'>[] = [
    {
        id: 'acetate',
        pairName: 'Buffer de Acetato',
        acid: { formula: 'CH₃COOH', concentration: 0.1, pKa: 4.76 },
        base: { formula: 'CH₃COO⁻', concentration: 0.1 },
        effectiveRange: [3.76, 5.76],
    },
    {
        id: 'phosphate',
        pairName: 'Buffer de Fosfato',
        acid: { formula: 'H₂PO₄⁻', concentration: 0.1, pKa: 7.21 },
        base: { formula: 'HPO₄²⁻', concentration: 0.1 },
        effectiveRange: [6.21, 8.21],
    },
    {
        id: 'tris',
        pairName: 'Buffer TRIS',
        acid: { formula: '(HOCH₂)₃CNH₃⁺', concentration: 0.05, pKa: 8.07 },
        base: { formula: '(HOCH₂)₃CNH₂', concentration: 0.05 },
        effectiveRange: [7.07, 9.07],
    },
];

const { Title, Text } = Typography;

const BufferDesigner: React.FC<BufferDesignerProps> = ({ targetPH = 7.0, onBufferDesigned, constraints }) => {
    const [form] = Form.useForm();
    const [selectedTemplate, setSelectedTemplate] = useState<Omit<BufferSystem, 'finalPH' | 'bufferCapacity'>>(bufferTemplates[0]);
    const [ratio, setRatio] = useState(1); // Ratio [Base]/[Ácido]
    const [totalConcentration, setTotalConcentration] = useState(0.2);

    // Calcula el pH y otras propiedades basadas en el estado
    const designedBuffer = useMemo((): BufferSystem => {
        const acidConc = totalConcentration / (1 + ratio);
        const baseConc = totalConcentration - acidConc;
        const finalPH = selectedTemplate.acid.pKa + Math.log10(ratio);

        return {
            ...selectedTemplate,
            acid: { ...selectedTemplate.acid, concentration: acidConc },
            base: { ...selectedTemplate.base, concentration: baseConc },
            finalPH: finalPH,
            bufferCapacity: 2.303 * ((acidConc * baseConc) / (acidConc + baseConc)),
        };
    }, [selectedTemplate, ratio, totalConcentration]);
    
    // Genera datos para el gráfico de titulación simulada
    const titrationData = useMemo(() => {
        const data = [];
        const pKa = selectedTemplate.acid.pKa;
        for (let ph = pKa - 3; ph <= pKa + 3; ph += 0.1) {
            const ratio = Math.pow(10, ph - pKa);
            const alpha_base = ratio / (1 + ratio); // Fracción de la forma básica
            data.push({ ph: ph.toFixed(2), alpha_base });
        }
        return data;
    }, [selectedTemplate.acid.pKa]);


    useEffect(() => {
        // Si el targetPH cambia, ajusta el ratio inicial
        const initialRatio = Math.pow(10, targetPH - selectedTemplate.acid.pKa);
        setRatio(initialRatio);
        form.setFieldsValue({ ratio: initialRatio });
    }, [targetPH, selectedTemplate, form]);

    const handleTemplateChange = (id: string) => {
        const template = bufferTemplates.find(t => t.id === id);
        if (template) {
            setSelectedTemplate(template);
            // Recalcula el ratio para el nuevo pKa
            const newRatio = Math.pow(10, targetPH - template.acid.pKa);
            setRatio(newRatio);
            form.setFieldsValue({ ratio: newRatio });
        }
    };

    const handleFinish = () => {
        onBufferDesigned(designedBuffer);
    };

    return (
        <Card>
            <Title level={4}><BeakerIcon className="h-6 w-6 inline-block mr-2" /> Diseñador de Buffer</Title>
            <Form form={form} layout="vertical" onFinish={handleFinish} initialValues={{ ratio, totalConcentration, templateId: selectedTemplate.id }}>
                <Row gutter={24}>
                    <Col xs={24} md={8}>
                        <Form.Item name="templateId" label="Sistema Buffer">
                            <Select onChange={handleTemplateChange}>
                                {bufferTemplates.map(t => <Select.Option key={t.id} value={t.id}>{t.pairName}</Select.Option>)}
                            </Select>
                        </Form.Item>
                        <Form.Item label={<span>Ratio [Base]/[Ácido] <AntTooltip title="Ajusta la proporción para alcanzar el pH deseado."><InformationCircleIcon className="h-4 w-4 inline-block" /></AntTooltip></span>}>
                            <Slider min={0.1} max={10} step={0.01} value={ratio} onChange={setRatio} />
                        </Form.Item>
                        <Form.Item name="totalConcentration" label="Concentración Total (M)">
                            <InputNumber min={0.01} max={2} step={0.01} className="w-full" onChange={(val) => setTotalConcentration(val || 0.01)} />
                        </Form.Item>
                        
                        <Title level={5}>Resultados del Diseño</Title>
                        <Row gutter={16}>
                            <Col span={12}><Statistic title="pH Final" value={designedBuffer.finalPH} precision={2} /></Col>
                            <Col span={12}><Statistic title="Capacidad (β)" value={designedBuffer.bufferCapacity} precision={3} /></Col>
                        </Row>
                        <Text type="secondary">Rango efectivo: {designedBuffer.effectiveRange[0]} - {designedBuffer.effectiveRange[1]}</Text>
                        
                        <Form.Item className="mt-4">
                            <Button type="primary" htmlType="submit" icon={<CheckCircleIcon className="h-5 w-5 mr-2" />}>
                                Confirmar y Usar Buffer
                            </Button>
                        </Form.Item>
                    </Col>
                    <Col xs={24} md={16}>
                        <Title level={5}>Simulación de Curva de Titulación</Title>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={titrationData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="ph" name="pH" />
                                <YAxis dataKey="alpha_base" name="Fracción Base" domain={[0, 1]} />
                                <Tooltip />
                                <Legend />
                                <Line type="monotone" dataKey="alpha_base" name="Fracción [Base]" stroke="#8884d8" dot={false} />
                                <ReferenceLine x={selectedTemplate.acid.pKa} stroke="red" label={`pKa = ${selectedTemplate.acid.pKa}`} />
                                <ReferenceLine x={designedBuffer.finalPH} stroke="green" label={{ value: `pH Objetivo = ${designedBuffer.finalPH.toFixed(2)}`, position: 'insideTop' }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </Col>
                </Row>
            </Form>
        </Card>
    );
};

export default BufferDesigner;