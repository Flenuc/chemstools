'use client';
import { useState } from 'react';
import { Form, Input, Button, Alert } from 'antd';
import { UserOutlined, MailOutlined, LockOutlined } from '@ant-design/icons';

export default function RegisterFormDebug() {
  const [form] = Form.useForm();
  const [debugInfo, setDebugInfo] = useState<string>('');

  const handleSubmit = async (values: any) => {
    console.log('Form values:', values);
    setDebugInfo(JSON.stringify(values, null, 2));
  };

  const customValidator = (rule: any, value: any) => {
    const password = form.getFieldValue('password');
    
    console.log('Validator called:');
    console.log('  Password field:', password);
    console.log('  Password type:', typeof password);
    console.log('  Password length:', password?.length);
    console.log('  Confirm field:', value);
    console.log('  Confirm type:', typeof value);
    console.log('  Confirm length:', value?.length);
    console.log('  Are equal?:', password === value);
    console.log('  Trimmed equal?:', password?.trim() === value?.trim());
    
    if (!value) {
      return Promise.resolve();
    }
    
    if (value === password) {
      console.log('✅ Passwords match!');
      return Promise.resolve();
    }
    
    console.log('❌ Passwords do NOT match');
    return Promise.reject(new Error(`Las contraseñas no coinciden. Password: "${password}", Confirm: "${value}"`));
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">Registro - Debug Mode</h2>
      
      <Form
        form={form}
        name="register_debug"
        onFinish={handleSubmit}
        layout="vertical"
        autoComplete="off"
      >
        <Form.Item
          name="username"
          label="Usuario"
          rules={[{ required: true, message: 'Requerido' }]}
        >
          <Input prefix={<UserOutlined />} placeholder="Usuario" />
        </Form.Item>

        <Form.Item
          name="email"
          label="Email"
          rules={[
            { required: true, message: 'Requerido' },
            { type: 'email', message: 'Email inválido' }
          ]}
        >
          <Input prefix={<MailOutlined />} placeholder="email@example.com" />
        </Form.Item>

        <Form.Item
          name="password"
          label="Contraseña"
          rules={[
            { required: true, message: 'Requerido' },
            { min: 8, message: 'Mínimo 8 caracteres' }
          ]}
        >
          <Input.Password 
            prefix={<LockOutlined />} 
            placeholder="Contraseña"
            onChange={(e) => {
              console.log('Password changed:', e.target.value);
              // Trigger validation of confirm field
              if (form.getFieldValue('confirmPassword')) {
                form.validateFields(['confirmPassword']);
              }
            }}
          />
        </Form.Item>

        <Form.Item
          name="confirmPassword"
          label="Confirmar Contraseña"
          dependencies={['password']}
          rules={[
            { required: true, message: 'Requerido' },
            { validator: customValidator }
          ]}
        >
          <Input.Password 
            prefix={<LockOutlined />} 
            placeholder="Confirmar contraseña"
            onChange={(e) => console.log('Confirm changed:', e.target.value)}
          />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" className="w-full">
            Registrar (Debug)
          </Button>
        </Form.Item>
      </Form>

      {debugInfo && (
        <Alert
          message="Valores del formulario"
          description={<pre className="text-xs">{debugInfo}</pre>}
          type="info"
          className="mt-4"
        />
      )}
      
      <div className="mt-4 p-3 bg-gray-100 rounded text-xs">
        <p className="font-bold">Instrucciones de debug:</p>
        <p>1. Abre la consola del navegador (F12)</p>
        <p>2. Ingresa los datos del formulario</p>
        <p>3. Revisa los logs en la consola</p>
      </div>
    </div>
  );
}
