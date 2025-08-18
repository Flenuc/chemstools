'use client';
import React, { useState } from 'react';
import { Tabs, message } from 'antd';
import { motion } from 'framer-motion';
import PeriodicTableEnhanced from '@/components/features/PeriodicTableEnhanced';
import { 
  Form, 
  FormItem, 
  Input, 
  TextArea, 
  Select, 
  AnimatedSwitch, 
  RadioGroup, 
  CheckboxGroup,
  UploadArea,
  AnimatedSlider,
  FormActions,
  validateMessages 
} from '@/components/ui/forms';
import { 
  Button, 
  Card, 
  Container, 
  Modal, 
  Alert,
  Badge,
  Tag,
  Tooltip
} from '@/components/ui';
import { AnimatedDiv, PageTransition } from '@/lib/animations';
import { 
  BeakerIcon, 
  BookOpenIcon, 
  ChartBarIcon,
  SparklesIcon,
  UserIcon,
  AcademicCapIcon 
} from '@heroicons/react/24/outline';

export default function DemoHybrid() {
  const [form] = Form.useForm();
  const [showModal, setShowModal] = useState(false);
  const [switchValue, setSwitchValue] = useState(false);
  const [radioValue, setRadioValue] = useState('option1');
  const [checkboxValues, setCheckboxValues] = useState<string[]>([]);
  const [sliderValue, setSliderValue] = useState(50);
  const [activeTab, setActiveTab] = useState('1');

  const handleFormSubmit = () => {
    form.validateFields().then((values) => {
      console.log('Form values:', values);
      message.success('Formulario enviado correctamente!');
    }).catch((error) => {
      message.error('Por favor completa todos los campos requeridos');
    });
  };

  const radioOptions = [
    {
      label: 'Básico',
      value: 'basic',
      description: 'Funcionalidades esenciales',
      icon: <BeakerIcon className="w-5 h-5" />
    },
    {
      label: 'Profesional',
      value: 'pro',
      description: 'Todas las características avanzadas',
      icon: <AcademicCapIcon className="w-5 h-5" />
    },
    {
      label: 'Empresarial',
      value: 'enterprise',
      description: 'Solución completa para organizaciones',
      icon: <ChartBarIcon className="w-5 h-5" />
    }
  ];

  const checkboxOptions = [
    {
      label: 'Notificaciones por email',
      value: 'email',
      icon: <BookOpenIcon className="w-5 h-5" />
    },
    {
      label: 'Actualizaciones en tiempo real',
      value: 'realtime',
      icon: <SparklesIcon className="w-5 h-5" />
    },
    {
      label: 'Análisis avanzado',
      value: 'analytics',
      icon: <ChartBarIcon className="w-5 h-5" />
    }
  ];

  const tabItems = [
    {
      key: '1',
      label: 'Tabla Periódica',
      children: (
        <AnimatedDiv animation="fadeIn">
          <PeriodicTableEnhanced />
        </AnimatedDiv>
      )
    },
    {
      key: '2',
      label: 'Formularios',
      children: (
        <AnimatedDiv animation="fadeInUp" className="max-w-4xl mx-auto">
          <Card title="Formulario de Ejemplo" className="shadow-xl">
            <Form
              form={form}
              layout="vertical"
              validateMessages={validateMessages}
            >
              <div className="grid md:grid-cols-2 gap-6">
                <FormItem
                  label="Nombre"
                  name="name"
                  rules={[{ required: true }]}
                  animation="slideIn"
                >
                  <Input 
                    placeholder="Ingresa tu nombre"
                    icon={<UserIcon className="w-5 h-5" />}
                  />
                </FormItem>

                <FormItem
                  label="Email"
                  name="email"
                  rules={[{ required: true, type: 'email' }]}
                  animation="slideIn"
                  delay={0.1}
                >
                  <Input 
                    placeholder="correo@ejemplo.com"
                    type="email"
                  />
                </FormItem>
              </div>

              <FormItem
                label="Descripción"
                name="description"
                animation="slideIn"
                delay={0.2}
              >
                <TextArea 
                  placeholder="Describe tu proyecto..."
                  rows={4}
                  showCount
                  maxLength={500}
                />
              </FormItem>

              <FormItem
                label="Categoría"
                name="category"
                animation="slideIn"
                delay={0.3}
              >
                <Select
                  placeholder="Selecciona una categoría"
                  options={[
                    { label: 'Química Orgánica', value: 'organic' },
                    { label: 'Química Inorgánica', value: 'inorganic' },
                    { label: 'Bioquímica', value: 'biochem' },
                    { label: 'Física Química', value: 'physical' }
                  ]}
                />
              </FormItem>

              <div className="space-y-6 mt-6">
                <div>
                  <h3 className="text-lg font-semibold mb-3">Plan de Suscripción</h3>
                  <RadioGroup
                    options={radioOptions}
                    value={radioValue}
                    onChange={setRadioValue}
                    layout="vertical"
                  />
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-3">Características Adicionales</h3>
                  <CheckboxGroup
                    options={checkboxOptions}
                    value={checkboxValues}
                    onChange={setCheckboxValues}
                  />
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-3">Configuración</h3>
                  <div className="space-y-4">
                    <AnimatedSwitch
                      label="Activar modo oscuro"
                      checked={switchValue}
                      onChange={setSwitchValue}
                    />
                    
                    <div>
                      <p className="text-sm font-medium mb-2">Nivel de precisión: {sliderValue}%</p>
                      <AnimatedSlider
                        value={sliderValue}
                        onChange={setSliderValue}
                        marks={{
                          0: 'Bajo',
                          50: 'Medio',
                          100: 'Alto'
                        }}
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-3">Cargar Archivo</h3>
                  <UploadArea
                    accept=".mol,.sdf,.pdb"
                    onUpload={(files) => {
                      console.log('Files uploaded:', files);
                      message.success(`Archivo ${files[0].name} cargado`);
                    }}
                  />
                </div>
              </div>

              <FormActions
                onSubmit={handleFormSubmit}
                onCancel={() => form.resetFields()}
                submitText="Enviar Formulario"
                cancelText="Limpiar"
              />
            </Form>
          </Card>
        </AnimatedDiv>
      )
    },
    {
      key: '3',
      label: 'Componentes UI',
      children: (
        <AnimatedDiv animation="fadeInRight" className="space-y-8">
          {/* Botones */}
          <Card title="Botones" size="small">
            <div className="flex flex-wrap gap-3">
              <Button variant="primary">Primario</Button>
              <Button variant="secondary">Secundario</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="danger">Peligro</Button>
              <Button variant="success">Éxito</Button>
              <Button variant="primary" loading>Cargando</Button>
              <Button variant="primary" disabled>Deshabilitado</Button>
            </div>
          </Card>

          {/* Alertas */}
          <Card title="Alertas" size="small">
            <div className="space-y-3">
              <Alert type="info" message="Información importante" />
              <Alert type="success" message="Operación exitosa" />
              <Alert type="warning" message="Advertencia del sistema" />
              <Alert type="error" message="Error en el proceso" />
            </div>
          </Card>

          {/* Badges y Tags */}
          <Card title="Badges y Tags" size="small">
            <div className="space-y-4">
              <div className="flex gap-3">
                <Badge count={5}>
                  <Button>Notificaciones</Button>
                </Badge>
                <Badge count={99}>
                  <Button>Mensajes</Button>
                </Badge>
                <Badge count={1000} overflowCount={999}>
                  <Button>Actividad</Button>
                </Badge>
              </div>
              
              <div className="flex flex-wrap gap-2">
                <Tag color="blue">React</Tag>
                <Tag color="green">TypeScript</Tag>
                <Tag color="purple">Tailwind</Tag>
                <Tag color="orange">Ant Design</Tag>
                <Tag color="pink">Framer Motion</Tag>
              </div>
            </div>
          </Card>

          {/* Modal */}
          <Card title="Modal" size="small">
            <Button onClick={() => setShowModal(true)}>
              Abrir Modal de Ejemplo
            </Button>
            
            <Modal
              open={showModal}
              onClose={() => setShowModal(false)}
              title="Modal con Animaciones"
              footer={
                <div className="flex gap-2 justify-end">
                  <Button variant="outline" onClick={() => setShowModal(false)}>
                    Cancelar
                  </Button>
                  <Button variant="primary" onClick={() => {
                    setShowModal(false);
                    message.success('Acción confirmada!');
                  }}>
                    Confirmar
                  </Button>
                </div>
              }
            >
              <p className="text-gray-600">
                Este es un modal mejorado con animaciones de Framer Motion 
                y estilos de Tailwind CSS integrados con Ant Design.
              </p>
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <p className="text-sm">
                  Las animaciones fluidas mejoran la experiencia del usuario
                  y hacen que la interfaz se sienta más responsiva y moderna.
                </p>
              </div>
            </Modal>
          </Card>

          {/* Tooltips */}
          <Card title="Tooltips" size="small">
            <div className="flex gap-4">
              <Tooltip title="Información adicional">
                <Button variant="outline">Hover aquí</Button>
              </Tooltip>
              <Tooltip title="Acción peligrosa" placement="top">
                <Button variant="danger">Eliminar</Button>
              </Tooltip>
              <Tooltip title="Guardado automático activado" placement="right">
                <Button variant="success">Guardar</Button>
              </Tooltip>
            </div>
          </Card>
        </AnimatedDiv>
      )
    }
  ];

  return (
    <Container maxWidth="full" className="py-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            Sistema Híbrido ChemsTools
          </h1>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Demostración completa del sistema que combina Ant Design, Tailwind CSS y Framer Motion
            para crear una experiencia de usuario excepcional en aplicaciones químicas.
          </p>
        </motion.div>

        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={tabItems}
          size="large"
          className="demo-tabs"
        />
    </Container>
  );
}
