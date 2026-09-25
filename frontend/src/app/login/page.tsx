'use client';

import LoginForm from '@/components/features/LoginForm';
import { ConfigProvider } from 'antd';
import { theme } from '@/lib/theme';
import { useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useRouter } from 'next/navigation';
import { RootState } from '@/store';

export default function LoginPage() {
  const router = useRouter();
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);

  useEffect(() => {
    // Si el usuario ya está autenticado, redirigir a la página principal
    if (isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  return (
    <ConfigProvider theme={theme}>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-4">
        <LoginForm />
      </div>
    </ConfigProvider>
  );
}
