import React from 'react';
import ReactionSimulator from '@/components/features/ReactionSimulator';

export default function SimulatorPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8">
        <ReactionSimulator />
      </div>
    </div>
  );
}

// Metadata para SEO (App Router)
export const metadata = {
  title: 'Simulador de Reacciones Químicas | ChemTools',
  description: 'Balancea ecuaciones químicas automáticamente con nuestro simulador avanzado',
};