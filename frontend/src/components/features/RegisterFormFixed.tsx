'use client';
import { useState, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { useRouter } from 'next/navigation';
import { Form, Input, Button, Alert, Progress } from 'antd';
import { UserOutlined, MailOutlined, LockOutlined, UserAddOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';
import { addNotification } from '@/store/notificationsSlice';
import { showMessage } from '@/hooks/useMessage';

interface RegisterFormValues {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export default function RegisterFormFixed() {
  const [form] = Form.useForm<RegisterFormValues>();
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<boolean>(false);
  const [loading, setLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const dispatch = useDispatch();
  const router = useRouter();

  const calculatePasswordStrength = (password: string): number => {
    let strength = 0;
    if (password.length >= 8) strength += 25;
    if (password.length >= 12) strength += 25;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 25;
    if (/\d/.test(password)) strength += 12.5;
    if (/[^a-zA-Z\d]/.test(password)) strength += 12.5;
    return strength;
  };

  const handlePasswordChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newPassword = e.target.value;
    setPasswordStrength(calculatePasswordStrength(newPassword));
  }, []);

  const getPasswordStrengthColor = (): string => {
    if (passwordStrength < 30) return '#ff4d4f';
    if (passwordStrength < 60) return '#faad14';
    if (passwordStrength < 80) return '#52c41a';
    return '#52c41a';
  };

  const getPasswordStrengthText = (): string => {
    if (passwordStrength < 30) return 'Débil';
    if (passwordStrength < 60) return 'Regular';
    if (passwordStrength < 80) return 'Buena';
    return 'Excelente';
  };

  const handleSubmit = async (values: RegisterFormValues) => {
    console.log('=== Iniciando registro ===');
    console.log('Valores del formulario:', {
      username: values.username,
      email: values.email,
      passwordLength: values.password.length,
      confirmPasswordLength: values.confirmPassword.length
    });

    setError('');
    setLoading(true);
    
    try {
      // Validación manual de contraseñas
      if (values.password !== values.confirmPassword) {
        throw new Error('Las contraseñas no coinciden');
      }

      // Preparar datos para enviar
      const registerData = {
        username: values.username,
        email: values.email,
        password: values.password
      };

      console.log('Enviando petición a /api/auth/register/');
      
      // Hacer la petición directamente con fetch
      const response = await fetch('/api/auth/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerData)
      });

      console.log('Respuesta recibida:', response.status);
      
      const data = await response.json();
      console.log('Datos de respuesta:', data);

      if (response.ok) {
        // Éxito
        showMessage.success('¡Usuario registrado con éxito!');
        dispatch(addNotification({ 
          message: '¡Usuario registrado con éxito! Redirigiendo al login...', 
          type: 'success' 
        }));
        
        setSuccess(true);
        form.resetFields();
        setPasswordStrength(0);
        
        // Redirigir al login después de 2 segundos
        setTimeout(() => {
          router.push('/login');
        }, 2000);
      } else {
        // Error del servidor
        let errorMessage = 'Error al registrar el usuario';
        
        if (data.username) {
          errorMessage = Array.isArray(data.username) ? data.username[0] : data.username;
        } else if (data.email) {
          errorMessage = Array.isArray(data.email) ? data.email[0] : data.email;
        } else if (data.password) {
          errorMessage = Array.isArray(data.password) ? data.password[0] : data.password;
        } else if (data.detail) {
          errorMessage = data.detail;
        } else if (data.message) {
          errorMessage = data.message;
        }
        
        throw new Error(errorMessage);
      }
    } catch (err: any) {
      console.error('Error en registro:', err);
      const errorMessage = err.message || 'Error al registrar el usuario';
      setError(errorMessage);
      showMessage.error(errorMessage);
      dispatch(addNotification({ 
        message: errorMessage, 
        type: 'error' 
      }));
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
          <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            Crear Cuenta
          </h2>
          <p className="text-gray-500 mt-2">Únete a la comunidad ChemsTools</p>
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
          
          {success && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ type: 'spring', stiffness: 200 }}
              className="mb-4"
            >
              <Alert
                message="¡Registro exitoso!"
                description="Redirigiendo al inicio de sesión..."
                type="success"
                showIcon
                icon={<CheckCircleOutlined />}
                className="rounded-lg"
              />
            </motion.div>
          )}
        </AnimatePresence>

        <Form
          form={form}
          name="registerFixed"
          onFinish={handleSubmit}
          autoComplete="off"
          layout="vertical"
          requiredMark={false}
        >
          <Form.Item
            name="username"
            label="Nombre de Usuario"
            rules={[
              { required: true, message: 'Por favor ingresa un nombre de usuario' },
              { min: 3, message: 'El usuario debe tener al menos 3 caracteres' },
              { max: 20, message: 'El usuario no puede tener más de 20 caracteres' },
              { pattern: /^[a-zA-Z0-9_]+$/, message: 'Solo se permiten letras, números y guiones bajos' }
            ]}
          >
            <Input
              id="username"
              prefix={<UserOutlined className="text-gray-400" />}
              placeholder="Elige un nombre de usuario"
              size="large"
              className="rounded-lg"
              autoComplete="username"
            />
          </Form.Item>

          <Form.Item
            name="email"
            label="Correo Electrónico"
            rules={[
              { required: true, message: 'Por favor ingresa tu correo electrónico' },
              { type: 'email', message: 'Por favor ingresa un correo válido' }
            ]}
          >
            <Input
              id="email"
              prefix={<MailOutlined className="text-gray-400" />}
              placeholder="tu@correo.com"
              size="large"
              className="rounded-lg"
              autoComplete="email"
            />
          </Form.Item>

          <Form.Item
            name="password"
            label="Contraseña"
            rules={[
              { required: true, message: 'Por favor ingresa una contraseña' },
              { min: 8, message: 'La contraseña debe tener al menos 8 caracteres' }
            ]}
          >
            <Input.Password
              id="password"
              prefix={<LockOutlined className="text-gray-400" />}
              placeholder="Crea una contraseña segura"
              size="large"
              className="rounded-lg"
              onChange={handlePasswordChange}
              autoComplete="new-password"
            />
          </Form.Item>
          
          {passwordStrength > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mb-4"
            >
              <div className="flex items-center gap-2">
                <Progress
                  percent={passwordStrength}
                  strokeColor={getPasswordStrengthColor()}
                  showInfo={false}
                  size="small"
                  className="flex-1"
                />
                <span className="text-xs font-medium" style={{ color: getPasswordStrengthColor() }}>
                  {getPasswordStrengthText()}
                </span>
              </div>
            </motion.div>
          )}

          <Form.Item
            name="confirmPassword"
            label="Confirmar Contraseña"
            dependencies={['password']}
            rules={[
              { 
                required: true, 
                message: 'Por favor confirma tu contraseña' 
              },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('Las contraseñas no coinciden'));
                },
              }),
            ]}
          >
            <Input.Password
              id="confirmPassword"
              prefix={<LockOutlined className="text-gray-400" />}
              placeholder="Confirma tu contraseña"
              size="large"
              className="rounded-lg"
              autoComplete="new-password"
            />
          </Form.Item>

          <Form.Item className="mb-0 mt-6">
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              size="large"
              icon={<UserAddOutlined />}
              disabled={success}
              className="w-full h-12 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 border-0 text-white font-medium text-base hover:from-purple-700 hover:to-pink-700 transition-all duration-300 shadow-lg hover:shadow-xl"
              style={{ background: success ? '#52c41a' : undefined }}
            >
              {loading ? 'Registrando...' : success ? '¡Registrado!' : 'Crear Cuenta'}
            </Button>
          </Form.Item>

          <div className="text-center pt-4">
            <p className="text-sm text-gray-600">
              ¿Ya tienes una cuenta?{' '}
              <a href="/login" className="text-purple-600 hover:text-purple-700 font-medium transition-colors">
                Inicia sesión
              </a>
            </p>
          </div>
        </Form>
      </div>
    </motion.div>
  );
}
