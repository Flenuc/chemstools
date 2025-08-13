'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useDispatch } from 'react-redux';
import { addNotification } from '@/store/notificationsSlice';
import { api } from '@/services/api';
import PeriodicTable from './PeriodicTable';
import GameTimer from './GameTimer';
import ElementDisplay from './ElementDisplay';
import GameStats from './GameStats';
import GameResults from './GameResults';
import { Trophy, Zap, Clock, Target, Brain, ChevronRight } from 'lucide-react';

interface TargetElement {
  number: number;
  symbol: string;
  name: string;
  category?: string;
  atomic_mass?: number;
}

interface Game {
  id: number;
  target_element: TargetElement;
  is_completed: boolean;
  is_correct: boolean;
  time_taken_seconds?: number;
  hint_used: boolean;
  started_at: string;
}

interface GameResult {
  is_correct: boolean;
  target_element: TargetElement;
  selected_element: TargetElement;
  time_taken: number;
  message: string;
}

interface Stats {
  games_played: number;
  games_correct: number;
  accuracy_rate: number;
  best_time_seconds?: number;
  average_time_seconds: number;
  current_streak: number;
  best_streak: number;
}

const PeriodicSpeedGame: React.FC = () => {
  const dispatch = useDispatch();
  
  // Game state
  const [game, setGame] = useState<Game | null>(null);
  const [loading, setLoading] = useState(false);
  const [difficulty, setDifficulty] = useState<'random' | 'common' | 'rare'>('random');
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [gameStarted, setGameStarted] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [gameResult, setGameResult] = useState<GameResult | null>(null);
  const [hint, setHint] = useState<string | null>(null);
  const [showHint, setShowHint] = useState(false);
  
  // Stats state
  const [stats, setStats] = useState<Stats | null>(null);
  const [showStats, setShowStats] = useState(false);

  // Periodic table data
  const [periodicElements, setPeriodicElements] = useState<TargetElement[]>([]);

  // Load periodic table data on mount
  useEffect(() => {
    loadPeriodicTable();
    loadUserStats();
    checkCurrentGame();
  }, []);

  // Timer effect
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (game && !game.is_completed && gameStarted) {
      interval = setInterval(() => {
        setTimeElapsed(prev => prev + 0.1);
      }, 100);
    }
    return () => clearInterval(interval);
  }, [game, gameStarted]);

  // Load periodic table data
  const loadPeriodicTable = async () => {
    try {
      const data = await api.get('games/periodic-speed/periodic_table/');
      if (data.success) {
        setPeriodicElements(data.elements);
      }
    } catch (error) {
      console.error('Error loading periodic table:', error);
    }
  };

  // Load user stats
  const loadUserStats = async () => {
    try {
      const data = await api.get('games/periodic-speed/stats/');
      if (data.success) {
        setStats(data.stats);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  // Check for current game
  const checkCurrentGame = async () => {
    try {
      const data = await api.get('games/periodic-speed/current_challenge/');
      if (data.success && data.game) {
        setGame(data.game);
        setGameStarted(true);
        // Calculate elapsed time from start
        const startTime = new Date(data.game.started_at).getTime();
        const now = new Date().getTime();
        setTimeElapsed((now - startTime) / 1000);
      }
    } catch (error) {
      console.error('Error checking current game:', error);
    }
  };

  // Start new game
  const startNewGame = async () => {
    setLoading(true);
    setShowResult(false);
    setHint(null);
    setShowHint(false);
    
    try {
      const data = await api.post('games/periodic-speed/start_challenge/', {
        difficulty
      });

      if (data.success) {
        setGame(data.game);
        setGameStarted(true);
        setTimeElapsed(0);
        setGameResult(null);
        dispatch(addNotification({
          message: `Desafío iniciado - Encuentra: ${data.game.target_element.name}`,
          type: 'info'
        }));
      } else {
        const errorMessage = data.error || 'Error al iniciar el juego';
        dispatch(addNotification({
          message: errorMessage,
          type: 'error'
        }));
      }
    } catch (error) {
      dispatch(addNotification({
        message: 'Error al conectar con el servidor',
        type: 'error'
      }));
    } finally {
      setLoading(false);
    }
  };

  // Handle element selection
  const handleElementSelect = async (elementNumber: number) => {
    if (!game || game.is_completed || loading) return;

    setLoading(true);
    try {
      const data = await api.post('games/periodic-speed/submit_selection/', {
        game_id: game.id,
        selected_element_number: elementNumber,
        time_taken: timeElapsed
      });

      if (data.success) {
        setGame(data.game);
        setGameResult(data.result);
        setShowResult(true);
        
        const message = data.result.is_correct 
          ? `¡Correcto! ${data.result.target_element.name} en ${timeElapsed.toFixed(1)}s`
          : `Incorrecto. Era ${data.result.target_element.name}`;
        
        dispatch(addNotification({
          message,
          type: data.result.is_correct ? 'success' : 'error'
        }));
        
        // Reload stats after game completion
        await loadUserStats();
      } else {
        dispatch(addNotification({
          message: 'Error al procesar la selección',
          type: 'error'
        }));
      }
    } catch (error) {
      dispatch(addNotification({
        message: 'Error al enviar la selección',
        type: 'error'
      }));
    } finally {
      setLoading(false);
    }
  };

  // Get hint
  const requestHint = async () => {
    if (!game || game.is_completed || game.hint_used) return;

    setLoading(true);
    try {
      const data = await api.post('games/periodic-speed/get_hint/', {
        game_id: game.id
      });

      if (data.success) {
        setHint(data.hint);
        setShowHint(true);
        setGame(prev => prev ? { ...prev, hint_used: true } : null);
        dispatch(addNotification({
          message: 'Pista obtenida',
          type: 'info'
        }));
      } else {
        dispatch(addNotification({
          message: 'Error al obtener la pista',
          type: 'error'
        }));
      }
    } catch (error) {
      dispatch(addNotification({
        message: 'Error al obtener la pista',
        type: 'error'
      }));
    } finally {
      setLoading(false);
    }
  };

  // Play again
  const playAgain = () => {
    setShowResult(false);
    setGameResult(null);
    setHint(null);
    setShowHint(false);
    startNewGame();
  };

  // Difficulty settings
  const difficultyConfig = {
    random: {
      label: 'Todos los Elementos',
      color: 'bg-blue-500',
      icon: <Zap className="w-5 h-5" />,
      description: 'Cualquier elemento de la tabla periódica'
    },
    common: {
      label: 'Elementos Comunes',
      color: 'bg-green-500',
      icon: <Target className="w-5 h-5" />,
      description: 'Los elementos más conocidos'
    },
    rare: {
      label: 'Elementos Raros',
      color: 'bg-purple-500',
      icon: <Brain className="w-5 h-5" />,
      description: 'Lantánidos, actínidos y elementos pesados'
    }
  };

  // Main menu screen
  if (!gameStarted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-4">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-2xl p-8"
          >
            {/* Header */}
            <div className="text-center mb-8">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
                className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full mb-4"
              >
                <Zap className="w-10 h-10 text-white" />
              </motion.div>
              <h1 className="text-4xl font-bold text-gray-800 mb-2">
                ⚡ Tabla Periódica Rápida
              </h1>
              <p className="text-gray-600 text-lg">
                Encuentra el elemento lo más rápido posible
              </p>
            </div>

            {/* Stats Preview */}
            {stats && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
              >
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4">
                  <div className="text-2xl font-bold text-blue-600">
                    {stats.games_played}
                  </div>
                  <div className="text-sm text-blue-700">Partidas Jugadas</div>
                </div>
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4">
                  <div className="text-2xl font-bold text-green-600">
                    {stats.accuracy_rate.toFixed(1)}%
                  </div>
                  <div className="text-sm text-green-700">Precisión</div>
                </div>
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4">
                  <div className="text-2xl font-bold text-purple-600">
                    {stats.best_time_seconds ? `${stats.best_time_seconds.toFixed(1)}s` : 'N/A'}
                  </div>
                  <div className="text-sm text-purple-700">Mejor Tiempo</div>
                </div>
                <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4">
                  <div className="text-2xl font-bold text-orange-600">
                    🔥 {stats.current_streak}
                  </div>
                  <div className="text-sm text-orange-700">Racha Actual</div>
                </div>
              </motion.div>
            )}

            {/* Difficulty Selection */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-700 mb-4">
                Selecciona la Dificultad:
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(difficultyConfig).map(([key, config]) => (
                  <motion.button
                    key={key}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setDifficulty(key as typeof difficulty)}
                    className={`
                      relative p-6 rounded-xl border-2 transition-all
                      ${difficulty === key 
                        ? 'border-indigo-500 bg-indigo-50' 
                        : 'border-gray-200 bg-white hover:border-gray-300'
                      }
                    `}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className={`p-2 rounded-lg ${config.color} text-white`}>
                        {config.icon}
                      </div>
                      {difficulty === key && (
                        <div className="text-indigo-500">
                          <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            className="w-6 h-6 bg-indigo-500 rounded-full flex items-center justify-center"
                          >
                            <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          </motion.div>
                        </div>
                      )}
                    </div>
                    <div className="text-left">
                      <div className="font-semibold text-gray-800">{config.label}</div>
                      <div className="text-sm text-gray-600 mt-1">{config.description}</div>
                    </div>
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Start Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={startNewGame}
              disabled={loading}
              className="w-full py-4 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold text-lg rounded-xl shadow-lg hover:shadow-xl transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white" />
              ) : (
                <>
                  <Trophy className="w-6 h-6" />
                  Comenzar Desafío
                  <ChevronRight className="w-6 h-6" />
                </>
              )}
            </motion.button>

            {/* Toggle Stats Button */}
            <button
              onClick={() => setShowStats(!showStats)}
              className="w-full mt-4 py-3 text-gray-600 hover:text-gray-800 transition-colors"
            >
              {showStats ? 'Ocultar' : 'Ver'} Estadísticas Detalladas
            </button>

            {/* Detailed Stats */}
            <AnimatePresence>
              {showStats && stats && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-4"
                >
                  <GameStats stats={stats} />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    );
  }

  // Game Results Screen
  if (showResult && gameResult) {
    return (
      <GameResults
        result={gameResult}
        timeElapsed={timeElapsed}
        hintUsed={game?.hint_used || false}
        stats={stats}
        onPlayAgain={playAgain}
        onMainMenu={() => {
          setGameStarted(false);
          setShowResult(false);
          setGame(null);
        }}
      />
    );
  }

  // Active Game Screen
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Game Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-xl p-6 mb-6"
        >
          <div className="flex flex-col lg:flex-row items-center justify-between gap-4">
            {/* Target Element Display */}
            <div className="flex-1 w-full">
              {game && (
                <ElementDisplay 
                  element={game.target_element}
                  showHint={showHint}
                  hint={hint}
                />
              )}
            </div>

            {/* Timer and Actions */}
            <div className="flex items-center gap-4">
              <GameTimer 
                seconds={timeElapsed}
                isRunning={!game?.is_completed}
              />

              {/* Hint Button */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={requestHint}
                disabled={game?.hint_used || loading}
                className={`
                  px-6 py-3 rounded-xl font-semibold transition-all
                  ${game?.hint_used 
                    ? 'bg-gray-200 text-gray-500 cursor-not-allowed' 
                    : 'bg-gradient-to-r from-yellow-400 to-orange-500 text-white hover:shadow-lg'
                  }
                `}
              >
                {game?.hint_used ? '💡 Pista Usada' : '💡 Pedir Pista'}
              </motion.button>

              {/* Abandon Game */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={async () => {
                  if (confirm('¿Seguro que quieres abandonar el juego?')) {
                    try {
                      await api.delete('games/periodic-speed/end_challenge/');
                      setGameStarted(false);
                      setGame(null);
                    } catch (error) {
                      console.error('Error ending game:', error);
                    }
                  }
                }}
                className="px-6 py-3 bg-red-500 text-white rounded-xl font-semibold hover:bg-red-600 transition-colors"
              >
                Abandonar
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Periodic Table */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-2xl shadow-xl p-6"
        >
          <PeriodicTable
            elements={periodicElements}
            onElementClick={handleElementSelect}
            disabled={loading || game?.is_completed || false}
            targetElement={game?.target_element}
          />
        </motion.div>

        {/* Quick Stats Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-6 bg-white rounded-xl shadow-lg p-4"
        >
          <div className="flex justify-around text-center">
            <div>
              <div className="text-2xl font-bold text-gray-700">
                {stats?.games_played || 0}
              </div>
              <div className="text-sm text-gray-500">Partidas</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {stats?.accuracy_rate.toFixed(1) || 0}%
              </div>
              <div className="text-sm text-gray-500">Precisión</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {stats?.best_time_seconds ? `${stats.best_time_seconds.toFixed(1)}s` : 'N/A'}
              </div>
              <div className="text-sm text-gray-500">Mejor Tiempo</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-600">
                🔥 {stats?.current_streak || 0}
              </div>
              <div className="text-sm text-gray-500">Racha</div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default PeriodicSpeedGame;