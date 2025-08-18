'use client';
import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';
import QuizGame from '@/components/features/quiz/QuizGame';
import QuizLeaderboard from '@/components/features/quiz/QuizLeaderboard';


const QuizPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'game' | 'leaderboard'>('game');
  const { gameState } = useSelector((state: RootState) => state.quiz);
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-100 py-8">
        <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Acceso Requerido</h2>
            <p className="text-gray-600 mb-6">Debes iniciar sesión para acceder al quiz de química.</p>
            <a
              href="/"
              className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition-colors"
            >
              Ir al Login
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      
      <div className="max-w-6xl mx-auto px-4">
        {/* Navigation Tabs */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-lg p-1 shadow-md">
            <button
              onClick={() => setActiveTab('game')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'game'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              🎮 Jugar Quiz
            </button>
            <button
              onClick={() => setActiveTab('leaderboard')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'leaderboard'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              🏆 Clasificación
            </button>
          </div>
        </div>

        {/* Content */}
        {activeTab === 'game' ? (
          <QuizGame onComplete={() => setActiveTab('leaderboard')} />
        ) : (
          <QuizLeaderboard />
        )}
      </div>
    </div>
  );
};

export default QuizPage;