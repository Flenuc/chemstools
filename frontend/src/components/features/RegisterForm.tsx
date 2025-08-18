'use client';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Form, Input, Button, Alert, Progress, Tooltip } from 'antd';
import { UserOutlined, MailOutlined, LockOutlined, UserAddOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/services/api';
import { addNotification } from '@/store/notificationsSlice';

interface RegisterFormValues {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export default function RegisterForm() {
  const [form] = Form.useForm<RegisterFormValues>();
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<boolean>(false);
  const [loading, setLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const dispatch = useDispatch();

  const calculatePasswordStrength = (password: string): number => {
    let strength = 0;
    if (password.length >= 8) strength += 25;
    if (password.length >= 12) strength += 25;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 25;
    if (/\d/.test(password)) strength += 12.5;
    if (/[^a-zA-Z\d]/.test(password)) strength += 12.5;
    return strength;
  };

  // Función para manejar cambios en el campo de contraseña
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPassword = e.target.value;
    setPasswordStrength(calculatePasswordStrength(newPassword));
    
    // Forzar revalidación del campo confirmPassword cuando cambia la contraseña
    setTimeout(() => {
      const confirmValue = form.getFieldValue('confirmPassword');
      if (confirmValue) {
        form.validateFields(['confirmPassword']);
      }
    }, 0);
  };

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
    console.log('Iniciando registro con valores:', values);
    setError('');
    setLoading(true);
    
    try {
      // Eliminar confirmPassword antes de enviar al backend
      const { confirmPassword, ...registerData } = values;
      console.log('Enviando datos de registro:', registerData);
      
      const response = await api.post('auth/register/', registerData);
      console.log('Respuesta del servidor:', response);
      
      dispatch(addNotification({ 
        message: '¡Usuario registrado con éxito! Ahora puedes iniciar sesión.', 
        type: 'success' 
      }));
      
      setSuccess(true);
      form.resetFields();
      setPasswordStrength(0);
      
      // Redirect to login after 2 seconds
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
    } catch (err: any) {
      console.error('Error en registro:', err);
      
      // Manejar diferentes tipos de errores
      let errorMessage = 'Error al registrar el usuario';
      
      if (err.response?.data) {
        // Errores del backend
        const data = err.response.data;
        if (typeof data === 'object') {
          // Si hay errores específicos por campo
          if (data.username) errorMessage = data.username[0];
          else if (data.email) errorMessage = data.email[0];
          else if (data.password) errorMessage = data.password[0];
          else if (data.detail) errorMessage = data.detail;
          else if (data.message) errorMessage = data.message;
        } else {
          errorMessage = String(data);
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
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
          name="register"
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
              label="Nombre de Usuario"
              rules={[
                { required: true, message: 'Por favor ingresa un nombre de usuario' },
                { min: 3, message: 'El usuario debe tener al menos 3 caracteres' },
                { max: 20, message: 'El usuario no puede tener más de 20 caracteres' },
                { pattern: /^[a-zA-Z0-9_]+$/, message: 'Solo se permiten letras, números y guiones bajos' }
              ]}
            >
              <Input
                prefix={<UserOutlined className="text-gray-400" />}
                placeholder="Elige un nombre de usuario"
                size="large"
                className="rounded-lg hover:border-purple-400 focus:border-purple-500 transition-colors"
              />
            </Form.Item>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Form.Item
              name="email"
              label="Correo Electrónico"
              rules={[
                { required: true, message: 'Por favor ingresa tu correo electrónico' },
                { type: 'email', message: 'Por favor ingresa un correo válido' }
              ]}
            >
              <Input
                prefix={<MailOutlined className="text-gray-400" />}
                placeholder="tu@correo.com"
                size="large"
                className="rounded-lg hover:border-purple-400 focus:border-purple-500 transition-colors"
              />
            </Form.Item>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Form.Item
              name="password"
              label="Contraseña"
              hasFeedback
              rules={[
                { required: true, message: 'Por favor ingresa una contraseña' },
                { min: 8, message: 'La contraseña debe tener al menos 8 caracteres' }
              ]}
            >
              <Tooltip title="Usa mayúsculas, minúsculas, números y símbolos para una contraseña más segura">
                <Input.Password
                  prefix={<LockOutlined className="text-gray-400" />}
                  placeholder="Crea una contraseña segura"
                  size="large"
                  className="rounded-lg hover:border-purple-400 focus:border-purple-500 transition-colors"
                  onChange={handlePasswordChange}
                />
              </Tooltip>
            </Form.Item>
            {passwordStrength > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mt-2"
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
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Form.Item
              name="confirmPassword"
              label="Confirmar Contraseña"
              dependencies={['password']}
              hasFeedback
              validateFirst
              rules={[
                { 
                  required: true, 
                  message: 'Por favor confirma tu contraseña' 
                },
                ({ getFieldValue }) => ({
                  validator(rule, value) {
                    if (!value) {
                      return Promise.resolve();
                    }
                    
                    const password = getFieldValue('password');
                    
                    // Comparación directa sin trim ni modificaciones
                    if (value === password) {
                      return Promise.resolve();
                    }
                    
                    return Promise.reject(new Error('Las contraseñas no coinciden'));
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined className="text-gray-400" />}
                placeholder="Confirma tu contraseña"
                size="large"
                className="rounded-lg hover:border-purple-400 focus:border-purple-500 transition-colors"
                autoComplete="new-password"
              />
            </Form.Item>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="pt-2"
          >
            <Form.Item className="mb-0">
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                size="large"
                icon={<UserAddOutlined />}
                disabled={success}
                className="w-full h-12 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 border-0 text-white font-medium text-base hover:from-purple-700 hover:to-pink-700 transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                {loading ? 'Registrando...' : 'Crear Cuenta'}
              </Button>
            </Form.Item>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
            className="text-center pt-4"
          >
            <p className="text-sm text-gray-600">
              ¿Ya tienes una cuenta?{' '}
              <a href="/login" className="text-purple-600 hover:text-purple-700 font-medium transition-colors">
                Inicia sesión
              </a>
            </p>
          </motion.div>
        </Form>
      </div>
    </motion.div>
  );
}
