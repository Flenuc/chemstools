'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { api } from '@/services/api';

interface MemoryStats {
  username: string;
  games_played: number;
  games_completed: number;
  completion_rate: number;
  best_time_easy: number | null;
  best_time_medium: number | null;
  best_time_hard: number | null;
  total_pairs_found: number;
  total_attempts: number;
  average_accuracy: number;
}

interface LeaderboardEntry {
  rank: number;
  username: string;
  games_played: number;
  completion_rate: number;
  average_accuracy: number;
  best_time_overall: number | null;
  total_pairs_found: number;
}

const MemoryGameStats: React.FC = () => {
  const [stats, setStats] = useState<MemoryStats | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'stats' | 'leaderboard'>('stats');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsData, leaderboardData] = await Promise.all([
        api.get('games/memory/stats/'),
        api.get('games/memory/leaderboard/')
      ]);

      if (statsData.success) {
        setStats(statsData.stats);
      }

      if (leaderboardData.success) {
        setLeaderboard(leaderboardData.leaderboard);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds: number | null) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getMedalIcon = (rank: number) => {
    switch (rank) {
      case 1: return '🥇';
      case 2: return '🥈';
      case 3: return '🥉';
      default: return `#${rank}`;
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">
            📊 Estadísticas Memory Molecular
          </h2>
          <p className="text-gray-600">
            Tu rendimiento en el juego de memoria química
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-lg mb-6">
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('stats')}
            className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
              activeTab === 'stats'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            📈 Mis Estadísticas
          </button>
          <button
            onClick={() => setActiveTab('leaderboard')}
            className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
              activeTab === 'leaderboard'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            🏆 Clasificación Global
          </button>
        </div>

        <div className="p-6">
          {activeTab === 'stats' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {stats ? (
                <div className="space-y-6">
                  {/* Overview Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-blue-800">
                        {stats.games_played}
                      </div>
                      <div className="text-sm text-blue-600">Partidas Jugadas</div>
                    </div>
                    
                    <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-green-800">
                        {stats.games_completed}
                      </div>
                      <div className="text-sm text-green-600">Partidas Completadas</div>
                    </div>
                    
                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-purple-800">
                        {stats.completion_rate.toFixed(1)}%
                      </div>
                      <div className="text-sm text-purple-600">Tasa de Finalización</div>
                    </div>
                    
                    <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-orange-800">
                        {stats.average_accuracy.toFixed(1)}%
                      </div>
                      <div className="text-sm text-orange-600">Precisión Promedio</div>
                    </div>
                  </div>

                  {/* Performance Details */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Best Times */}
                    <div className="bg-gray-50 p-6 rounded-lg">
                      <h3 className="text-lg font-semibold text-gray-800 mb-4">
                        ⏱️ Mejores Tiempos
                      </h3>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-green-600 font-medium">Fácil:</span>
                          <span className="font-semibold">
                            {formatTime(stats.best_time_easy)}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-yellow-600 font-medium">Medio:</span>
                          <span className="font-semibold">
                            {formatTime(stats.best_time_medium)}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-red-600 font-medium">Difícil:</span>
                          <span className="font-semibold">
                            {formatTime(stats.best_time_hard)}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Game Performance */}
                    <div className="bg-gray-50 p-6 rounded-lg">
                      <h3 className="text-lg font-semibold text-gray-800 mb-4">
                        🎯 Rendimiento General
                      </h3>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Pares Encontrados:</span>
                          <span className="font-semibold text-blue-600">
                            {stats.total_pairs_found}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Total Intentos:</span>
                          <span className="font-semibold text-purple-600">
                            {stats.total_attempts}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Ratio Éxito:</span>
                          <span className="font-semibold text-green-600">
                            {stats.total_attempts > 0 
                              ? (stats.total_pairs_found / stats.total_attempts * 100).toFixed(1)
                              : '0'
                            }%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Progress Visualization */}
                  <div className="bg-gray-50 p-6 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">
                      📊 Progreso Visual
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between text-sm text-gray-600 mb-1">
                          <span>Tasa de Finalización</span>
                          <span>{stats.completion_rate.toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className="bg-gradient-to-r from-blue-400 to-blue-600 h-3 rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(stats.completion_rate, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-sm text-gray-600 mb-1">
                          <span>Precisión Promedio</span>
                          <span>{stats.average_accuracy.toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className="bg-gradient-to-r from-green-400 to-green-600 h-3 rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(stats.average_accuracy, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🎮</div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-2">
                    ¡Aún no has jugado Memory Molecular!
                  </h3>
                  <p className="text-gray-600">
                    Juega tu primera partida para ver tus estadísticas aquí.
                  </p>
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'leaderboard' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-800">
                  🏆 Top 10 Jugadores
                </h3>
                <p className="text-sm text-gray-600">
                  Clasificación basada en tasa de finalización y precisión promedio
                </p>
              </div>

              {leaderboard.length > 0 ? (
                <div className="space-y-2">
                  {leaderboard.map((player, index) => (
                    <motion.div
                      key={player.username}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className={`
                        p-4 rounded-lg border transition-all duration-200 hover:shadow-md
                        ${player.rank <= 3 
                          ? 'bg-gradient-to-r from-yellow-50 to-yellow-100 border-yellow-200' 
                          : 'bg-white border-gray-200'
                        }
                      `}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="text-2xl font-bold">
                            {getMedalIcon(player.rank)}
                          </div>
                          <div>
                            <div className="font-semibold text-gray-800">
                              {player.username}
                            </div>
                            <div className="text-sm text-gray-600">
                              {player.games_played} partidas jugadas
                            </div>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-3 gap-4 text-center">
                          <div>
                            <div className="font-semibold text-green-600">
                              {player.completion_rate}%
                            </div>
                            <div className="text-xs text-gray-500">Finalización</div>
                          </div>
                          <div>
                            <div className="font-semibold text-blue-600">
                              {player.average_accuracy}%
                            </div>
                            <div className="text-xs text-gray-500">Precisión</div>
                          </div>
                          <div>
                            <div className="font-semibold text-purple-600">
                              {formatTime(player.best_time_overall)}
                            </div>
                            <div className="text-xs text-gray-500">Mejor Tiempo</div>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📈</div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-2">
                    No hay datos en la clasificación
                  </h3>
                  <p className="text-gray-600">
                    Sé el primero en aparecer jugando Memory Molecular.
                  </p>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>

      {/* Help Section */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          ❓ Cómo Funciona Memory Molecular
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-800 mb-2">🎯 Objetivo</h4>
            <p className="text-sm text-gray-600 mb-4">
              Encuentra todos los pares emparejando nombres de compuestos químicos 
              con sus fórmulas correspondientes.
            </p>
            
            <h4 className="font-medium text-gray-800 mb-2">🎮 Cómo Jugar</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Haz clic en las cartas para revelarlas</li>
              <li>• Las cartas moradas contienen nombres</li>
              <li>• Las cartas naranjas contienen fórmulas</li>
              <li>• Encuentra la pareja correcta para cada compuesto</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-800 mb-2">🏆 Puntuación</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Fácil: 100 puntos por par</li>
              <li>• Medio: 200 puntos por par</li>
              <li>• Difícil: 300 puntos por par</li>
            </ul>
            
            <h4 className="font-medium text-gray-800 mb-2 mt-4">📊 Estadísticas</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• <strong>Tasa de Finalización:</strong> % de partidas completadas</li>
              <li>• <strong>Precisión:</strong> % de intentos exitosos</li>
              <li>• <strong>Mejor Tiempo:</strong> Tu record por dificultad</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MemoryGameStats;