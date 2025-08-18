'use client';
import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';
import ChemWordle from '@/components/features/chemwordle/ChemWordle';
import ChemWordleStats from '@/components/features/chemwordle/ChemWordleStats';

const ChemWordlePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'game' | 'stats'>('game');
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-100 to-blue-100 py-8">
        <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Acceso Requerido</h2>
            <p className="text-gray-600 mb-6">Debes iniciar sesión para jugar ChemWordle.</p>
            <a
              href="/"
              className="bg-purple-500 hover:bg-purple-600 text-white font-bold py-2 px-4 rounded transition-colors"
            >
              Ir al Login
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 to-blue-100 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Navigation Tabs */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-lg p-1 shadow-md">
            <button
              onClick={() => setActiveTab('game')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'game'
                  ? 'bg-purple-500 text-white'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              ⚗️ Jugar ChemWordle
            </button>
            <button
              onClick={() => setActiveTab('stats')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'stats'
                  ? 'bg-purple-500 text-white'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              📊 Estadísticas
            </button>
          </div>
        </div>

        {/* Content */}
        {activeTab === 'game' ? (
          <ChemWordle onComplete={() => setActiveTab('stats')} />
        ) : (
          <ChemWordleStats />
        )}
      </div>
    </div>
  );
};

export default ChemWordlePage;