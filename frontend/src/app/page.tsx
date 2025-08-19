// frontend/src/app/page.tsx
'use client';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';

import PHCalculator from '@/components/features/PHCalculator';
import SolutionCalculator from '@/components/features/SolutionCalculator';


export default function Home() {
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  return (
    <main className="flex min-h-screen flex-col items-center p-6 md:p-12">
      <div className="w-full max-w-7xl">
        {isAuthenticated ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              
              <SolutionCalculator />
              
            </div>
            <div className="space-y-8">
              
              <PHCalculator />
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
              <h1 className="text-3xl font-bold mb-4 text-gray-900">Bienvenido a ChemsTools</h1>
              <p className="text-gray-600 mb-8">
                Herramientas químicas integradas para cálculos y visualización molecular
              </p>
              <div className="flex gap-4 justify-center">
                <a
                  href="/login"
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Iniciar Sesión
                </a>
                <a
                  href="/register"
                  className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Registrarse
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

