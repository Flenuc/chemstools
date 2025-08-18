'use client';
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { motion } from 'framer-motion';
import { message } from 'antd';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { setTokens, setUser } from '@/store/authSlice';
import { api } from '@/services/api';
import { logTelemetryEvent } from '@/services/telemetryService';
import { Form, FormItem, Input, FormActions, validateMessages } from '@/components/ui/forms';
import { Card, Alert, Button } from '@/components/ui';
import { AnimatedDiv } from '@/lib/animations';

export default function LoginFormEnhanced() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const dispatch = useDispatch();

  const handleSubmit = async () => {
    try {
      setError('');
      setLoading(true);
      
      const values = await form.validateFields();
      const { username, password } = values;
      
      // Animación de inicio
      message.loading('Iniciando sesión...', 0);
      
      const tokenData = await api.post('auth/token/', { username, password });
      dispatch(setTokens(tokenData));

      const userData = await api.get('auth/me/', {
        headers: { Authorization: `Bearer ${tokenData.access}` },
      });
      
      logTelemetryEvent('login_success', { username });
      dispatch(setUser(userData));
      
      message.destroy();
      message.success('¡Bienvenido de vuelta!');
      
    } catch (err: any) {
      message.destroy();
      const errorMessage = err.message || 'Error al iniciar sesión';
      setError(errorMessage);
      logTelemetryEvent('login_failed', { error: errorMessage });
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatedDiv animation="fadeInUp" className="w-full max-w-md mx-auto">
      <Card className="shadow-2xl">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 200, damping: 20 }}
          className="flex justify-center mb-6"
        >
          <div className="w-20 h-20 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center">
            <LockOutlined className="text-white text-3xl" />
          </div>
        </motion.div>

        <motion.h2 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-2xl font-bold text-center mb-6 bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent"
        >
          Iniciar Sesión
        </motion.h2>

        {error && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="mb-4"
          >
            <Alert type="error" message={error} closable onClose={() => setError('')} />
          </motion.div>
        )}

        <Form
          form={form}
          layout="vertical"
          validateMessages={validateMessages}
          onFinish={handleSubmit}
        >
          <FormItem
            label="Usuario"
            name="username"
            rules={[
              { required: true, message: 'Por favor ingresa tu usuario' },
              { min: 3, message: 'El usuario debe tener al menos 3 caracteres' }
            ]}
            animation="slideIn"
            delay={0.3}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Ingresa tu usuario"
              size="large"
              disabled={loading}
            />
          </FormItem>

          <FormItem
            label="Contraseña"
            name="password"
            rules={[
              { required: true, message: 'Por favor ingresa tu contraseña' },
              { min: 6, message: 'La contraseña debe tener al menos 6 caracteres' }
            ]}
            animation="slideIn"
            delay={0.4}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Ingresa tu contraseña"
              size="large"
              disabled={loading}
            />
          </FormItem>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="space-y-4"
          >
            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={loading}
              className="w-full"
            >
              {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
            </Button>

            <div className="flex items-center justify-between text-sm">
              <motion.a
                href="/forgot-password"
                className="text-primary-600 hover:text-primary-700 transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                ¿Olvidaste tu contraseña?
              </motion.a>
              
              <motion.a
                href="/register"
                className="text-primary-600 hover:text-primary-700 transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Crear cuenta
              </motion.a>
            </div>
          </motion.div>
        </Form>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-6 pt-6 border-t border-gray-200"
        >
          <p className="text-center text-sm text-gray-600">
            Al iniciar sesión, aceptas nuestros{' '}
            <a href="/terms" className="text-primary-600 hover:underline">
              Términos de Servicio
            </a>{' '}
            y{' '}
            <a href="/privacy" className="text-primary-600 hover:underline">
              Política de Privacidad
            </a>
          </p>
        </motion.div>
      </Card>
    </AnimatedDiv>
  );
}
