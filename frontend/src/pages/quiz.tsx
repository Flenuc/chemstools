import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';
import QuizGame from '@/components/features/quiz/QuizGame';
import QuizLeaderboard from '@/components/features/quiz/QuizLeaderboard';

const QuizPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'game' | 'leaderboard'>('game');
  const { gameState } = useSelector((state: RootState) => state.quiz);

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