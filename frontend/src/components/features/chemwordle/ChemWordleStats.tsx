import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '@/store';
import { fetchChemWordleStats, fetchChemWordleLeaderboard } from '@/store/chemWordleSlice';

const ChemWordleStats: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { stats, leaderboard, loading } = useSelector((state: RootState) => state.chemWordle);

  useEffect(() => {
    dispatch(fetchChemWordleStats());
    dispatch(fetchChemWordleLeaderboard());
  }, [dispatch]);

  const formatTime = (seconds: number | undefined) => {
    if (!seconds) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const renderWinDistribution = () => {
    if (!stats?.win_distribution) return null;

    const maxAttempts = 6;
    const maxCount = Math.max(...Object.values(stats.win_distribution));
    
    return (
      <div className="space-y-2">
        <h4 className="font-semibold text-gray-800">Distribución de Victorias</h4>
        {Array.from({ length: maxAttempts }, (_, i) => {
          const attempt = i + 1;
          const count = stats.win_distribution[attempt.toString()] || 0;
          const percentage = maxCount > 0 ? (count / maxCount) * 100 : 0;
          
          return (
            <div key={attempt} className="flex items-center space-x-2">
              <span className="w-4 text-sm font-medium">{attempt}</span>
              <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
                <div
                  className="bg-green-500 h-6 rounded-full flex items-center justify-end pr-2"
                  style={{ width: `${Math.max(percentage, count > 0 ? 10 : 0)}%` }}
                >
                  {count > 0 && (
                    <span className="text-white text-xs font-bold">{count}</span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p>Cargando estadísticas...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <h2 className="text-3xl font-bold text-center text-purple-600 mb-8">
        📊 Estadísticas ChemWordle
      </h2>

      {/* Estadísticas personales */}
      {stats && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-semibold mb-6 text-purple-800">Tus Estadísticas</h3>
          
          {/* Resumen general */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">{stats.games_played}</div>
              <div className="text-sm text-gray-600">Partidas Jugadas</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{stats.win_percentage.toFixed(1)}%</div>
              <div className="text-sm text-gray-600">Porcentaje Victoria</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">{stats.current_streak}</div>
              <div className="text-sm text-gray-600">Racha Actual</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600">{stats.max_streak}</div>
              <div className="text-sm text-gray-600">Mejor Racha</div>
            </div>
          </div>

          {/* Estadísticas adicionales */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h4 className="font-semibold text-gray-800 mb-4">Resumen de Victorias</h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Partidas ganadas:</span>
                  <span className="font-semibold">{stats.games_won}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Partidas perdidas:</span>
                  <span className="font-semibold">{stats.games_played - stats.games_won}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Mejor tiempo:</span>
                  <span className="font-semibold">{formatTime(stats.best_time_seconds)}</span>
                </div>
              </div>
            </div>
            
            <div>
              {renderWinDistribution()}
            </div>
          </div>
        </div>
      )}

      {/* Tabla de clasificación */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-semibold mb-6 text-purple-800">🏆 Clasificación Global</h3>
        
        {leaderboard.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-purple-100">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-purple-800">Posición</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-purple-800">Usuario</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-purple-800">% Victoria</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-purple-800">Partidas</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-purple-800">Racha Actual</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-purple-800">Mejor Racha</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {leaderboard.map((entry) => (
                  <tr key={entry.username} className={entry.rank <= 3 ? 'bg-yellow-50' : ''}>
                    <td className="px-4 py-3">
                      <div className="flex items-center">
                        {entry.rank === 1 && <span className="text-2xl mr-2">🥇</span>}
                        {entry.rank === 2 && <span className="text-2xl mr-2">🥈</span>}
                        {entry.rank === 3 && <span className="text-2xl mr-2">🥉</span>}
                        <span className="font-medium">#{entry.rank}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 font-medium text-gray-900">{entry.username}</td>
                    <td className="px-4 py-3">
                      <span className="font-bold text-green-600">{entry.win_percentage.toFixed(1)}%</span>
                    </td>
                    <td className="px-4 py-3">{entry.games_played}</td>
                    <td className="px-4 py-3">
                      <span className="font-medium text-blue-600">{entry.current_streak}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-medium text-orange-600">{entry.max_streak}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No hay datos de clasificación disponibles
          </div>
        )}
      </div>

      {/* Información sobre ChemWordle */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6 border-l-4 border-purple-500">
        <h3 className="text-lg font-semibold text-purple-800 mb-4">🎯 Cómo Jugar ChemWordle</h3>
        <div className="space-y-3 text-sm text-gray-700">
          <p>• <strong>Objetivo:</strong> Adivina el elemento o compuesto químico en 6 intentos máximo</p>
          <p>• <strong>Pistas:</strong> Cada letra tiene un color que indica su estado:</p>
          <div className="flex flex-wrap gap-4 ml-4 mt-2">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-green-500 rounded flex items-center justify-center text-white font-bold text-xs">A</div>
              <span>Verde: Letra correcta en posición correcta</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-yellow-500 rounded flex items-center justify-center text-white font-bold text-xs">B</div>
              <span>Amarillo: Letra correcta en posición incorrecta</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gray-500 rounded flex items-center justify-center text-white font-bold text-xs">C</div>
              <span>Gris: Letra no está en la palabra</span>
            </div>
          </div>
          <p>• <strong>Pistas adicionales:</strong> Puedes solicitar pistas sobre la categoría, fórmula y propiedades</p>
          <p>• <strong>Categorías:</strong> Elementos, compuestos, iones y moléculas</p>
        </div>
      </div>
    </div>
  );
};

export default ChemWordleStats;