'use client';

import RegisterFormFixed from '@/components/features/RegisterFormFixed';
import { ConfigProvider } from 'antd';
import { theme } from '@/lib/theme';

export default function RegisterPage() {
  return (
    <ConfigProvider theme={theme}>
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50 flex items-center justify-center p-4">
        <RegisterFormFixed />
      </div>
    </ConfigProvider>
  );
}
