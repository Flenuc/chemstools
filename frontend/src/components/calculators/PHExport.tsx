import React, { useState, useEffect, useMemo } from 'react';
import { Modal, Form, Select, Checkbox, Button, Progress, notification, Alert, Table, Typography } from 'antd';
import { ArrowDownTrayIcon, CogIcon } from '@heroicons/react/24/outline';
// Suponiendo que PHHistoryItem se exporta desde PHHistory o un archivo de tipos
import { PHHistoryItem } from './PHHistory';

// --- Tipos de Datos ---
interface PHExportProps {
    calculationIds: string[];
    visible: boolean;
    onClose: () => void;
    onExportComplete: (result: { format: string; url?: string; error?: string }) => void;
    maxExportSize?: number;
    // Pasamos los datos completos para la vista previa y la exportación
    allHistoryData: PHHistoryItem[]; 
}

interface ExportOptions {
    format: 'csv' | 'pdf' | 'json' | 'excel';
    fields: string[];
    includeSteps: boolean;
    includeWarnings: boolean;
}

const defaultFields = ['calculationType', 'inputSummary', 'ph', 'timestamp', 'calculationTimeMs', 'hasWarnings'];

const PHExport: React.FC<PHExportProps> = ({
    calculationIds,
    visible,
    onClose,
    onExportComplete,
    maxExportSize = 50,
    allHistoryData,
}) => {
    const [form] = Form.useForm<ExportOptions>();
    const [isExporting, setIsExporting] = useState(false);
    const [progress, setProgress] = useState(0);
    const [previewData, setPreviewData] = useState<any[]>([]);

    const exportLimitExceeded = calculationIds.length > maxExportSize;

    const calculationsToExport = useMemo(() => {
        return allHistoryData.filter(item => calculationIds.includes(item.key));
    }, [calculationIds, allHistoryData]);

    useEffect(() => {
        // Inicializa el formulario y la vista previa cuando el modal se hace visible
        if (visible) {
            form.setFieldsValue({
                format: 'csv',
                fields: defaultFields,
                includeSteps: true,
                includeWarnings: true,
            });
            updatePreview(form.getFieldsValue());
        }
    }, [visible, form]);
    
    const updatePreview = (options: Partial<ExportOptions>) => {
        const { fields = defaultFields } = options;
        const preview = calculationsToExport.slice(0, 5).map(PHHistoryItem => {
            const row: { [key: string]: any } = { key: PHHistoryItem.key };
            fields.forEach(field => {
                row[field] = PHHistoryItem;
            });
            return row;
        });
        setPreviewData(preview);
    };

    const handleExport = async (options: ExportOptions) => {
        setIsExporting(true);
        setProgress(0);

        // Simulación de generación de archivo
        for (let i = 0; i <= 100; i += 10) {
            await new Promise(res => setTimeout(res, 150));
            setProgress(i);
        }

        setIsExporting(false);
        onClose();

        // Simulación de resultado
        const success = Math.random() > 0.1; // 90% de éxito
        if (success) {
            notification.success({
                message: 'Exportación Completada',
                description: `Tu archivo ${options.format.toUpperCase()} ha sido generado y la descarga comenzará en breve.`,
            });
            onExportComplete({ format: options.format, url: 'blob:http://localhost/mock-file-url' });
        } else {
            notification.error({
                message: 'Error en la Exportación',
                description: 'No se pudo generar el archivo. Por favor, inténtalo de nuevo.',
            });
            onExportComplete({ format: options.format, error: 'Generation failed' });
        }
    };

    const previewColumns = form.getFieldValue('fields')?.map((field: string) => ({
        title: field.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()), // Formatear nombre de columna
        dataIndex: field,
        key: field,
    })) || [];

    return (
        <Modal
            title={
                <div className="flex items-center">
                    <CogIcon className="h-6 w-6 mr-2" />
                    Opciones de Exportación
                </div>
            }
            open={visible}
            onCancel={onClose}
            footer={null}
            width={700}
        >
            {exportLimitExceeded && (
                <Alert
                    message="Límite de Exportación Excedido"
                    description={`Has seleccionado ${calculationIds.length} cálculos, pero tu plan actual permite un máximo de ${maxExportSize}.`}
                    type="warning"
                    showIcon
                    action={<Button size="small" type="primary">Mejorar Plan</Button>}
                    className="mb-4"
                />
            )}

            <Form
                form={form}
                layout="vertical"
                onFinish={handleExport}
                onValuesChange={(_, allValues) => updatePreview(allValues)}
            >
                <Form.Item name="format" label="Formato de Archivo" rules={[{ required: true }]}>
                    <Select>
                        <Select.Option value="csv">CSV (Valores Separados por Comas)</Select.Option>
                        <Select.Option value="json">JSON (JavaScript Object Notation)</Select.Option>
                        <Select.Option value="pdf">PDF (Documento Portable)</Select.Option>
                        <Select.Option value="excel">Excel (XLSX)</Select.Option>
                    </Select>
                </Form.Item>

                <Form.Item name="fields" label="Campos a Incluir">
                    <Checkbox.Group options={defaultFields.map(f => ({ label: f, value: f }))} />
                </Form.Item>

                <Form.Item>
                    <Checkbox.Group>
                        <Checkbox value="includeSteps" defaultChecked>Incluir pasos del cálculo</Checkbox>
                        <Checkbox value="includeWarnings" defaultChecked>Incluir advertencias</Checkbox>
                    </Checkbox.Group>
                </Form.Item>

                <div>
                    <Typography.Title level={5}>Vista Previa (primeros 5 registros)</Typography.Title>
                    <Table
                        columns={previewColumns}
                        dataSource={previewData}
                        pagination={false}
                        size="small"
                    />
                </div>

                {isExporting && (
                    <div className="mt-4">
                        <Progress percent={progress} />
                        <p className="text-center">Generando archivo, por favor espera...</p>
                    </div>
                )}

                <Form.Item className="mt-6 text-right">
                    <Button onClick={onClose} className="mr-2">Cancelar</Button>
                    <Button
                        type="primary"
                        htmlType="submit"
                        loading={isExporting}
                        disabled={exportLimitExceeded}
                        icon={<ArrowDownTrayIcon className="h-5 w-5 mr-2" />}
                    >
                        Exportar {calculationIds.length} Registros
                    </Button>
                </Form.Item>
            </Form>
        </Modal>
    );
};

export default PHExport;