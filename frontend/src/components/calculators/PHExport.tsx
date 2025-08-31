import React, { useState, useEffect, useMemo } from 'react';
import { Modal, Form, Select, Checkbox, Button, Progress, notification, Alert, Table, Typography, message, Row, Col } from 'antd';
import { ArrowDownTrayIcon, CogIcon, DocumentArrowDownIcon } from '@heroicons/react/24/outline';
import { PHHistoryItem } from './PHHistory';
import phCalculatorService from '../../services/phCalculatorService';
import { ExportFormat } from '../../types/advancedPH';

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
    format: ExportFormat;
    fields: string[];
    includeSteps: boolean;
    includeWarnings: boolean;
    dateRange?: [string, string];
}

const defaultFields = ['calculationType', 'inputSummary', 'results', 'timestamp', 'calculationTimeMs', 'warnings'];

const fieldLabels: Record<string, string> = {
    calculationType: 'Tipo de Cálculo',
    inputSummary: 'Entrada',
    results: 'Resultados',
    timestamp: 'Fecha y Hora',
    calculationTimeMs: 'Tiempo (ms)',
    warnings: 'Advertencias',
    calculation_steps: 'Pasos del Cálculo',
    temperature: 'Temperatura',
    ionic_strength: 'Fuerza Iónica'
};

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
                format: ExportFormat.CSV,
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
        if (calculationIds.length === 0) {
            message.warning('Por favor selecciona al menos un cálculo para exportar');
            return;
        }

        setIsExporting(true);
        setProgress(10);

        try {
            // Construir el request para el backend
            const exportRequest = {
                calculationIds,
                format: options.format,
                includeSteps: options.includeSteps,
                fields: options.fields,
                includeWarnings: options.includeWarnings
            };

            setProgress(30);

            // Llamar al servicio de exportación
            const response = await phCalculatorService.exportCalculations(exportRequest);
            
            setProgress(70);

            if (response.success && response.data) {
                // Si el backend devuelve una URL de descarga
                const downloadUrl = response.data.download_url;
                
                // Usar la URL tal como viene del backend
                // Next.js se encargará del proxy a través de los rewrites
                // Si la URL ya es absoluta, usarla tal cual
                // Si es relativa (empieza con /media/), también funcionará gracias al proxy
                const fullDownloadUrl = downloadUrl;
                
                // Iniciar la descarga
                const link = document.createElement('a');
                link.href = fullDownloadUrl;
                link.download = `ph_calculations_${Date.now()}.${options.format}`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                setProgress(100);
                
                notification.success({
                    message: 'Exportación Completada',
                    description: `Se exportaron ${calculationIds.length} cálculos en formato ${options.format.toUpperCase()}.`,
                    duration: 4,
                });
                
                onExportComplete({ 
                    format: options.format, 
                    url: downloadUrl 
                });
                
                // Cerrar el modal después de un breve delay
                setTimeout(() => {
                    onClose();
                    setProgress(0);
                }, 500);
            } else {
                throw new Error(response.error || 'Error desconocido en la exportación');
            }
        } catch (error: any) {
            console.error('Error durante la exportación:', error);
            
            notification.error({
                message: 'Error en la Exportación',
                description: error.message || 'No se pudo generar el archivo. Por favor, inténtalo de nuevo.',
                duration: 5,
            });
            
            onExportComplete({ 
                format: options.format, 
                error: error.message || 'Error en la generación del archivo' 
            });
            
            setProgress(0);
        } finally {
            setIsExporting(false);
        }
    };

    const previewColumns = form.getFieldValue('fields')?.map((field: string) => ({
        title: fieldLabels[field] || field.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()),
        dataIndex: field,
        key: field,
        ellipsis: true,
        width: field === 'inputSummary' || field === 'results' ? 200 : undefined,
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
                <Form.Item 
                    name="format" 
                    label="Formato de Archivo" 
                    rules={[{ required: true, message: 'Por favor selecciona un formato' }]}
                    tooltip="Selecciona el formato en el que deseas exportar los datos"
                >
                    <Select>
                        <Select.Option value={ExportFormat.CSV}>
                            <DocumentArrowDownIcon className="h-4 w-4 inline mr-2" />
                            CSV (Valores Separados por Comas)
                        </Select.Option>
                        <Select.Option value={ExportFormat.JSON}>
                            <DocumentArrowDownIcon className="h-4 w-4 inline mr-2" />
                            JSON (JavaScript Object Notation)
                        </Select.Option>
                        <Select.Option value={ExportFormat.PDF}>
                            <DocumentArrowDownIcon className="h-4 w-4 inline mr-2" />
                            PDF (Documento Portable)
                        </Select.Option>
                        <Select.Option value={ExportFormat.Excel}>
                            <DocumentArrowDownIcon className="h-4 w-4 inline mr-2" />
                            Excel (XLSX)
                        </Select.Option>
                    </Select>
                </Form.Item>

                <Form.Item 
                    name="fields" 
                    label="Campos a Incluir"
                    tooltip="Selecciona qué información incluir en el archivo exportado"
                >
                    <Checkbox.Group 
                        options={defaultFields.map(f => ({ 
                            label: fieldLabels[f] || f, 
                            value: f 
                        }))} 
                    />
                </Form.Item>

                <Row gutter={16}>
                    <Col span={12}>
                        <Form.Item 
                            name="includeSteps" 
                            valuePropName="checked"
                            initialValue={true}
                        >
                            <Checkbox>
                                Incluir pasos detallados del cálculo
                            </Checkbox>
                        </Form.Item>
                    </Col>
                    <Col span={12}>
                        <Form.Item 
                            name="includeWarnings" 
                            valuePropName="checked"
                            initialValue={true}
                        >
                            <Checkbox>
                                Incluir advertencias y observaciones
                            </Checkbox>
                        </Form.Item>
                    </Col>
                </Row>

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
                    <div className="mt-4 mb-4">
                        <Progress 
                            percent={progress} 
                            status={progress === 100 ? 'success' : 'active'}
                            strokeColor={{
                                '0%': '#108ee9',
                                '100%': '#87d068',
                            }}
                        />
                        <p className="text-center text-gray-600 mt-2">
                            {progress < 30 ? 'Preparando datos...' : 
                             progress < 70 ? 'Generando archivo...' : 
                             progress < 100 ? 'Finalizando...' : '¡Listo!'}
                        </p>
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