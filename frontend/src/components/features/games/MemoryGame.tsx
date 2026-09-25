'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/services/api';

interface Card {
  id: number;
  position: number;
  content?: string;
  type: 'name' | 'formula' | 'hidden';
  pair_id?: number;
  compound_type?: string;
  is_revealed: boolean;
  is_matched: boolean;
}

interface MemoryGame {
  id: number;
  difficulty: string;
  is_completed: boolean;
  pairs_found: number;
  total_pairs: number;
  attempts: number;
  score: number;
  cards: Card[];
  time_elapsed: number;
}

interface MemoryGameProps {
  onGameComplete?: (score: number, time: number) => void;
}

const MemoryGame: React.FC<MemoryGameProps> = ({ onGameComplete }) => {
  const [game, setGame] = useState<MemoryGame | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedCards, setSelectedCards] = useState<number[]>([]);
  const [isChecking, setIsChecking] = useState(false);
  const [gameStarted, setGameStarted] = useState(false);
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('easy');
  const [totalPairs, setTotalPairs] = useState(6);
  const [showResult, setShowResult] = useState(false);
  const [timeElapsed, setTimeElapsed] = useState(0);

  // Timer effect
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (game && !game.is_completed && gameStarted) {
      interval = setInterval(() => {
        setTimeElapsed(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [game, gameStarted]);

  // Start new game
  const startNewGame = async () => {
    setLoading(true);
    try {
      const data = await api.post('games/memory/start_game/', {
        difficulty,
        total_pairs: totalPairs
      });

      if (data.success) {
        setGame(data.game);
        setGameStarted(true);
        setTimeElapsed(0);
        setSelectedCards([]);
        setShowResult(false);
      } else {
        console.error('Error starting game:', data.error);
      }
    } catch (error) {
      console.error('Error starting game:', error);
    } finally {
      setLoading(false);
    }
  };

  // Reveal card
  const revealCard = async (cardPosition: number) => {
    if (!game || isChecking || selectedCards.length >= 2) return;

    const card = game.cards[cardPosition];
    if (card.is_revealed || card.is_matched) return;

    try {
      const data = await api.post('games/memory/reveal_card/', {
        game_id: game.id,
        card_position: cardPosition
      });
      if (data.success) {
        setGame(data.game);
        setSelectedCards(prev => [...prev, cardPosition]);

        // If this is the second card, check for match
        if (selectedCards.length === 1) {
          setIsChecking(true);
          
          setTimeout(async () => {
            if (!data.result.is_match) {
              // Hide cards if no match
              await hideCards();
            }
            setSelectedCards([]);
            setIsChecking(false);

            // Check if game completed
            if (data.result.game_completed) {
              setShowResult(true);
              onGameComplete?.(data.game.score, data.game.time_elapsed);
            }
          }, 3000); // Show cards for 3 seconds
        }
      }
    } catch (error) {
      console.error('Error revealing card:', error);
    }
  };

  // Hide revealed cards
  const hideCards = async () => {
    if (!game) return;

    try {
      const data = await api.post('games/memory/hide_cards/', {
        game_id: game.id
      });
      if (data.success) {
        setGame(data.game);
      }
    } catch (error) {
      console.error('Error hiding cards:', error);
    }
  };

  // Load current game on component mount
  useEffect(() => {
    const loadCurrentGame = async () => {
      try {
        const data = await api.get('games/memory/current_game/');
        if (data.success && data.game) {
          setGame(data.game);
          setGameStarted(true);
          setDifficulty(data.game.difficulty);
        }
      } catch (error) {
        console.error('Error loading current game:', error);
      }
    };

    loadCurrentGame();
  }, []);

  // Get card display content
  const getCardContent = (card: Card) => {
    if (card.type === 'hidden' || (!card.is_revealed && !card.is_matched)) {
      return '?';
    }
    return card.content || '?';
  };

  // Get card color based on type
  const getCardColor = (card: Card) => {
    if (card.type === 'hidden' || (!card.is_revealed && !card.is_matched)) {
      return 'bg-gradient-to-br from-blue-500 to-blue-600';
    }
    
    if (card.is_matched) {
      return 'bg-gradient-to-br from-green-400 to-green-500';
    }

    switch (card.type) {
      case 'name':
        return 'bg-gradient-to-br from-purple-400 to-purple-500';
      case 'formula':
        return 'bg-gradient-to-br from-orange-400 to-orange-500';
      default:
        return 'bg-gradient-to-br from-gray-400 to-gray-500';
    }
  };

  // Format time
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (!gameStarted) {
    return (
      <div className="max-w-md mx-auto bg-white rounded-xl shadow-lg p-6">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            🧠 Memory Molecular
          </h2>
          <p className="text-gray-600">
            Empareja nombres de compuestos con sus fórmulas químicas
          </p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Dificultad
            </label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value as 'easy' | 'medium' | 'hard')}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="easy">Fácil - Compuestos básicos</option>
              <option value="medium">Medio - Compuestos comunes</option>
              <option value="hard">Difícil - Compuestos complejos</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Número de pares: {totalPairs}
            </label>
            <input
              type="range"
              min="3"
              max="8"
              value={totalPairs}
              onChange={(e) => setTotalPairs(parseInt(e.target.value))}
              className="w-full"
            />
          </div>

          <button
            onClick={startNewGame}
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 disabled:opacity-50"
          >
            {loading ? 'Iniciando...' : 'Iniciar Juego'}
          </button>
        </div>
      </div>
    );
  }

  if (!game) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-4 mb-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <h2 className="text-xl font-bold text-gray-800">
              Memory Molecular
            </h2>
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              {game.difficulty.charAt(0).toUpperCase() + game.difficulty.slice(1)}
            </span>
          </div>
          
          <div className="flex items-center space-x-6 text-sm">
            <div className="text-center">
              <div className="font-semibold text-gray-800">{game.pairs_found}</div>
              <div className="text-gray-600">Pares</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-gray-800">{game.attempts}</div>
              <div className="text-gray-600">Intentos</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-gray-800">{game.score}</div>
              <div className="text-gray-600">Puntos</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-gray-800">
                {formatTime(game.time_elapsed || timeElapsed)}
              </div>
              <div className="text-gray-600">Tiempo</div>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Progreso</span>
            <span>{game.pairs_found}/{game.total_pairs}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-green-400 to-green-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(game.pairs_found / game.total_pairs) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Game Board */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div 
          className="grid gap-4"
          style={{
            gridTemplateColumns: `repeat(${Math.ceil(Math.sqrt(game.cards.length))}, 1fr)`
          }}
        >
          {game.cards.map((card, index) => (
            <motion.div
              key={`${card.id}-${index}`}
              className="aspect-square"
              whileHover={{ scale: card.is_matched ? 1 : 1.05 }}
              whileTap={{ scale: card.is_matched ? 1 : 0.95 }}
            >
              <button
                onClick={() => revealCard(index)}
                disabled={card.is_revealed || card.is_matched || isChecking}
                className={`
                  w-full h-full rounded-lg shadow-md transition-all duration-1000
                  flex items-center justify-center text-white font-bold
                  disabled:cursor-not-allowed
                  ${getCardColor(card)}
                  ${card.is_matched ? 'opacity-75' : 'hover:shadow-lg'}
                `}
              >
                <motion.div
                  initial={false}
                  animate={{
                    rotateY: card.is_revealed || card.is_matched ? 180 : 0
                  }}
                  transition={{ 
                    duration: 0.8,
                    ease: "easeInOut",
                    delay: card.is_revealed && !card.is_matched ? 0.2 : 0
                  }}
                  className="flex items-center justify-center h-full w-full"
                  style={{ backfaceVisibility: 'hidden' }}
                >
                  <span className="text-lg font-semibold text-center px-2 leading-tight">
                    {getCardContent(card)}
                  </span>
                </motion.div>
              </button>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Game Complete Modal */}
      <AnimatePresence>
        {showResult && game.is_completed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-white rounded-xl p-8 max-w-md w-full mx-4"
            >
              <div className="text-center">
                <div className="text-6xl mb-4">🎉</div>
                <h3 className="text-2xl font-bold text-gray-800 mb-4">
                  ¡Felicitaciones!
                </h3>
                <p className="text-gray-600 mb-6">
                  Has completado el juego Memory Molecular
                </p>
                
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <div className="font-semibold text-blue-800">{game.score}</div>
                    <div className="text-sm text-blue-600">Puntos</div>
                  </div>
                  <div className="bg-green-50 p-3 rounded-lg">
                    <div className="font-semibold text-green-800">
                      {formatTime(game.time_elapsed || 0)}
                    </div>
                    <div className="text-sm text-green-600">Tiempo</div>
                  </div>
                  <div className="bg-purple-50 p-3 rounded-lg">
                    <div className="font-semibold text-purple-800">{game.attempts}</div>
                    <div className="text-sm text-purple-600">Intentos</div>
                  </div>
                  <div className="bg-orange-50 p-3 rounded-lg">
                    <div className="font-semibold text-orange-800">
                      {Math.round((game.pairs_found / game.attempts) * 100)}%
                    </div>
                    <div className="text-sm text-orange-600">Precisión</div>
                  </div>
                </div>
                
                <button
                  onClick={() => {
                    setShowResult(false);
                    setGameStarted(false);
                    setGame(null);
                  }}
                  className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-600 hover:to-purple-700 transition-all duration-200"
                >
                  Jugar de Nuevo
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Quit Game Button */}
      <div className="mt-6 text-center">

      </div>
    </div>
  );
};

export default MemoryGame;