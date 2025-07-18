// frontend/src/app/page.tsx
'use client';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';
import Header from '@/components/core/Header';
import LoginForm from '@/components/features/LoginForm';
import RegisterForm from '@/components/features/RegisterForm';
import MoleculeList from '@/components/features/MoleculeList';
import AddMoleculeForm from '@/components/features/AddMoleculeForm';
import MolarMassCalculator from '@/components/features/MolarMassCalculator';

export default function Home() {
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  return (
    <main className="flex min-h-screen flex-col items-center p-6 md:p-12 bg-gray-100">
      <Header />
      <div className="w-full max-w-7xl">
        {isAuthenticated ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <MoleculeList />
            </div>
            <div className="space-y-8">
              <AddMoleculeForm />
              <MolarMassCalculator />
            </div>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <LoginForm />
            <RegisterForm />
          </div>
        )}
      </div>
    </main>
  );
}

