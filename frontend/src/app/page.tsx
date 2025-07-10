'use client';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';
import Header from '@/components/core/Header';
import LoginForm from '@/components/features/LoginForm';
import RegisterForm from '@/components/features/RegisterForm';
import MolecularWeightCalculator from '@/components/features/MolecularWeightCalculator';

export default function Home() {
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  return (
    <main className="flex min-h-screen flex-col items-center p-6 md:p-12 bg-gray-50">
      <Header />
      <div className="w-full max-w-4xl">
        {isAuthenticated ? (
          <div className="w-full max-w-2xl mx-auto">
            <MolecularWeightCalculator />
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-8">
            <LoginForm />
            <RegisterForm />
          </div>
        )}
      </div>
    </main>
  );
}
