'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Award, Zap, Target, Clock, Trophy } from 'lucide-react';

interface Stats {
  games_played: number;
  games_correct: number;
  accuracy_rate: number;
  best_time_seconds?: number;
  average_time_seconds: number;
  current_streak: number;
  best_streak: number;
}

interface GameStatsProps {
  stats: Stats;
}

const GameStats: React.FC<GameStatsProps> = ({ stats }) => {
  const statCards = [
    {
      icon: <Trophy className="w-6 h-6" />,
      label: 'Partidas Jugadas',
      value: stats.games_played,
      color: 'from-blue-400 to-blue-600',
      format: (v: number) => v.toString()
    },
    {
      icon: <Target className="w-6 h-6" />,
      label: 'Aciertos',
      value: stats.games_correct,
      color: 'from-green-400 to-green-600',
      format: (v: number) => v.toString()
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      label: 'Precisión',
      value: stats.accuracy_rate,
      color: 'from-purple-400 to-purple-600',
      format: (v: number) => `${v.toFixed(1)}%`
    },
    {
      icon: <Clock className="w-6 h-6" />,
      label: 'Mejor Tiempo',
      value: stats.best_time_seconds || 0,
      color: 'from-yellow-400 to-yellow-600',
      format: (v: number) => v ? `${v.toFixed(1)}s` : 'N/A'
    },
    {
      icon: <Zap className="w-6 h-6" />,
      label: 'Tiempo Promedio',
      value: stats.average_time_seconds,
      color: 'from-orange-400 to-orange-600',
      format: (v: number) => `${v.toFixed(1)}s`
    },
    {
      icon: <Award className="w-6 h-6" />,
      label: 'Mejor Racha',
      value: stats.best_streak,
      color: 'from-red-400 to-red-600',
      format: (v: number) => `🔥 ${v}`
    }
  ];

  return (
    <div className="w-full">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {statCards.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="relative overflow-hidden"
          >
            <div className={`bg-gradient-to-br ${stat.color} rounded-xl p-4 shadow-lg`}>
              <div className="flex items-start justify-between mb-2">
                <div className="text-white/90">
                  {stat.icon}
                </div>
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.3 + index * 0.1, type: "spring" }}
                  className="text-2xl font-bold text-white"
                >
                  {stat.format(stat.value)}
                </motion.div>
              </div>
              <div className="text-white/80 text-sm">
                {stat.label}
              </div>
              
              {/* Background decoration */}
              <div className="absolute -right-4 -bottom-4 w-20 h-20 bg-white/10 rounded-full" />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Achievement Badges */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="mt-6 p-4 bg-gray-50 rounded-xl"
      >
        <h3 className="text-lg font-semibold text-gray-700 mb-3">
          🏆 Logros Desbloqueados
        </h3>
        <div className="flex flex-wrap gap-2">
          {stats.games_played >= 1 && (
            <Badge
              title="Principiante"
              description="Primera partida"
              color="bg-green-500"
            />
          )}
          {stats.games_played >= 10 && (
            <Badge
              title="Aprendiz"
              description="10 partidas"
              color="bg-blue-500"
            />
          )}
          {stats.games_played >= 50 && (
            <Badge
              title="Experto"
              description="50 partidas"
              color="bg-purple-500"
            />
          )}
          {stats.accuracy_rate >= 50 && (
            <Badge
              title="Preciso"
              description="50% precisión"
              color="bg-yellow-500"
            />
          )}
          {stats.accuracy_rate >= 80 && (
            <Badge
              title="Francotirador"
              description="80% precisión"
              color="bg-red-500"
            />
          )}
          {stats.best_streak >= 5 && (
            <Badge
              title="En Racha"
              description="5 aciertos seguidos"
              color="bg-orange-500"
            />
          )}
          {stats.best_time_seconds && stats.best_time_seconds < 5 && (
            <Badge
              title="Velocista"
              description="Menos de 5 segundos"
              color="bg-indigo-500"
            />
          )}
        </div>
      </motion.div>
    </div>
  );
};

// Badge component
const Badge: React.FC<{ title: string; description: string; color: string }> = ({ 
  title, 
  description, 
  color 
}) => (
  <motion.div
    whileHover={{ scale: 1.05 }}
    className={`${color} text-white px-3 py-2 rounded-lg shadow-md`}
  >
    <div className="font-semibold text-sm">{title}</div>
    <div className="text-xs opacity-90">{description}</div>
  </motion.div>
);

export default GameStats;