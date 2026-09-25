'use client';

import RegisterFormDebug from '@/components/features/RegisterFormDebug';
import RegisterForm from '@/components/features/RegisterForm';
import { Provider } from 'react-redux';
import { store } from '@/store';
import { ConfigProvider } from 'antd';
import { theme } from '@/lib/theme';
import { useState } from 'react';

export default function RegisterDebugPage() {
  const [showDebug, setShowDebug] = useState(true);

  return (
    <Provider store={store}>
      <ConfigProvider theme={theme}>
        <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50 p-4">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-6">
              <button
                onClick={() => setShowDebug(!showDebug)}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
              >
                {showDebug ? 'Ver Formulario Normal' : 'Ver Formulario Debug'}
              </button>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-bold mb-4 text-center">
                  {showDebug ? 'Formulario Debug (Con logs)' : 'Formulario Normal'}
                </h3>
                {showDebug ? <RegisterFormDebug /> : <RegisterForm />}
              </div>
              
              <div>
                <h3 className="text-lg font-bold mb-4 text-center">
                  Formulario Original (Migrado)
                </h3>
                <RegisterForm />
              </div>
            </div>
            
            <div className="mt-8 p-4 bg-white rounded-lg shadow">
              <h3 className="font-bold mb-2">Notas sobre el problema:</h3>
              <ul className="list-disc list-inside space-y-1 text-sm">
                <li>El warning de React 19 con Ant Design v5 es solo una advertencia, no afecta la funcionalidad</li>
                <li>El problema de validación puede estar relacionado con el timing de la validación</li>
                <li>Usa el formulario de debug para ver los valores exactos en la consola</li>
                <li>Compara el comportamiento entre ambos formularios</li>
              </ul>
            </div>
          </div>
        </div>
      </ConfigProvider>
    </Provider>
  );
}
