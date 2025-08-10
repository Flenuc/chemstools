import React, { useState, useEffect, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '@/store';
import {
  startChemWordleGame,
  submitGuess,
  getHint,
  addLetter,
  removeLetter,
  setCurrentGuess,
  resetGame,
  clearError
} from '@/store/chemWordleSlice';

interface ChemWordleProps {
  onComplete?: () => void;
}

const ChemWordle: React.FC<ChemWordleProps> = ({ onComplete }) => {
  const dispatch = useDispatch<AppDispatch>();
  const {
    currentGame,
    currentGuess,
    gameState,
    currentHint,
    hintsUsed,
    gameStartTime,
    loading,
    error,
    keyboardState
  } = useSelector((state: RootState) => state.chemWordle);

  const [showHint, setShowHint] = useState(false);
  const [shakeRow, setShakeRow] = useState(-1);

  // Keyboard layout
  const keyboardRows = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    ['ENTER', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'BACKSPACE']
  ];

  // Handle keyboard input
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (gameState !== 'playing') return;

      const key = event.key.toUpperCase();
      
      if (key === 'ENTER') {
        handleSubmitGuess();
      } else if (key === 'BACKSPACE') {
        dispatch(removeLetter());
      } else if (key.match(/[A-Z]/) && key.length === 1) {
        dispatch(addLetter(key));
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [gameState, dispatch]);

  const handleStartGame = (difficulty?: string) => {
    dispatch(resetGame());
    dispatch(startChemWordleGame({ difficulty }));
  };

  const handleSubmitGuess = useCallback(() => {
    if (!currentGame || !currentGuess || gameState !== 'playing') return;
    
    if (currentGuess.length !== currentGame.word_length) {
      setShakeRow(currentGame.attempts_used);
      setTimeout(() => setShakeRow(-1), 500);
      return;
    }

    const timeTaken = Math.floor((Date.now() - gameStartTime) / 1000);
    dispatch(submitGuess({
      game_id: currentGame.id,
      guess: currentGuess,
      time_taken: timeTaken
    }));
  }, [currentGame, currentGuess, gameState, gameStartTime, dispatch]);

  const handleKeyClick = (key: string) => {
    if (gameState !== 'playing') return;

    if (key === 'ENTER') {
      handleSubmitGuess();
    } else if (key === 'BACKSPACE') {
      dispatch(removeLetter());
    } else {
      dispatch(addLetter(key));
    }
  };

  const handleGetHint = () => {
    if (!currentGame) return;
    
    dispatch(getHint({
      game_id: currentGame.id,
      hint_level: hintsUsed + 1
    }));
    setShowHint(true);
  };

  const getKeyClass = (key: string) => {
    const baseClass = "m-1 px-3 py-4 rounded font-bold text-sm transition-all duration-200 ";
    
    if (key === 'ENTER' || key === 'BACKSPACE') {
      return baseClass + "bg-gray-400 hover:bg-gray-500 text-white px-6";
    }
    
    const state = keyboardState[key];
    switch (state) {
      case 'correct':
        return baseClass + "bg-green-500 text-white";
      case 'present':
        return baseClass + "bg-yellow-500 text-white";
      case 'absent':
        return baseClass + "bg-gray-600 text-white";
      default:
        return baseClass + "bg-gray-200 hover:bg-gray-300 text-gray-800";
    }
  };

  const getLetterClass = (letter: string, state: string, isCurrentRow = false, position = 0) => {
    const baseClass = "w-14 h-14 border-2 flex items-center justify-center font-bold text-lg transition-all duration-300 ";
    
    if (isCurrentRow && currentGuess[position] === letter) {
      return baseClass + "border-gray-400 bg-white text-gray-800 scale-110";
    }
    
    switch (state) {
      case 'correct':
        return baseClass + "bg-green-500 border-green-500 text-white";
      case 'present':
        return baseClass + "bg-yellow-500 border-yellow-500 text-white";
      case 'absent':
        return baseClass + "bg-gray-500 border-gray-500 text-white";
      default:
        return baseClass + "border-gray-300 bg-white text-gray-800";
    }
  };

  const renderGameGrid = () => {
    if (!currentGame) return null;

    const rows = [];
    
    // Renderizar intentos completados
    for (let i = 0; i < currentGame.attempts_used; i++) {
      const guess = currentGame.guesses[i];
      rows.push(
        <div key={i} className="flex justify-center gap-1 mb-2">
          {guess.results.map((result: { letter: string; state: string }, j: number) => (
            <div
              key={j}
              className={getLetterClass(result.letter, result.state)}
            >
              {result.letter}
            </div>
          ))}
        </div>
      );
    }
    
    // Renderizar fila actual
    if (!currentGame.is_completed) {
      const currentRowClass = shakeRow === currentGame.attempts_used ? "animate-shake" : "";
      rows.push(
        <div key={currentGame.attempts_used} className={`flex justify-center gap-1 mb-2 ${currentRowClass}`}>
          {Array.from({ length: currentGame.word_length }).map((_, i) => (
            <div
              key={i}
              className={getLetterClass(
                currentGuess[i] || '', 
                '', 
                true, 
                i
              )}
            >
              {currentGuess[i] || ''}
            </div>
          ))}
        </div>
      );
    }
    
    // Renderizar filas vacías restantes
    const remainingRows = currentGame.max_attempts - currentGame.attempts_used - (currentGame.is_completed ? 0 : 1);
    for (let i = 0; i < remainingRows; i++) {
      rows.push(
        <div key={currentGame.attempts_used + i + 1} className="flex justify-center gap-1 mb-2">
          {Array.from({ length: currentGame.word_length }).map((_, j) => (
            <div key={j} className={getLetterClass('', '')}>
            </div>
          ))}
        </div>
      );
    }
    
    return rows;
  };

  const CategoryBadge = ({ category }: { category: string }) => {
    const categoryColors = {
      element: 'bg-blue-500',
      compound: 'bg-green-500',
      ion: 'bg-purple-500',
      molecule: 'bg-orange-500'
    };
    
    const categoryNames = {
      element: 'Elemento',
      compound: 'Compuesto',
      ion: 'Ion',
      molecule: 'Molécula'
    };
    
    return (
      <span className={`px-3 py-1 rounded-full text-white text-sm ${categoryColors[category as keyof typeof categoryColors] || 'bg-gray-500'}`}>
        {categoryNames[category as keyof typeof categoryNames] || category}
      </span>
    );
  };

  // Estado inicial - menú de inicio
  if (gameState === 'idle') {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <div className="flex justify-center items-center gap-4 mb-6">
            <div className="text-5xl">⚗️</div>
            <h2 className="text-3xl font-bold text-purple-600">ChemWordle</h2>
            <div className="text-5xl">🧪</div>
          </div>
          <p className="text-gray-600 mb-6">Adivina el elemento o compuesto químico</p>
          
          <div className="space-y-4">
            <button
              onClick={() => handleStartGame()}
              className="w-full bg-purple-500 hover:bg-purple-600 text-white font-bold py-3 px-6 rounded-lg transition-colors"
            >
              🎲 Jugar Palabra Aleatoria
            </button>
            
            <div className="grid grid-cols-3 gap-3">
              <button
                onClick={() => handleStartGame('easy')}
                className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded transition-colors"
              >
                📚 Fácil
              </button>
              <button
                onClick={() => handleStartGame('medium')}
                className="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-2 px-4 rounded transition-colors"
              >
                🎯 Medio
              </button>
              <button
                onClick={() => handleStartGame('hard')}
                className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition-colors"
              >
                🔥 Difícil
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Estado de carga
  if (loading) {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Preparando ChemWordle...</p>
        </div>
      </div>
    );
  }

  // Estado de error
  if (gameState === 'error') {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">❌ Error</div>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="space-y-2">
            <button
              onClick={() => dispatch(clearError())}
              className="bg-purple-500 hover:bg-purple-600 text-white font-bold py-2 px-4 rounded mr-2"
            >
              Reintentar
            </button>
            <button
              onClick={() => dispatch(resetGame())}
              className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded"
            >
              Nuevo Juego
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Juego principal
  if (!currentGame) return null;

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      {/* Header del juego */}
      <div className="text-center mb-6">
        <div className="flex justify-center items-center gap-4 mb-4">
          <h2 className="text-2xl font-bold text-purple-600">ChemWordle</h2>
          <CategoryBadge category={currentGame.target_word.category} />
        </div>
        
        <div className="flex justify-center items-center gap-6 text-sm text-gray-600">
          <span>Intento: {currentGame.attempts_used + (currentGame.is_completed ? 0 : 1)}/{currentGame.max_attempts}</span>
          <span>Letras: {currentGame.word_length}</span>
          <span>Pistas: {hintsUsed}</span>
        </div>
      </div>

      {/* Pista principal */}
      <div className="mb-6 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
        <p className="text-blue-800">
          <strong>💡 Pista:</strong> {currentGame.target_word.hint}
        </p>
      </div>

      {/* Pista adicional si se solicitó */}
      {showHint && currentHint && (
        <div className="mb-6 p-4 bg-yellow-50 rounded-lg border-l-4 border-yellow-500">
          <p className="text-yellow-800">
            <strong>🔍 Pista adicional:</strong> {currentHint}
          </p>
          <button
            onClick={() => setShowHint(false)}
            className="mt-2 text-xs text-yellow-600 hover:text-yellow-800"
          >
            Ocultar pista
          </button>
        </div>
      )}

      {/* Grid del juego */}
      <div className="mb-6">
        {renderGameGrid()}
      </div>

      {/* Botones de acción */}
      {!currentGame.is_completed && (
        <div className="flex justify-center gap-4 mb-6">
          <button
            onClick={handleGetHint}
            className="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-2 px-4 rounded transition-colors"
            disabled={gameState === 'submitting'}
          >
            💡 Pista (+{hintsUsed + 1})
          </button>
          <button
            onClick={handleSubmitGuess}
            disabled={currentGuess.length !== currentGame.word_length || gameState === 'submitting'}
            className={`font-bold py-2 px-6 rounded transition-colors ${
              currentGuess.length === currentGame.word_length && gameState !== 'submitting'
                ? 'bg-purple-500 hover:bg-purple-600 text-white'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {gameState === 'submitting' ? '⏳ Enviando...' : '✅ Enviar'}
          </button>
        </div>
      )}

      {/* Resultado del juego */}
      {currentGame.is_completed && (
        <div className="mb-6 p-6 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border">
          <div className="text-center">
            {currentGame.is_won ? (
              <>
                <div className="text-4xl mb-2">🎉</div>
                <h3 className="text-2xl font-bold text-green-600 mb-2">¡Felicitaciones!</h3>
                <p className="text-gray-700 mb-4">
                  Adivinaste <strong>{currentGame.target_word.word}</strong> en {currentGame.attempts_used} intento{currentGame.attempts_used !== 1 ? 's' : ''}
                </p>
              </>
            ) : (
              <>
                <div className="text-4xl mb-2">😔</div>
                <h3 className="text-2xl font-bold text-red-600 mb-2">¡Casi lo logras!</h3>
                <p className="text-gray-700 mb-4">
                  La palabra era: <strong>{currentGame.target_word.word}</strong>
                </p>
              </>
            )}
            
            {/* Información adicional sobre la palabra */}
            <div className="mt-4 p-4 bg-white rounded-lg text-left">
              <h4 className="font-semibold mb-2">Información sobre {currentGame.target_word.word}:</h4>
              <ul className="text-sm space-y-1">
                {currentGame.target_word.chemical_formula && (
                  <li><strong>Fórmula:</strong> {currentGame.target_word.chemical_formula}</li>
                )}
                {currentGame.target_word.atomic_number && (
                  <li><strong>Número atómico:</strong> {currentGame.target_word.atomic_number}</li>
                )}
                {currentGame.target_word.group_number && (
                  <li><strong>Grupo:</strong> {currentGame.target_word.group_number}</li>
                )}
                {currentGame.target_word.period_number && (
                  <li><strong>Período:</strong> {currentGame.target_word.period_number}</li>
                )}
                {currentGame.target_word.state_at_stp && (
                  <li><strong>Estado STP:</strong> {currentGame.target_word.state_at_stp}</li>
                )}
                {currentGame.target_word.molecular_weight && (
                  <li><strong>Peso molecular:</strong> {currentGame.target_word.molecular_weight} g/mol</li>
                )}
              </ul>
            </div>
            
            <div className="mt-4 space-y-2">
              <button
                onClick={() => dispatch(resetGame())}
                className="w-full bg-purple-500 hover:bg-purple-600 text-white font-bold py-2 px-4 rounded transition-colors"
              >
                🔄 Jugar de Nuevo
              </button>
              <button
                onClick={onComplete}
                className="w-full bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition-colors"
              >
                📊 Ver Estadísticas
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Teclado virtual */}
      <div className="space-y-2">
        {keyboardRows.map((row, i) => (
          <div key={i} className="flex justify-center">
            {row.map((key) => (
              <button
                key={key}
                onClick={() => handleKeyClick(key)}
                className={getKeyClass(key)}
                disabled={gameState !== 'playing'}
              >
                {key === 'BACKSPACE' ? '⌫' : key === 'ENTER' ? '↵' : key}
              </button>
            ))}
          </div>
        ))}
      </div>

      {/* Error messages */}
      {error && (
        <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded text-red-700 text-sm">
          {error}
          <button
            onClick={() => dispatch(clearError())}
            className="ml-2 text-red-500 hover:text-red-700"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
};

export default ChemWordle;