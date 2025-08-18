'use client';
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, Typography, Divider, Tag, message } from 'antd';
import { CalculatorOutlined, ExperimentOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { Form, FormItem, Input, FormActions } from '@/components/ui/forms';
import { Button, Alert } from '@/components/ui';
import { AnimatedDiv, staggerContainer, staggerItem } from '@/lib/animations';
import { cn } from '@/lib/utils';

const { Title, Text, Paragraph } = Typography;

interface ElementCount {
  symbol: string;
  count: number;
  mass: number;
  name: string;
}

// Tabla periódica simplificada con masas atómicas
const ATOMIC_MASSES: { [key: string]: { mass: number; name: string } } = {
  H: { mass: 1.008, name: 'Hidrógeno' },
  He: { mass: 4.003, name: 'Helio' },
  Li: { mass: 6.941, name: 'Litio' },
  Be: { mass: 9.012, name: 'Berilio' },
  B: { mass: 10.811, name: 'Boro' },
  C: { mass: 12.011, name: 'Carbono' },
  N: { mass: 14.007, name: 'Nitrógeno' },
  O: { mass: 15.999, name: 'Oxígeno' },
  F: { mass: 18.998, name: 'Flúor' },
  Ne: { mass: 20.180, name: 'Neón' },
  Na: { mass: 22.990, name: 'Sodio' },
  Mg: { mass: 24.305, name: 'Magnesio' },
  Al: { mass: 26.982, name: 'Aluminio' },
  Si: { mass: 28.086, name: 'Silicio' },
  P: { mass: 30.974, name: 'Fósforo' },
  S: { mass: 32.065, name: 'Azufre' },
  Cl: { mass: 35.453, name: 'Cloro' },
  Ar: { mass: 39.948, name: 'Argón' },
  K: { mass: 39.098, name: 'Potasio' },
  Ca: { mass: 40.078, name: 'Calcio' },
  Fe: { mass: 55.845, name: 'Hierro' },
  Cu: { mass: 63.546, name: 'Cobre' },
  Zn: { mass: 65.380, name: 'Zinc' },
  Ag: { mass: 107.868, name: 'Plata' },
  Au: { mass: 196.967, name: 'Oro' },
};

export default function MolarMassCalculatorEnhanced() {
  const [form] = Form.useForm();
  const [formula, setFormula] = useState('');
  const [elements, setElements] = useState<ElementCount[]>([]);
  const [totalMass, setTotalMass] = useState(0);
  const [error, setError] = useState('');
  const [calculating, setCalculating] = useState(false);

  const parseFormula = (formula: string): ElementCount[] => {
    const regex = /([A-Z][a-z]?)(\d*)/g;
    const result: ElementCount[] = [];
    let match;

    while ((match = regex.exec(formula)) !== null) {
      const symbol = match[1];
      const count = match[2] ? parseInt(match[2]) : 1;

      if (!ATOMIC_MASSES[symbol]) {
        throw new Error(`Elemento desconocido: ${symbol}`);
      }

      const existingElement = result.find(e => e.symbol === symbol);
      if (existingElement) {
        existingElement.count += count;
      } else {
        result.push({
          symbol,
          count,
          mass: ATOMIC_MASSES[symbol].mass,
          name: ATOMIC_MASSES[symbol].name,
        });
      }
    }

    return result;
  };

  const calculateMolarMass = () => {
    try {
      setError('');
      setCalculating(true);
      
      const formulaValue = form.getFieldValue('formula');
      if (!formulaValue) {
        setError('Por favor ingresa una fórmula química');
        return;
      }

      // Animación de cálculo
      setTimeout(() => {
        try {
          const parsedElements = parseFormula(formulaValue);
          if (parsedElements.length === 0) {
            setError('Fórmula inválida');
            return;
          }

          const mass = parsedElements.reduce(
            (sum, el) => sum + el.mass * el.count,
            0
          );

          setElements(parsedElements);
          setTotalMass(mass);
          setFormula(formulaValue);
          message.success('Cálculo completado');
        } catch (err: any) {
          setError(err.message);
          message.error(err.message);
        } finally {
          setCalculating(false);
        }
      }, 500);
    } catch (err: any) {
      setError(err.message);
      setCalculating(false);
    }
  };

  const exampleFormulas = [
    { formula: 'H2O', name: 'Agua' },
    { formula: 'CO2', name: 'Dióxido de carbono' },
    { formula: 'NaCl', name: 'Sal común' },
    { formula: 'C6H12O6', name: 'Glucosa' },
    { formula: 'H2SO4', name: 'Ácido sulfúrico' },
    { formula: 'Ca(OH)2', name: 'Hidróxido de calcio' },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <AnimatedDiv animation="fadeInDown">
        <div className="text-center mb-8">
          <Title level={2} className="!mb-2">
            <CalculatorOutlined className="mr-2" />
            Calculadora de Masa Molar
          </Title>
          <Text className="text-gray-600">
            Calcula la masa molar de cualquier compuesto químico
          </Text>
        </div>
      </AnimatedDiv>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <AnimatedDiv animation="fadeInLeft">
          <Card className="h-full shadow-lg">
            <Form
              form={form}
              layout="vertical"
              onFinish={calculateMolarMass}
            >
              <FormItem
                label="Fórmula Química"
                name="formula"
                rules={[{ required: true, message: 'Ingresa una fórmula' }]}
                animation="slideIn"
              >
                <Input
                  size="large"
                  placeholder="Ej: H2SO4, Ca(OH)2, C6H12O6"
                  prefix={<ExperimentOutlined />}
                  disabled={calculating}
                />
              </FormItem>

              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-4"
                >
                  <Alert type="error" message={error} closable onClose={() => setError('')} />
                </motion.div>
              )}

              <Button
                type="primary"
                variant="primary"
                size="large"
                loading={calculating}
                className="w-full"
              >
                {calculating ? 'Calculando...' : 'Calcular Masa Molar'}
              </Button>
            </Form>

            <Divider />

            <div>
              <Text strong className="block mb-3">
                Ejemplos rápidos:
              </Text>
              <motion.div 
                className="flex flex-wrap gap-2"
                variants={staggerContainer}
                initial="hidden"
                animate="visible"
              >
                {exampleFormulas.map((example, index) => (
                  <motion.div
                    key={example.formula}
                    variants={staggerItem}
                    custom={index}
                  >
                    <Tag
                      className="cursor-pointer px-3 py-1 text-sm"
                      color="blue"
                      onClick={() => {
                        form.setFieldsValue({ formula: example.formula });
                        calculateMolarMass();
                      }}
                    >
                      {example.formula} ({example.name})
                    </Tag>
                  </motion.div>
                ))}
              </motion.div>
            </div>
          </Card>
        </AnimatedDiv>

        {/* Results Section */}
        <AnimatedDiv animation="fadeInRight">
          <Card className="h-full shadow-lg">
            <Title level={4} className="!mb-4">
              <InfoCircleOutlined className="mr-2" />
              Resultados
            </Title>

            <AnimatePresence mode="wait">
              {elements.length > 0 ? (
                <motion.div
                  key="results"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  className="space-y-4"
                >
                  {/* Formula Display */}
                  <div className="text-center p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                    <Text className="text-2xl font-bold text-gray-800">
                      {formula}
                    </Text>
                  </div>

                  {/* Elements Breakdown */}
                  <div className="space-y-2">
                    <Text strong className="block mb-2">
                      Composición:
                    </Text>
                    {elements.map((element, index) => (
                      <motion.div
                        key={element.symbol}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white font-bold">
                            {element.symbol}
                          </div>
                          <div>
                            <Text strong>{element.name}</Text>
                            <Text className="block text-xs text-gray-500">
                              {element.count} átomo{element.count > 1 ? 's' : ''}
                            </Text>
                          </div>
                        </div>
                        <div className="text-right">
                          <Text strong>{(element.mass * element.count).toFixed(3)}</Text>
                          <Text className="block text-xs text-gray-500">g/mol</Text>
                        </div>
                      </motion.div>
                    ))}
                  </div>

                  <Divider />

                  {/* Total Mass */}
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 200, damping: 20 }}
                    className="text-center p-6 bg-gradient-to-r from-green-400 to-blue-500 rounded-lg text-white"
                  >
                    <Text className="block text-sm uppercase tracking-wide opacity-90">
                      Masa Molar Total
                    </Text>
                    <div className="text-4xl font-bold mt-2">
                      {totalMass.toFixed(3)} g/mol
                    </div>
                  </motion.div>
                </motion.div>
              ) : (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-center py-12 text-gray-500"
                >
                  <ExperimentOutlined className="text-6xl mb-4 text-gray-300" />
                  <Paragraph>
                    Ingresa una fórmula química para calcular su masa molar
                  </Paragraph>
                  <Text className="text-sm">
                    Usa la notación estándar: H2O, CO2, Ca(OH)2, etc.
                  </Text>
                </motion.div>
              )}
            </AnimatePresence>
          </Card>
        </AnimatedDiv>
      </div>

      {/* Information Card */}
      <AnimatedDiv animation="fadeInUp" delay={0.3}>
        <Card className="shadow-lg bg-gradient-to-r from-blue-50 to-purple-50">
          <div className="grid md:grid-cols-3 gap-4 text-center">
            <div>
              <Text strong className="block text-primary-600">¿Qué es la masa molar?</Text>
              <Text className="text-sm">
                La masa de un mol de sustancia, expresada en g/mol
              </Text>
            </div>
            <div>
              <Text strong className="block text-primary-600">¿Cómo se calcula?</Text>
              <Text className="text-sm">
                Suma de las masas atómicas de todos los átomos
              </Text>
            </div>
            <div>
              <Text strong className="block text-primary-600">¿Para qué sirve?</Text>
              <Text className="text-sm">
                Convertir entre masa y moles en cálculos químicos
              </Text>
            </div>
          </div>
        </Card>
      </AnimatedDiv>
    </div>
  );
}
