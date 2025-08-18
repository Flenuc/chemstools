'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import MemoryGame from '@/components/features/games/MemoryGame';
import MemoryGameStats from '@/components/features/games/MemoryGameStats';


const MemoryPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'game' | 'stats'>('game');
  const router = useRouter();

  const handleGameComplete = (score: number, time: number) => {
    console.log(`Game completed! Score: ${score}, Time: ${time}s`);
    // Optionally show a celebration or automatically switch to stats
    setTimeout(() => {
      setActiveTab('stats');
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 py-8">
      
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            🧠 Memory Molecular
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Desafía tu memoria emparejando nombres de compuestos químicos con sus fórmulas
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="max-w-md mx-auto mb-8">
          <div className="flex bg-white rounded-lg shadow-md overflow-hidden">
            <button
              onClick={() => setActiveTab('game')}
              className={`flex-1 py-3 px-6 font-medium transition-all duration-200 ${
                activeTab === 'game'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              🎮 Jugar
            </button>
            <button
              onClick={() => setActiveTab('stats')}
              className={`flex-1 py-3 px-6 font-medium transition-all duration-200 ${
                activeTab === 'stats'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              📊 Estadísticas
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="transition-all duration-300">
          {activeTab === 'game' && (
            <MemoryGame onGameComplete={handleGameComplete} />
          )}
          {activeTab === 'stats' && <MemoryGameStats />}
        </div>

        {/* Back Button */}
        <div className="text-center mt-8">
        </div>
      </div>
    </div>
  );
};

export default MemoryPage;