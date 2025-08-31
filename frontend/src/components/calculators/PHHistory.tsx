import React, { useState, useMemo, useEffect } from 'react';
import { Table, Input, Button, Modal, Tag, Space, Typography, Card, Statistic, Row, Col, DatePicker, Select, Tooltip, Spin, Alert } from 'antd';
import { EyeIcon, TrashIcon, DocumentDuplicateIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import type { ColumnsType } from 'antd/es/table';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { fetchPHHistory, deleteCalculation } from '../../store/advancedPHSlice';
import { ExportFormat, HistoryFilters, CalculationType } from '../../types/advancedPH';
import PHExport from './PHExport';

// --- Tipos de Datos ---
interface CalculationStep {
    title: string;
    explanation: string;
    formula: string;
}

export interface PHHistoryItem {
    key: string; // UUID
    calculationType: CalculationType;
    inputSummary: string;
    ph: number;
    timestamp: string; // ISO 8601 string
    calculationTimeMs: number;
    hasWarnings: boolean;
    steps: CalculationStep[];
}

interface PHHistoryProps {
    userId?: string;
    limit?: number;
    onCalculationSelect?: (calculation: PHHistoryItem) => void;
    onDuplicateCalculation?: (calculation: any) => void;
}

// Removemos los datos mock ya que ahora usaremos datos reales

const { RangePicker } = DatePicker;

const PHHistory: React.FC<PHHistoryProps> = ({ userId, limit = 10, onCalculationSelect, onDuplicateCalculation }) => {
    const dispatch = useAppDispatch();
    const { calculationHistory, isLoadingHistory, historyCount, errors } = useAppSelector((state) => state.advancedPH);
    
    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [viewingRecord, setViewingRecord] = useState<PHHistoryItem | null>(null);
    const [searchText, setSearchText] = useState('');
    const [filters, setFilters] = useState<HistoryFilters>({});
    const [currentPage, setCurrentPage] = useState(1);
    const [exportModalVisible, setExportModalVisible] = useState(false);
    
    // Cargar historial al montar el componente o cuando cambien los filtros
    useEffect(() => {
        const loadFilters: HistoryFilters = {
            ...filters,
            page: currentPage,
            pageSize: limit,
            searchQuery: searchText || undefined
        };
        dispatch(fetchPHHistory(loadFilters));
    }, [dispatch, currentPage, limit, searchText, filters]);

    const handleViewDetails = (record: PHHistoryItem) => {
        setViewingRecord(record);
        setIsModalVisible(true);
        if (onCalculationSelect) {
            onCalculationSelect(record);
        }
    };

    const handleDelete = async (recordKey: string) => {
        // Eliminar el cálculo usando Redux
        await dispatch(deleteCalculation(recordKey));
        // Recargar el historial después de eliminar
        dispatch(fetchPHHistory({ ...filters, page: currentPage, pageSize: limit }));
    };

    const handleDuplicate = (record: PHHistoryItem) => {
        // Buscar el cálculo original completo en el historial
        const originalCalc = calculationHistory.find((calc: any) => {
            const calcId = calc.key || calc.id || calc.calculation_id || calc.metadata?.calculation_id || '';
            return String(calcId) === record.key;
        });
        
        if (originalCalc && onDuplicateCalculation) {
            // Llamar al callback con los datos del cálculo para duplicar
            onDuplicateCalculation(originalCalc);
        } else {
            console.log('No se encontró el cálculo original para duplicar');
        }
    };

    // Mapear los datos del store al formato esperado por el componente
    const historyData = useMemo(() => {
        if (!calculationHistory || !Array.isArray(calculationHistory)) {
            return [];
        }
        
        return calculationHistory.map(calc => {
            // Manejar diferentes estructuras posibles de los datos
            const id = calc.key || calc.id || calc.calculation_id || '';
            const calcType = calc.calculationType || calc.calculation_type || '';
            const inputData = calc.inputSummary || calc.input_data || {};
            const results = calc.result || calc.results || {};
            const warnings = calc.warnings || results.warnings || [];
            const steps = calc.calculation_steps || results.calculation_steps || [];
            
            // Generar resumen de entrada si no existe
            let inputSummary = calc.inputSummary;
            if (!inputSummary && inputData) {
                if (typeof inputData === 'object') {
                    const inputType = inputData.input_type || '';
                    const inputValue = inputData.input_value;
                    inputSummary = `${inputType}: ${inputValue}`;
                } else {
                    inputSummary = String(inputData);
                }
            }
            
            return {
                key: String(id),
                calculationType: calcType as CalculationType,
                inputSummary: inputSummary || 'Sin descripción',
                ph: results.ph || 0,
                timestamp: calc.timestamp || calc.created_at || new Date().toISOString(),
                calculationTimeMs: calc.calculationTimeMs || calc.calculation_time_ms || 0,
                hasWarnings: Array.isArray(warnings) ? warnings.length > 0 : false,
                steps: Array.isArray(steps) ? steps.map((step, idx) => {
                    if (typeof step === 'string') {
                        return {
                            title: `Paso ${idx + 1}`,
                            explanation: step,
                            formula: ''
                        };
                    }
                    return {
                        title: step.title || `Paso ${idx + 1}`,
                        explanation: step.explanation || step.description || '',
                        formula: step.formula || ''
                    };
                }) : []
            };
        });
    }, [calculationHistory]);
    
    const columns: ColumnsType<PHHistoryItem> = [
        { 
            title: 'Tipo de Cálculo', 
            dataIndex: 'calculationType', 
            key: 'calculationType', 
            sorter: (a, b) => (a.calculationType || '').localeCompare(b.calculationType || ''), 
            render: (type: string) => type ? <Tag color="blue">{type.replace(/_/g, ' ').toUpperCase()}</Tag> : <Tag>N/A</Tag> 
        },
        { 
            title: 'Entrada', 
            dataIndex: 'inputSummary', 
            key: 'inputSummary',
            render: (text: string) => text || 'Sin descripción'
        },
        { 
            title: 'Resultado (pH)', 
            dataIndex: 'ph', 
            key: 'ph', 
            sorter: (a, b) => (a.ph || 0) - (b.ph || 0), 
            render: (ph: number) => ph !== undefined && ph !== null ? ph.toFixed(2) : 'N/A' 
        },
        { 
            title: 'Fecha', 
            dataIndex: 'timestamp', 
            key: 'timestamp', 
            sorter: (a, b) => {
                const dateA = a.timestamp ? new Date(a.timestamp).getTime() : 0;
                const dateB = b.timestamp ? new Date(b.timestamp).getTime() : 0;
                return dateB - dateA;
            }, 
            render: (ts: string) => ts ? new Date(ts).toLocaleString() : 'N/A' 
        },
        { 
            title: 'Tiempo (ms)', 
            dataIndex: 'calculationTimeMs', 
            key: 'calculationTimeMs', 
            sorter: (a, b) => (a.calculationTimeMs || 0) - (b.calculationTimeMs || 0),
            render: (time: number) => time !== undefined ? time : 'N/A'
        },
        { 
            title: 'Advertencias', 
            dataIndex: 'hasWarnings', 
            key: 'hasWarnings', 
            render: (has: boolean) => has ? <Tag color="warning">Sí</Tag> : <Tag color="success">No</Tag> 
        },
        {
            title: 'Acciones',
            key: 'actions',
            render: (_, record) => (
                <Space size="middle">
                    <Tooltip title="Ver Detalles"><Button icon={<EyeIcon className="h-4 w-4" />} onClick={() => handleViewDetails(record)} /></Tooltip>
                    <Tooltip title="Duplicar Cálculo"><Button icon={<DocumentDuplicateIcon className="h-4 w-4" />} onClick={() => handleDuplicate(record)} /></Tooltip>
                    <Tooltip title="Eliminar"><Button icon={<TrashIcon className="h-4 w-4" />} danger onClick={() => handleDelete(record.key)} /></Tooltip>
                </Space>
            ),
        },
    ];

    const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
        setSelectedRowKeys(newSelectedRowKeys);
    };

    const rowSelection = {
        selectedRowKeys,
        onChange: onSelectChange,
    };
    
    const hasSelected = selectedRowKeys.length > 0;
    
    const handleExport = () => {
        if (selectedRowKeys.length > 0) {
            setExportModalVisible(true);
        }
    };

    const handleExportComplete = (result: { format: string; url?: string; error?: string }) => {
        if (result.error) {
            console.error('Export error:', result.error);
        } else if (result.url) {
            console.log('Export successful, URL:', result.url);
        }
        setExportModalVisible(false);
    };

    return (
        <Card>
            <Typography.Title level={4}>Historial de Cálculos</Typography.Title>
            
            {errors.history && (
                <Alert
                    message="Error al cargar el historial"
                    description={errors.history}
                    type="error"
                    showIcon
                    className="mb-4"
                />
            )}
            
            <Row gutter={[16, 16]} className="mb-4">
                <Col xs={24} sm={8}><Statistic title="Cálculos Totales" value={historyCount} /></Col>
                <Col xs={24} sm={8}>
                    <Statistic 
                        title="Tiempo Promedio (ms)" 
                        value={historyData.length > 0 ? historyData.reduce((acc, curr) => acc + curr.calculationTimeMs, 0) / historyData.length : 0} 
                        precision={0} 
                    />
                </Col>
                <Col xs={24} sm={8}><Statistic title="Con Advertencias" value={historyData.filter(d => d.hasWarnings).length} /></Col>
            </Row>

            <div className="flex flex-col sm:flex-row justify-between mb-4 gap-2">
                <Input.Search
                    placeholder="Buscar en historial..."
                    onChange={e => setSearchText(e.target.value)}
                    style={{ maxWidth: 300 }}
                />
                <Space>
                <Select
                    placeholder="Filtrar por tipo"
                    allowClear
                    onChange={value => setFilters(prev => ({ ...prev, calculationType: value as any }))}
                    style={{ width: 150 }}
                >
                        <Select.Option value="concentration_to_ph">Concentración</Select.Option>
                        <Select.Option value="buffer">Buffer</Select.Option>
                        <Select.Option value="ph_to_all">pH Inverso</Select.Option>
                    </Select>
                    <Select
                        placeholder="Advertencias"
                        allowClear
                        onChange={value => setFilters(prev => ({ ...prev, warnings: value }))}
                        style={{ width: 130 }}
                    >
                        <Select.Option value={true}>Con Warnings</Select.Option>
                        <Select.Option value={false}>Sin Warnings</Select.Option>
                    </Select>
                </Space>
            </div>

            <div className="mb-4">
                <Button 
                    type="primary" 
                    disabled={!hasSelected} 
                    icon={<ArrowDownTrayIcon className="h-4 w-4" />}
                    onClick={handleExport}
                >
                    Exportar Seleccionados ({selectedRowKeys.length})
                </Button>
            </div>

            <Table
                rowSelection={rowSelection}
                columns={columns}
                dataSource={historyData}
                loading={isLoadingHistory}
                pagination={{ 
                    pageSize: limit,
                    current: currentPage,
                    total: historyCount,
                    onChange: (page) => setCurrentPage(page)
                }}
                scroll={{ x: 'max-content' }} // Para responsividad en móviles
            />

            <Modal
                title="Detalles del Cálculo"
                open={isModalVisible}
                onCancel={() => setIsModalVisible(false)}
                footer={[<Button key="back" onClick={() => setIsModalVisible(false)}>Cerrar</Button>]}
                width={600}
            >
                {viewingRecord && (
                    <div>
                        <p><strong>ID:</strong> {viewingRecord.key}</p>
                        <p><strong>Tipo:</strong> {viewingRecord.calculationType}</p>
                        <p><strong>Entrada:</strong> {viewingRecord.inputSummary}</p>
                        <p><strong>Resultado pH:</strong> {viewingRecord.ph.toFixed(2)}</p>
                        <p><strong>Fecha:</strong> {new Date(viewingRecord.timestamp).toLocaleString()}</p>
                        <Typography.Title level={5} className="mt-4">Pasos del Cálculo</Typography.Title>
                        {viewingRecord.steps.length > 0 ? (
                            viewingRecord.steps.map((step, index) => (
                                <div key={index} className="mb-2 p-2 border-l-4 border-blue-500 bg-gray-50">
                                    <Typography.Text strong>{step.title}</Typography.Text>
                                    <p>{step.explanation}</p>
                                    <Typography.Text code>{step.formula}</Typography.Text>
                                </div>
                            ))
                        ) : <p>No hay pasos detallados para este tipo de cálculo.</p>}
                    </div>
                )}
            </Modal>

            {/* Modal de Exportación */}
            <PHExport
                calculationIds={selectedRowKeys as string[]}
                visible={exportModalVisible}
                onClose={() => setExportModalVisible(false)}
                onExportComplete={handleExportComplete}
                allHistoryData={historyData}
                maxExportSize={100}
            />
        </Card>
    );
};

export default PHHistory;
