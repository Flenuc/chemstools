"use client";

import React, { useState, useEffect, useMemo } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';
import { api } from '@/services/api';
import { 
  Card, 
  Input, 
  Typography, 
  Space, 
  Spin, 
  Alert, 
  Empty,
  List,
  Tag,
  Divider,
  Badge,
  Row,
  Col,
  Skeleton
} from 'antd';
import { 
  SearchOutlined, 
  BookOutlined,
  FileTextOutlined,
  TagsOutlined
} from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';


const { Title, Text, Paragraph } = Typography;

interface GlossaryTerm {
  id: number;
  term: string;
  definition: string;
}

const GlossaryPage = () => {
  const [terms, setTerms] = useState<GlossaryTerm[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLetter, setSelectedLetter] = useState<string | null>(null);
  const token = useSelector((state: RootState) => state.auth.accessToken);

  useEffect(() => {
    const fetchTerms = async () => {
      if (!token) {
        setError("Autenticación requerida.");
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const responseData = await api.get('calculators/glossary/');
        if (Array.isArray(responseData)) {
          setTerms(responseData);
        } else {
          console.error("Unexpected data format from glossary API:", responseData);
          setError('Formato de datos inesperado del servidor.');
          setTerms([]);
        }
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Error al cargar el glosario.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTerms();
  }, [token]);

  // Generar índice alfabético
  const alphabetIndex = useMemo(() => {
    const letters = new Set<string>();
    terms.forEach(term => {
      const firstLetter = term.term[0]?.toUpperCase();
      if (firstLetter && /[A-Z]/.test(firstLetter)) {
        letters.add(firstLetter);
      }
    });
    return Array.from(letters).sort();
  }, [terms]);

  // Filtrar términos basado en búsqueda y letra seleccionada
  const filteredTerms = useMemo(() => {
    if (!Array.isArray(terms)) return [];
    
    let filtered = terms;
    
    // Filtrar por búsqueda
    if (searchTerm) {
      filtered = filtered.filter(term =>
        term.term.toLowerCase().includes(searchTerm.toLowerCase()) ||
        term.definition.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Filtrar por letra seleccionada
    if (selectedLetter) {
      filtered = filtered.filter(term =>
        term.term[0]?.toUpperCase() === selectedLetter
      );
    }
    
    // Ordenar alfabéticamente
    return filtered.sort((a, b) => a.term.localeCompare(b.term));
  }, [terms, searchTerm, selectedLetter]);

  // Variantes de animación
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100
      }
    }
  };

  return (
    <motion.div 
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4 md:p-8"
    >
      <div className="max-w-7xl mx-auto">
        {/* Header con estadísticas */}
        <motion.div variants={itemVariants}>
          <Card className="mb-8 bg-white/90 backdrop-blur-sm shadow-xl border-0">
            <Row gutter={[16, 16]} align="middle">
              <Col xs={24} lg={12}>
                <Space direction="vertical" size="small">
                  <Title level={1} className="!mb-2">
                    <BookOutlined className="mr-3 text-blue-600" />
                    Glosario de Términos Químicos
                  </Title>
                  <Text type="secondary" className="text-lg">
                    Definiciones claras y precisas de conceptos químicos fundamentales
                  </Text>
                </Space>
              </Col>
              <Col xs={24} lg={12}>
                <Row gutter={16} justify="end">
                  <Col>
                    <Card size="small" className="text-center bg-blue-50 border-blue-200">
                      <Text type="secondary">Total de términos</Text>
                      <Title level={3} className="!mt-1 !mb-0 text-blue-600">
                        {terms.length}
                      </Title>
                    </Card>
                  </Col>
                  <Col>
                    <Card size="small" className="text-center bg-green-50 border-green-200">
                      <Text type="secondary">Filtrados</Text>
                      <Title level={3} className="!mt-1 !mb-0 text-green-600">
                        {filteredTerms.length}
                      </Title>
                    </Card>
                  </Col>
                </Row>
              </Col>
            </Row>
          </Card>
        </motion.div>

        {/* Barra de búsqueda y filtros */}
        <motion.div variants={itemVariants}>
          <Card className="mb-6 shadow-lg border-0">
            <Space direction="vertical" className="w-full" size="large">
              <Input
                size="large"
                placeholder="Buscar por término o definición..."
                prefix={<SearchOutlined className="text-gray-400" />}
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setSelectedLetter(null); // Limpiar filtro alfabético al buscar
                }}
                allowClear
                className="hover:border-blue-400 focus:border-blue-500"
              />
              
              {/* Índice alfabético */}
              {alphabetIndex.length > 0 && (
                <div>
                  <Text type="secondary" className="block mb-2">
                    Filtrar por letra inicial:
                  </Text>
                  <Space wrap>
                    <Tag
                      className="cursor-pointer hover:scale-105 transition-transform"
                      color={!selectedLetter ? 'blue' : 'default'}
                      onClick={() => setSelectedLetter(null)}
                    >
                      Todas
                    </Tag>
                    {alphabetIndex.map(letter => (
                      <Tag
                        key={letter}
                        className="cursor-pointer hover:scale-105 transition-transform"
                        color={selectedLetter === letter ? 'blue' : 'default'}
                        onClick={() => {
                          setSelectedLetter(letter);
                          setSearchTerm(''); // Limpiar búsqueda al filtrar por letra
                        }}
                      >
                        {letter}
                      </Tag>
                    ))}
                  </Space>
                </div>
              )}
            </Space>
          </Card>
        </motion.div>

        {/* Estados de carga y error */}
        {loading && (
          <motion.div variants={itemVariants}>
            <Card className="text-center py-12">
              <Spin size="large" tip="Cargando términos..." />
            </Card>
          </motion.div>
        )}

        {error && (
          <motion.div variants={itemVariants}>
            <Alert
              message="Error"
              description={error}
              type="error"
              showIcon
              className="mb-6"
            />
          </motion.div>
        )}

        {/* Lista de términos */}
        {!loading && !error && (
          <AnimatePresence mode="wait">
            {filteredTerms.length > 0 ? (
              <motion.div
                key="terms-list"
                initial="hidden"
                animate="visible"
                exit="hidden"
                variants={containerVariants}
              >
                <Row gutter={[16, 16]}>
                  {filteredTerms.map((term, index) => (
                    <Col xs={24} lg={12} key={term.id}>
                      <motion.div
                        variants={itemVariants}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <Card 
                          hoverable
                          className="h-full shadow-md hover:shadow-xl transition-shadow duration-300 border-l-4 border-l-blue-500"
                        >
                          <Space direction="vertical" className="w-full">
                            <div className="flex items-start justify-between">
                              <Title level={4} className="!mb-0 text-blue-700">
                                <FileTextOutlined className="mr-2" />
                                {term.term}
                              </Title>
                              <Badge 
                                count={index + 1} 
                                style={{ backgroundColor: '#52c41a' }}
                                className="mt-1"
                              />
                            </div>
                            <Divider className="!my-3" />
                            <Paragraph 
                              className="!mb-0 text-gray-600"
                              ellipsis={{ rows: 4, expandable: true, symbol: 'Ver más' }}
                            >
                              {term.definition}
                            </Paragraph>
                            <div className="mt-2">
                              <Tag color="blue" icon={<TagsOutlined />}>
                                Química
                              </Tag>
                              {term.term[0] && (
                                <Tag color="cyan">
                                  {term.term[0].toUpperCase()}
                                </Tag>
                              )}
                            </div>
                          </Space>
                        </Card>
                      </motion.div>
                    </Col>
                  ))}
                </Row>
              </motion.div>
            ) : (
              <motion.div
                key="empty-state"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
              >
                <Card className="text-center py-12">
                  <Empty
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                    description={
                      <Space direction="vertical">
                        <Text type="secondary" className="text-lg">
                          No se encontraron términos
                        </Text>
                        {(searchTerm || selectedLetter) && (
                          <Text type="secondary">
                            Intenta con otros criterios de búsqueda
                          </Text>
                        )}
                      </Space>
                    }
                  />
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        )}

        {/* Botón flotante para volver arriba */}
        {filteredTerms.length > 5 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="fixed bottom-8 right-8 z-10"
          >
            <Card 
              className="cursor-pointer shadow-lg hover:shadow-xl transition-shadow"
              onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            >
              <Text className="text-blue-600">↑ Volver arriba</Text>
            </Card>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

export default GlossaryPage;