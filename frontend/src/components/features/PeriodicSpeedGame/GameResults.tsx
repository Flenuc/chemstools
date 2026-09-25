'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, Clock, Trophy, RefreshCw, Home, Share2, TrendingUp } from 'lucide-react';
import confetti from 'canvas-confetti';

interface Element {
  number: number;
  symbol: string;
  name: string;
  category?: string;
}

interface GameResult {
  is_correct: boolean;
  target_element: Element;
  selected_element: Element;
  time_taken: number;
  message: string;
}

interface Stats {
  games_played: number;
  games_correct: number;
  accuracy_rate: number;
  best_time_seconds?: number;
  current_streak: number;
  best_streak: number;
}

interface GameResultsProps {
  result: GameResult;
  timeElapsed: number;
  hintUsed: boolean;
  stats: Stats | null;
  onPlayAgain: () => void;
  onMainMenu: () => void;
}

const GameResults: React.FC<GameResultsProps> = ({
  result,
  timeElapsed,
  hintUsed,
  stats,
  onPlayAgain,
  onMainMenu
}) => {
  // Trigger confetti for correct answer
  React.useEffect(() => {
    if (result.is_correct) {
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 }
      });
    }
  }, [result.is_correct]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(2);
    return mins > 0 ? `${mins}:${secs.padStart(5, '0')}` : `${secs}s`;
  };

  const getPerformanceRating = () => {
    if (!result.is_correct) return { rating: 'Intenta de nuevo', stars: 0, color: 'text-gray-500' };
    
    if (timeElapsed < 5) return { rating: '¡Increíble!', stars: 3, color: 'text-yellow-500' };
    if (timeElapsed < 10) return { rating: '¡Excelente!', stars: 2, color: 'text-green-500' };
    if (timeElapsed < 20) return { rating: '¡Bien hecho!', stars: 1, color: 'text-blue-500' };
    return { rating: 'Completado', stars: 1, color: 'text-gray-600' };
  };

  const performance = getPerformanceRating();

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-4 flex items-center justify-center">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-white rounded-2xl shadow-2xl p-8 max-w-2xl w-full"
      >
        {/* Result Header */}
        <div className="text-center mb-6">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200 }}
            className="inline-flex items-center justify-center w-24 h-24 rounded-full mb-4"
          >
            {result.is_correct ? (
              <CheckCircle className="w-24 h-24 text-green-500" />
            ) : (
              <XCircle className="w-24 h-24 text-red-500" />
            )}
          </motion.div>

          <h1 className={`text-3xl font-bold mb-2 ${result.is_correct ? 'text-green-600' : 'text-red-600'}`}>
            {result.is_correct ? '¡Correcto!' : 'Incorrecto'}
          </h1>

          <p className={`text-xl ${performance.color} font-semibold`}>
            {performance.rating}
          </p>

          {/* Stars */}
          <div className="flex justify-center gap-1 mt-2">
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, rotate: -180 }}
                animate={{ 
                  opacity: i < performance.stars ? 1 : 0.3,
                  rotate: 0
                }}
                transition={{ delay: i * 0.2 }}
              >
                <Trophy className={`w-8 h-8 ${i < performance.stars ? 'text-yellow-400' : 'text-gray-300'}`} />
              </motion.div>
            ))}
          </div>
        </div>

        {/* Elements Comparison */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Target Element */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4">
            <div className="text-sm text-blue-600 font-semibold mb-2">Elemento Objetivo</div>
            <div className="flex items-center gap-3">
              <div className="bg-blue-500 text-white rounded-lg p-3 text-2xl font-bold">
                {result.target_element.symbol}
              </div>
              <div>
                <div className="font-semibold text-gray-800">{result.target_element.name}</div>
                <div className="text-sm text-gray-600">Z = {result.target_element.number}</div>
              </div>
            </div>
          </div>

          {/* Selected Element */}
          <div className={`bg-gradient-to-br ${result.is_correct ? 'from-green-50 to-green-100' : 'from-red-50 to-red-100'} rounded-xl p-4`}>
            <div className={`text-sm ${result.is_correct ? 'text-green-600' : 'text-red-600'} font-semibold mb-2`}>
              Tu Selección
            </div>
            <div className="flex items-center gap-3">
              <div className={`${result.is_correct ? 'bg-green-500' : 'bg-red-500'} text-white rounded-lg p-3 text-2xl font-bold`}>
                {result.selected_element.symbol}
              </div>
              <div>
                <div className="font-semibold text-gray-800">{result.selected_element.name}</div>
                <div className="text-sm text-gray-600">Z = {result.selected_element.number}</div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Summary */}
        <div className="bg-gray-50 rounded-xl p-4 mb-6">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="flex items-center justify-center gap-2 text-gray-600 mb-1">
                <Clock className="w-4 h-4" />
                <span className="text-sm">Tiempo</span>
              </div>
              <div className="text-xl font-bold text-gray-800">
                {formatTime(timeElapsed)}
              </div>
            </div>
            
            <div>
              <div className="flex items-center justify-center gap-2 text-gray-600 mb-1">
                <TrendingUp className="w-4 h-4" />
                <span className="text-sm">Racha</span>
              </div>
              <div className="text-xl font-bold text-gray-800">
                🔥 {stats?.current_streak || 0}
              </div>
            </div>

            <div>
              <div className="flex items-center justify-center gap-2 text-gray-600 mb-1">
                <Trophy className="w-4 h-4" />
                <span className="text-sm">Precisión</span>
              </div>
              <div className="text-xl font-bold text-gray-800">
                {stats?.accuracy_rate.toFixed(0) || 0}%
              </div>
            </div>
          </div>

          {hintUsed && (
            <div className="mt-3 text-center text-sm text-yellow-600 bg-yellow-50 rounded-lg p-2">
              💡 Pista utilizada
            </div>
          )}
        </div>

        {/* New Records */}
        {result.is_correct && stats && (
          <>
            {stats.best_time_seconds === timeElapsed && timeElapsed < 100 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white rounded-lg p-3 mb-4 text-center"
              >
                🏆 ¡Nuevo récord de tiempo!
              </motion.div>
            )}
            {stats.current_streak === stats.best_streak && stats.current_streak > 1 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gradient-to-r from-purple-400 to-pink-500 text-white rounded-lg p-3 mb-4 text-center"
              >
                🔥 ¡Nueva mejor racha!
              </motion.div>
            )}
          </>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onPlayAgain}
            className="flex-1 bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center justify-center gap-2"
          >
            <RefreshCw className="w-5 h-5" />
            Jugar de Nuevo
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onMainMenu}
            className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-xl font-semibold hover:bg-gray-300 transition-all flex items-center justify-center gap-2"
          >
            <Home className="w-5 h-5" />
            Menú Principal
          </motion.button>
        </div>

        {/* Share Button */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => {
            const text = result.is_correct 
              ? `¡Encontré ${result.target_element.name} en ${formatTime(timeElapsed)} en Tabla Periódica Rápida! 🎯`
              : `Intenté encontrar ${result.target_element.name} en Tabla Periódica Rápida 🧪`;
            
            if (navigator.share) {
              navigator.share({
                title: 'Tabla Periódica Rápida',
                text: text
              });
            }
          }}
          className="w-full mt-3 py-2 text-gray-600 hover:text-gray-800 transition-colors flex items-center justify-center gap-2"
        >
          <Share2 className="w-4 h-4" />
          Compartir Resultado
        </motion.button>
      </motion.div>
    </div>
  );
};

export default GameResults;
