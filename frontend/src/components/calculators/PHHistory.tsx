import React, { useState, useMemo } from 'react';
import { Table, Input, Button, Modal, Tag, Space, Typography, Card, Statistic, Row, Col, DatePicker, Select, Tooltip } from 'antd';
import { EyeIcon, TrashIcon, DocumentDuplicateIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import type { ColumnsType } from 'antd/es/table';

// --- Tipos de Datos ---
interface CalculationStep {
    title: string;
    explanation: string;
    formula: string;
}

export interface PHHistoryItem {
    key: string; // UUID
    calculationType: 'concentration_to_ph' | 'buffer' | 'ph_to_all';
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
}

// --- Mock Data ---
const mockHistoryData: PHHistoryItem[] = [
    { key: '1', calculationType: 'concentration_to_ph', inputSummary: 'HCl 0.1M', ph: 1.00, timestamp: new Date().toISOString(), calculationTimeMs: 15, hasWarnings: true, steps: [{ title: 'Paso 1', explanation: '...', formula: 'pH = -log[H+]' }] },
    { key: '2', calculationType: 'buffer', inputSummary: 'Acetato 0.1M/0.1M', ph: 4.76, timestamp: new Date(Date.now() - 86400000).toISOString(), calculationTimeMs: 45, hasWarnings: false, steps: [{ title: 'Paso 1', explanation: '...', formula: 'Henderson-Hasselbalch' }] },
    { key: '3', calculationType: 'ph_to_all', inputSummary: 'pH = 7.4', ph: 7.40, timestamp: new Date(Date.now() - 172800000).toISOString(), calculationTimeMs: 8, hasWarnings: false, steps: [] },
    // ... agregar más datos para paginación
];

const { RangePicker } = DatePicker;

const PHHistory: React.FC<PHHistoryProps> = ({ userId, limit = 10, onCalculationSelect }) => {
    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [viewingRecord, setViewingRecord] = useState<PHHistoryItem | null>(null);
    const [searchText, setSearchText] = useState('');
    const [filters, setFilters] = useState<{ type?: string; warnings?: boolean }>({});

    const handleViewDetails = (record: PHHistoryItem) => {
        setViewingRecord(record);
        setIsModalVisible(true);
        if (onCalculationSelect) {
            onCalculationSelect(record);
        }
    };

    const handleDelete = (recordKey: string) => {
        // Lógica para eliminar (simulada)
        console.log(`Deleting record ${recordKey}`);
    };

    const handleDuplicate = (record: PHHistoryItem) => {
        // Lógica para duplicar (simulada)
        console.log(`Duplicating record ${record.key}`);
    };

    const filteredData = useMemo(() => {
        return mockHistoryData.filter(item => {
            const matchesSearch = item.inputSummary.toLowerCase().includes(searchText.toLowerCase());
            const matchesType = !filters.type || item.calculationType === filters.type;
            const matchesWarnings = filters.warnings === undefined || item.hasWarnings === filters.warnings;
            return matchesSearch && matchesType && matchesWarnings;
        });
    }, [searchText, filters]);
    
    const columns: ColumnsType<PHHistoryItem> = [
        { title: 'Tipo de Cálculo', dataIndex: 'calculationType', key: 'calculationType', sorter: (a, b) => a.calculationType.localeCompare(b.calculationType), render: (type: string) => <Tag color="blue">{type.replace(/_/g, ' ').toUpperCase()}</Tag> },
        { title: 'Entrada', dataIndex: 'inputSummary', key: 'inputSummary' },
        { title: 'Resultado (pH)', dataIndex: 'ph', key: 'ph', sorter: (a, b) => a.ph - b.ph, render: (ph: number) => ph.toFixed(2) },
        { title: 'Fecha', dataIndex: 'timestamp', key: 'timestamp', sorter: (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(), render: (ts: string) => new Date(ts).toLocaleString() },
        { title: 'Tiempo (ms)', dataIndex: 'calculationTimeMs', key: 'calculationTimeMs', sorter: (a, b) => a.calculationTimeMs - b.calculationTimeMs },
        { title: 'Advertencias', dataIndex: 'hasWarnings', key: 'hasWarnings', render: (has: boolean) => has ? <Tag color="warning">Sí</Tag> : <Tag color="success">No</Tag> },
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

    return (
        <Card>
            <Typography.Title level={4}>Historial de Cálculos</Typography.Title>
            
            <Row gutter={[16, 16]} className="mb-4">
                <Col xs={24} sm={8}><Statistic title="Cálculos Totales" value={mockHistoryData.length} /></Col>
                <Col xs={24} sm={8}><Statistic title="Tiempo Promedio (ms)" value={mockHistoryData.reduce((acc, curr) => acc + curr.calculationTimeMs, 0) / mockHistoryData.length} precision={0} /></Col>
                <Col xs={24} sm={8}><Statistic title="Con Advertencias" value={mockHistoryData.filter(d => d.hasWarnings).length} /></Col>
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
                        onChange={value => setFilters(prev => ({ ...prev, type: value }))}
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
                <Button type="primary" disabled={!hasSelected} icon={<ArrowDownTrayIcon className="h-4 w-4" />}>
                    Exportar Seleccionados ({selectedRowKeys.length})
                </Button>
            </div>

            <Table
                rowSelection={rowSelection}
                columns={columns}
                dataSource={filteredData}
                pagination={{ pageSize: limit }}
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
        </Card>
    );
};

export default PHHistory;