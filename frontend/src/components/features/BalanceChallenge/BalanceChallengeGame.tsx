import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../../store';
import {
  startChallenge,
  submitCoefficients,
  getHint,
  getCurrentChallenge,
  getChallengeStats,
  endChallenge,
  clearError,
  clearHints,
  resetGame,
} from '../../../store/balanceChallengeSlice';

const BalanceChallengeGame: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const {
    currentGame,
    stats,
    loading,
    error,
    hints,
  } = useSelector((state: RootState) => state.balanceChallenge);

  const [gameState, setGameState] = useState<'menu' | 'playing' | 'completed' | 'stats'>('menu');
  const [coefficients, setCoefficients] = useState<Array<{ id: string; value: number | null; numberId: string | null }>>([]);
  const [availableNumbers, setAvailableNumbers] = useState<Array<{ id: string; value: number; used: boolean }>>([]);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string; details?: any } | null>(null);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [gameStartTime, setGameStartTime] = useState<number | null>(null);
  const [draggedItem, setDraggedItem] = useState<any>(null);
  const [dragOverSlot, setDragOverSlot] = useState<number | null>(null);

  // Timer effect
  useEffect(() => {
    if (gameState === 'playing' && gameStartTime) {
      const timer = setInterval(() => {
        setTimeElapsed(Math.floor((Date.now() - gameStartTime) / 1000));
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [gameState, gameStartTime]);

  // Check for existing game on mount
  useEffect(() => {
    dispatch(getCurrentChallenge());
  }, [dispatch]);

  // Update game state when currentGame changes
  useEffect(() => {
    if (currentGame && !currentGame.is_completed) {
      setGameState('playing');
      initializeCoefficients(currentGame.compounds.all_compounds);
      setGameStartTime(Date.now() - (currentGame.time_elapsed || 0) * 1000);
    } else if (currentGame && currentGame.is_completed) {
      setGameState('completed');
    }
  }, [currentGame]);

  const handleStartNewChallenge = async (difficulty: 'easy' | 'medium' | 'hard') => {
    try {
      dispatch(clearError());
      dispatch(clearHints());
      const result = await dispatch(startChallenge(difficulty)).unwrap();
      
      console.log('Start challenge result:', result); // Debug log
      
      // Check if result has game data directly (without success wrapper)
      if (result?.game || result?.id) {
        setGameState('playing');
        setGameStartTime(Date.now());
        setTimeElapsed(0);
        setFeedback(null);
        // If the game data is at the root level
        if (result?.id && !result?.game) {
          // Update the game state directly if needed
          initializeCoefficients(result.compounds?.all_compounds || []);
        }
      } else if (result?.success) {
        // Original success wrapper format
        setGameState('playing');
        setGameStartTime(Date.now());
        setTimeElapsed(0);
        setFeedback(null);
      } else {
        console.error('Failed to start challenge. Result:', result);
        setFeedback({
          type: 'error',
          message: result?.error || result?.detail || 'Error al iniciar el desafío'
        });
      }
    } catch (error: any) {
      console.error('Error starting challenge:', error);
      setFeedback({
        type: 'error',
        message: error?.message || 'Error al conectar con el servidor'
      });
    }
  };

  const initializeCoefficients = (compounds: string[]) => {
    const emptyCoeffs = compounds.map((_, index) => ({ 
      id: `slot-${index}`, 
      value: null, 
      numberId: null 
    }));
    setCoefficients(emptyCoeffs);
    
    const numbers = [];
    for (let i = 1; i <= 10; i++) {
      for (let copy = 0; copy < 3; copy++) {
        numbers.push({ 
          id: `num-${i}-${copy}`, 
          value: i, 
          used: false 
        });
      }
    }
    setAvailableNumbers(numbers);
  };

  const handleSubmitAttempt = async () => {
    if (!currentGame) return;

    const coeffValues = coefficients.map(coeff => coeff.value).filter(val => val !== null) as number[];
    
    if (coeffValues.length !== coefficients.length) {
      setFeedback({
        type: 'error',
        message: 'Debes colocar coeficientes en todas las posiciones'
      });
      return;
    }

    try {
      const result = await dispatch(submitCoefficients({
        gameId: currentGame.id,
        coefficients: coeffValues,
        timeTaken: timeElapsed
      })).unwrap();

      console.log('Submit attempt result:', result); // Debug log

      // Handle different response structures
      const isCorrect = result?.is_correct || result?.attempt?.is_correct || false;
      const gameCompleted = result?.game_completed || result?.game?.is_completed || false;
      const validationResult = result?.validation_result || result?.attempt?.validation_result;

      setFeedback({
        type: isCorrect ? 'success' : 'error',
        message: isCorrect ? 
          '¡Excelente! Has balanceado la ecuación correctamente' : 
          'Intento incorrecto. La ecuación no está balanceada',
        details: validationResult
      });

      if (gameCompleted || isCorrect) {
        setGameState('completed');
      }
    } catch (error: any) {
      console.error('Error submitting attempt:', error);
      setFeedback({
        type: 'error',
        message: error?.message || 'Error al enviar el intento'
      });
    }
  };

  const handleGetHint = async (hintType: 'element' | 'coefficient' | 'method') => {
    if (!currentGame) return;
    
    try {
      const result = await dispatch(getHint({
        gameId: currentGame.id,
        hintType
      })).unwrap();
      
      console.log('Get hint result:', result); // Debug log
      
      // If hint is successfully added to state, no need for feedback
      // Only show error if there's an actual error
      if (result?.error || result?.detail) {
        setFeedback({
          type: 'error',
          message: result.error || result.detail || 'Error al obtener la pista'
        });
      }
    } catch (error: any) {
      console.error('Error getting hint:', error);
      setFeedback({
        type: 'error',
        message: error?.message || 'Error al obtener la pista'
      });
    }
  };

  const handleLoadStats = async () => {
    try {
      const result = await dispatch(getChallengeStats()).unwrap();
      console.log('Load stats result:', result); // Debug log
      
      // If stats are loaded (check if result has stats properties)
      if (result?.username || result?.games_played !== undefined || result?.stats) {
        setGameState('stats');
      } else if (result?.error || result?.detail) {
        setFeedback({
          type: 'error',
          message: result.error || result.detail || 'Error al cargar estadísticas'
        });
      } else {
        // Stats loaded successfully, just switch view
        setGameState('stats');
      }
    } catch (error: any) {
      console.error('Error loading stats:', error);
      setFeedback({
        type: 'error',
        message: error?.message || 'Error al cargar estadísticas'
      });
    }
  };

  const handleEndChallenge = async () => {
    try {
      const result = await dispatch(endChallenge()).unwrap();
      console.log('End challenge result:', result); // Debug log
      
      // For DELETE, success can be null, empty object, or have success/message property
      if (result === null || result === undefined || result?.success || result?.message || Object.keys(result || {}).length === 0) {
        dispatch(resetGame());
        setGameState('menu');
      } else if (result?.error || result?.detail) {
        setFeedback({
          type: 'error',
          message: result.error || result.detail || 'Error al finalizar el desafío'
        });
      } else {
        // Assume success if no error
        dispatch(resetGame());
        setGameState('menu');
      }
    } catch (error: any) {
      console.error('Error ending challenge:', error);
      // If error includes "No hay desafío activo", just go back to menu
      if (error?.message?.includes('No hay desafío activo') || error?.message?.includes('no active challenge')) {
        dispatch(resetGame());
        setGameState('menu');
      } else {
        setFeedback({
          type: 'error',
          message: error?.message || 'Error al finalizar el desafío'
        });
      }
    }
  };

  // Drag and drop handlers
  const handleDragStart = (e: React.DragEvent, item: any, source: string) => {
    setDraggedItem({ ...item, source });
    e.dataTransfer.effectAllowed = 'move';
    (e.target as HTMLElement).style.opacity = '0.5';
  };

  const handleDragEnd = (e: React.DragEvent) => {
    (e.target as HTMLElement).style.opacity = '1';
    setDraggedItem(null);
    setDragOverSlot(null);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDragEnter = (e: React.DragEvent, slotIndex: number) => {
    e.preventDefault();
    setDragOverSlot(slotIndex);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    if (!e.currentTarget.contains(e.relatedTarget as Node)) {
      setDragOverSlot(null);
    }
  };

  const handleDrop = (e: React.DragEvent, targetSlotIndex: number) => {
    e.preventDefault();
    setDragOverSlot(null);

    if (!draggedItem) return;

    if (draggedItem.source === 'pool') {
      const number = availableNumbers.find(num => num.id === draggedItem.id);
      if (!number || number.used) return;

      const newAvailableNumbers = [...availableNumbers];
      const numberIndex = newAvailableNumbers.findIndex(num => num.id === draggedItem.id);
      newAvailableNumbers[numberIndex] = { ...number, used: true };

      const newCoefficients = [...coefficients];
      if (newCoefficients[targetSlotIndex].value !== null) {
        const oldNumberId = newCoefficients[targetSlotIndex].numberId;
        const oldNumberIndex = newAvailableNumbers.findIndex(num => num.id === oldNumberId);
        if (oldNumberIndex !== -1) {
          newAvailableNumbers[oldNumberIndex].used = false;
        }
      }

      newCoefficients[targetSlotIndex] = {
        ...newCoefficients[targetSlotIndex],
        value: draggedItem.value,
        numberId: draggedItem.id
      };

      setCoefficients(newCoefficients);
      setAvailableNumbers(newAvailableNumbers);
    }
  };

  const handleReturnToPool = (slotIndex: number) => {
    const newCoefficients = [...coefficients];
    const coefficient = newCoefficients[slotIndex];
    
    if (coefficient.value !== null && coefficient.numberId) {
      const newAvailableNumbers = [...availableNumbers];
      const numberIndex = newAvailableNumbers.findIndex(num => num.id === coefficient.numberId);
      if (numberIndex !== -1) {
        newAvailableNumbers[numberIndex].used = false;
      }
      
      newCoefficients[slotIndex] = {
        ...coefficient,
        value: null,
        numberId: null
      };
      
      setCoefficients(newCoefficients);
      setAvailableNumbers(newAvailableNumbers);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const renderEquation = () => {
    if (!currentGame) return null;

    const { reactants, products } = currentGame.compounds;
    let compoundIndex = 0;

    const renderCompoundWithCoeff = (compound: string, isLast = false) => {
      const coeff = coefficients[compoundIndex];
      const index = compoundIndex++;
      
      return (
        <span key={index} className="inline-flex items-center">
          <div
            className={`w-16 h-16 border-2 border-dashed rounded-lg flex items-center justify-center mr-2 transition-all cursor-pointer ${
              dragOverSlot === index ? 'border-blue-400 bg-blue-50 scale-105' : 
              coeff.value ? 'border-green-400 bg-green-50' : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragOver={handleDragOver}
            onDragEnter={(e) => handleDragEnter(e, index)}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, index)}
            onClick={() => handleReturnToPool(index)}
            title={coeff.value ? "Click para devolver al pool" : "Arrastra un número aquí"}
          >
            {coeff.value && (
              <div
                className="w-12 h-12 bg-blue-500 hover:bg-blue-600 text-white rounded-full flex items-center justify-center font-bold cursor-grab active:cursor-grabbing transition-transform hover:scale-105"
                draggable
                onDragStart={(e) => handleDragStart(e, coeff, `slot-${index}`)}
                onDragEnd={handleDragEnd}
              >
                {coeff.value}
              </div>
            )}
          </div>
          <span className="text-2xl font-mono mr-2 select-none">{compound}</span>
          {!isLast && <span className="text-2xl text-gray-500 mr-2 select-none">+</span>}
        </span>
      );
    };

    return (
      <div className="flex items-center justify-center flex-wrap gap-2 p-8 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border-2 border-blue-200">
        {reactants.map((compound, idx) => 
          renderCompoundWithCoeff(compound, idx === reactants.length - 1)
        )}
        <span className="text-3xl font-bold text-purple-600 mx-6 select-none">→</span>
        {products.map((compound, idx) => 
          renderCompoundWithCoeff(compound, idx === products.length - 1)
        )}
      </div>
    );
  };

  const renderNumberPool = () => {
    const unusedNumbers = availableNumbers.filter(num => !num.used);
    
    return (
      <div className="min-h-[120px] p-6 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors">
        <h3 className="text-lg font-semibold text-gray-700 mb-4 select-none">
          🔢 Números disponibles (arrastra para usar):
        </h3>
        <div className="flex flex-wrap gap-3 justify-center">
          {unusedNumbers.slice(0, 20).map((number) => (
            <div
              key={number.id}
              className="w-12 h-12 bg-blue-500 hover:bg-blue-600 text-white rounded-full flex items-center justify-center font-bold cursor-grab active:cursor-grabbing transition-all hover:scale-110 hover:shadow-lg"
              draggable
              onDragStart={(e) => handleDragStart(e, number, 'pool')}
              onDragEnd={handleDragEnd}
              title={`Número ${number.value}`}
            >
              {number.value}
            </div>
          ))}
        </div>
        <p className="text-sm text-gray-600 mt-3 text-center select-none">
          💡 Tip: También puedes hacer click en los coeficientes ya colocados para devolverlos aquí
        </p>
      </div>
    );
  };

  // Error display
  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <h2 className="text-xl font-semibold text-red-800 mb-2">Error</h2>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => dispatch(clearError())}
            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded transition-colors"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  if (gameState === 'menu') {
    return (
      <div className="max-w-5xl mx-auto p-6">
        <div className="text-center mb-10">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">⚖️ Desafío de Balanceo</h1>
          <p className="text-xl text-gray-600">Balancea ecuaciones químicas arrastrando los coeficientes correctos</p>
          <div className="mt-4 text-sm text-gray-500">
            Arrastra los números desde el pool hasta las posiciones de los coeficientes
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-10">
          <div className="bg-green-50 border-2 border-green-200 rounded-xl p-8 text-center hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-4">🟢</div>
            <h3 className="text-xl font-semibold text-green-800 mb-3">Fácil</h3>
            <p className="text-green-600 mb-6">Ecuaciones simples de síntesis y descomposición</p>
            <button
              onClick={() => handleStartNewChallenge('easy')}
              disabled={loading}
              className="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Cargando...' : 'Comenzar Fácil'}
            </button>
          </div>

          <div className="bg-yellow-50 border-2 border-yellow-200 rounded-xl p-8 text-center hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-4">🟡</div>
            <h3 className="text-xl font-semibold text-yellow-800 mb-3">Medio</h3>
            <p className="text-yellow-600 mb-6">Combustión y reacciones ácido-base</p>
            <button
              onClick={() => handleStartNewChallenge('medium')}
              disabled={loading}
              className="w-full bg-yellow-500 hover:bg-yellow-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Cargando...' : 'Comenzar Medio'}
            </button>
          </div>

          <div className="bg-red-50 border-2 border-red-200 rounded-xl p-8 text-center hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-4">🔴</div>
            <h3 className="text-xl font-semibold text-red-800 mb-3">Difícil</h3>
            <p className="text-red-600 mb-6">Reacciones redox y ecuaciones complejas</p>
            <button
              onClick={() => handleStartNewChallenge('hard')}
              disabled={loading}
              className="w-full bg-red-500 hover:bg-red-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Cargando...' : 'Comenzar Difícil'}
            </button>
          </div>
        </div>

        <div className="text-center">
          <button
            onClick={handleLoadStats}
            disabled={loading}
            className="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-4 px-8 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            📊 Ver Estadísticas
          </button>
        </div>

        {loading && (
          <div className="text-center mt-6">
            <div className="inline-block animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
            <p className="mt-2 text-gray-600">Cargando...</p>
          </div>
        )}
      </div>
    );
  }

  if (gameState === 'stats') {
    return (
      <div className="max-w-5xl mx-auto p-6">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">📊 Tus Estadísticas</h1>
          <button
            onClick={() => setGameState('menu')}
            className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg transition-colors"
          >
            ← Volver al Menú
          </button>
        </div>

        {stats && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-8 text-center">
              <div className="text-4xl text-blue-600 mb-3">{stats.games_played}</div>
              <div className="text-lg font-semibold text-blue-800">Partidas Jugadas</div>
            </div>

            <div className="bg-green-50 border-2 border-green-200 rounded-xl p-8 text-center">
              <div className="text-4xl text-green-600 mb-3">{stats.games_correct}</div>
              <div className="text-lg font-semibold text-green-800">Partidas Correctas</div>
            </div>

            <div className="bg-purple-50 border-2 border-purple-200 rounded-xl p-8 text-center">
              <div className="text-4xl text-purple-600 mb-3">{stats.accuracy_rate.toFixed(1)}%</div>
              <div className="text-lg font-semibold text-purple-800">Precisión</div>
            </div>

            <div className="bg-orange-50 border-2 border-orange-200 rounded-xl p-8 text-center">
              <div className="text-4xl text-orange-600 mb-3">{stats.current_streak}</div>
              <div className="text-lg font-semibold text-orange-800">Racha Actual</div>
            </div>

            <div className="bg-red-50 border-2 border-red-200 rounded-xl p-8 text-center">
              <div className="text-4xl text-red-600 mb-3">{stats.best_streak}</div>
              <div className="text-lg font-semibold text-red-800">Mejor Racha</div>
            </div>

            <div className="bg-teal-50 border-2 border-teal-200 rounded-xl p-8 text-center">
              <div className="text-4xl text-teal-600 mb-3">{stats.average_time_per_game.toFixed(0)}s</div>
              <div className="text-lg font-semibold text-teal-800">Tiempo Promedio</div>
            </div>
          </div>
        )}
      </div>
    );
  }

  if (gameState === 'playing') {
    return (
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <button
            onClick={handleEndChallenge}
            className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg transition-colors"
          >
            ← Menú
          </button>
          
          <div className="flex items-center gap-8">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">⏱️ {formatTime(timeElapsed)}</div>
              <div className="text-sm text-gray-600">Tiempo</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">{currentGame?.attempts}/{currentGame?.max_attempts}</div>
              <div className="text-sm text-gray-600">Intentos</div>
            </div>
            
            <div className="text-center">
              <div className="text-xl font-semibold text-orange-600 capitalize">{currentGame?.difficulty}</div>
              <div className="text-sm text-gray-600">Dificultad</div>
            </div>
          </div>
        </div>

        {/* Título */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-3">Balancea la Ecuación</h1>
          <p className="text-lg text-gray-600">Arrastra los números desde el pool hacia las posiciones de los coeficientes</p>
        </div>

        {/* Ecuación */}
        <div className="mb-10">
          {renderEquation()}
        </div>

        {/* Pool de números */}
        <div className="mb-10">
          {renderNumberPool()}
        </div>

        {/* Botones de acción */}
        <div className="flex flex-wrap gap-4 justify-center mb-8">
          <button
            onClick={handleSubmitAttempt}
            disabled={loading || coefficients.some(c => c.value === null)}
            className="bg-green-500 hover:bg-green-600 disabled:bg-gray-300 text-white font-semibold py-4 px-8 rounded-xl transition-colors disabled:cursor-not-allowed text-lg"
          >
            {loading ? 'Verificando...' : '✓ Verificar Ecuación'}
          </button>

          <button
            onClick={() => handleGetHint('element')}
            disabled={loading}
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-4 px-8 rounded-xl transition-colors disabled:cursor-not-allowed"
          >
            💡 Pista General
          </button>

          <button
            onClick={() => handleGetHint('coefficient')}
            disabled={loading}
            className="bg-purple-500 hover:bg-purple-600 text-white font-semibold py-4 px-8 rounded-xl transition-colors disabled:cursor-not-allowed"
          >
            🔢 Pista de Coeficiente
          </button>
        </div>

        {/* Feedback */}
        {feedback && (
          <div className={`p-6 rounded-xl mb-8 border-2 ${
            feedback.type === 'success' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
          }`}>
            <p className={`text-lg font-semibold mb-2 ${
              feedback.type === 'success' ? 'text-green-800' : 'text-red-800'
            }`}>
              {feedback.message}
            </p>
            {feedback.details && (
              <div className="text-gray-700">
                <p><strong>Tu ecuación:</strong> {feedback.details.user_equation}</p>
                <p><strong>Ecuación objetivo:</strong> {feedback.details.target_equation}</p>
              </div>
            )}
          </div>
        )}

        {/* Pistas */}
        {hints.length > 0 && (
          <div className="space-y-3 mb-8">
            <h3 className="text-lg font-semibold text-gray-700">💡 Pistas recibidas:</h3>
            {hints.map((hint, index) => (
              <div key={index} className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
                <span className="text-yellow-800 font-medium">{hint.message}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  if (gameState === 'completed') {
    return (
      <div className="max-w-5xl mx-auto p-6 text-center">
        <div className="mb-10">
          <div className="text-8xl mb-6">🎉</div>
          <h1 className="text-5xl font-bold text-green-600 mb-6">¡Ecuación Balanceada!</h1>
          <p className="text-2xl text-gray-600 mb-8">
            Has completado el desafío en {formatTime(timeElapsed)} con {currentGame?.attempts} intentos
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 mb-10">
          <div className="bg-green-50 border-2 border-green-200 rounded-xl p-8">
            <h3 className="text-xl font-semibold text-green-800 mb-3">Tiempo</h3>
            <div className="text-4xl font-bold text-green-600">{formatTime(timeElapsed)}</div>
          </div>

          <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-8">
            <h3 className="text-xl font-semibold text-blue-800 mb-3">Intentos</h3>
            <div className="text-4xl font-bold text-blue-600">{currentGame?.attempts}</div>
          </div>
        </div>

        <div className="flex gap-6 justify-center">
          <button
            onClick={() => handleStartNewChallenge(currentGame?.difficulty || 'easy')}
            className="bg-green-500 hover:bg-green-600 text-white font-semibold py-4 px-8 rounded-xl transition-colors text-lg"
          >
            🔄 Otro Desafío
          </button>
          
          <button
            onClick={() => setGameState('menu')}
            className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-4 px-8 rounded-xl transition-colors text-lg"
          >
            🏠 Menú Principal
          </button>
        </div>
      </div>
    );
  }

  return null;
};

export default BalanceChallengeGame;