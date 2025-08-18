'use client';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useRouter } from 'next/navigation';
import { Form, Input, Button, Alert, Space } from 'antd';
import { UserOutlined, LockOutlined, LoginOutlined } from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';
import { setTokens, setUser } from '@/store/authSlice';
import { api } from '@/services/api';
import { addNotification } from '@/store/notificationsSlice';

interface LoginFormValues {
  username: string;
  password: string;
}

export default function LoginForm() {
  const [form] = Form.useForm<LoginFormValues>();
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch();
  const router = useRouter();

  const handleSubmit = async (values: LoginFormValues) => {
    setError('');
    setLoading(true);
    
    try {
      // Request authentication token
      const tokenData = await api.post('auth/token/', values);
      dispatch(setTokens(tokenData));

      // Get user data
      const userData = await api.get('auth/me/', {
        headers: { Authorization: `Bearer ${tokenData.access}` },
      });
      
      dispatch(setUser(userData));
      
      // Mostrar notificación de éxito
      dispatch(addNotification({ 
        message: '¡Bienvenido a ChemsTools!', 
        type: 'success' 
      }));
      
      // Clear form on success
      form.resetFields();
      
      // Redirigir a la página principal
      router.push('/');
    } catch (err: any) {
      setError(err.message || 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-md mx-auto"
    >
      <div className="bg-white/95 backdrop-blur-sm p-8 rounded-2xl shadow-xl border border-gray-100">
        <motion.div
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
          className="text-center mb-8"
        >
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Iniciar Sesión
          </h2>
          <p className="text-gray-500 mt-2">Bienvenido a ChemsTools</p>
        </motion.div>

        <AnimatePresence mode="wait">
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="mb-4"
            >
              <Alert
                message={error}
                type="error"
                showIcon
                closable
                onClose={() => setError('')}
                className="rounded-lg"
              />
            </motion.div>
          )}
        </AnimatePresence>

        <Form
          form={form}
          name="login"
          onFinish={handleSubmit}
          autoComplete="off"
          layout="vertical"
          requiredMark={false}
          className="space-y-4"
        >
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Form.Item
              name="username"
              label="Usuario"
              rules={[
                { required: true, message: 'Por favor ingresa tu usuario' },
                { min: 3, message: 'El usuario debe tener al menos 3 caracteres' }
              ]}
            >
              <Input
                prefix={<UserOutlined className="text-gray-400" />}
                placeholder="Ingresa tu usuario"
                size="large"
                className="rounded-lg hover:border-blue-400 focus:border-blue-500 transition-colors"
              />
            </Form.Item>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Form.Item
              name="password"
              label="Contraseña"
              rules={[
                { required: true, message: 'Por favor ingresa tu contraseña' },
                { min: 6, message: 'La contraseña debe tener al menos 6 caracteres' }
              ]}
            >
              <Input.Password
                prefix={<LockOutlined className="text-gray-400" />}
                placeholder="Ingresa tu contraseña"
                size="large"
                className="rounded-lg hover:border-blue-400 focus:border-blue-500 transition-colors"
              />
            </Form.Item>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="pt-2"
          >
            <Form.Item className="mb-0">
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                size="large"
                icon={<LoginOutlined />}
                className="w-full h-12 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 border-0 text-white font-medium text-base hover:from-blue-700 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
              </Button>
            </Form.Item>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-center pt-4"
          >
            <Space split="·" className="text-sm">
              <a href="#" className="text-blue-600 hover:text-blue-700 transition-colors">
                ¿Olvidaste tu contraseña?
              </a>
              <a href="/register" className="text-blue-600 hover:text-blue-700 transition-colors">
                Crear cuenta
              </a>
            </Space>
          </motion.div>
        </Form>
      </div>
    </motion.div>
  );
}
