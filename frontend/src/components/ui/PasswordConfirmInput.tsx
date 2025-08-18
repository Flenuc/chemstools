'use client';

import { useState, useEffect } from 'react';
import { Input, Form } from 'antd';
import { LockOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import type { FormInstance } from 'antd';

interface PasswordConfirmInputProps {
  form: FormInstance;
  passwordFieldName?: string;
  confirmFieldName?: string;
}

export function PasswordConfirmInput({ 
  form, 
  passwordFieldName = 'password',
  confirmFieldName = 'confirmPassword' 
}: PasswordConfirmInputProps) {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isMatching, setIsMatching] = useState<boolean | null>(null);

  // Observar cambios en el campo de contraseña principal
  useEffect(() => {
    const subscription = form.getFieldValue(passwordFieldName);
    if (subscription !== password) {
      setPassword(subscription || '');
    }
  }, [form, passwordFieldName, password]);

  const handleConfirmChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setConfirmPassword(value);
    
    // Validar coincidencia
    if (value && password) {
      setIsMatching(value === password);
    } else {
      setIsMatching(null);
    }
  };

  const getSuffixIcon = () => {
    if (isMatching === null || !confirmPassword) return null;
    
    return isMatching ? (
      <CheckCircleOutlined style={{ color: '#52c41a' }} />
    ) : (
      <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
    );
  };

  return (
    <div className="relative">
      <Input.Password
        prefix={<LockOutlined className="text-gray-400" />}
        suffix={getSuffixIcon()}
        placeholder="Confirma tu contraseña"
        size="large"
        value={confirmPassword}
        onChange={handleConfirmChange}
        className="rounded-lg hover:border-purple-400 focus:border-purple-500 transition-colors"
        status={confirmPassword && !isMatching ? 'error' : undefined}
      />
      {confirmPassword && !isMatching && (
        <div className="text-red-500 text-xs mt-1">
          Las contraseñas no coinciden
        </div>
      )}
    </div>
  );
}
