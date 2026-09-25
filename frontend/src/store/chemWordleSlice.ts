import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '../services/api';

interface LetterResult {
  letter: string;
  state: 'correct' | 'present' | 'absent';
}

interface GuessResult {
  word: string;
  results: LetterResult[];
  attempt: number;
}

interface ChemWordleGame {
  id: number;
  target_word: {
    id: number;
    category: string;
    difficulty: string;
    hint: string;
    atomic_number?: number;
    group_number?: number;
    period_number?: number;
    state_at_stp?: string;
    chemical_formula?: string;
    molecular_weight?: number;
    word?: string; // Solo disponible cuando el juego está completado
  };
  is_completed: boolean;
  is_won: boolean;
  attempts_used: number;
  max_attempts: number;
  guesses: GuessResult[];
  hints_revealed: number[];
  started_at: string;
  word_length: number;
}

interface ChemWordleAttempt {
  id: number;
  attempt_number: number;
  guessed_word: string;
  letter_results: LetterResult[];
  time_taken_seconds: number;
}

interface ChemWordleStats {
  games_played: number;
  games_won: number;
  win_percentage: number;
  current_streak: number;
  max_streak: number;
  win_distribution: Record<string, number>;
  best_time_seconds?: number;
}

interface LeaderboardEntry {
  rank: number;
  username: string;
  games_played: number;
  games_won: number;
  win_percentage: number;
  current_streak: number;
  max_streak: number;
}

interface ChemWordleState {
  currentGame: ChemWordleGame | null;
  currentGuess: string;
  gameState: 'idle' | 'playing' | 'submitting' | 'completed' | 'error';
  stats: ChemWordleStats | null;
  leaderboard: LeaderboardEntry[];
  currentHint: string | null;
  hintsUsed: number;
  gameStartTime: number;
  loading: boolean;
  error: string | null;
  keyboardState: Record<string, 'correct' | 'present' | 'absent' | 'unused'>;
}

const initialState: ChemWordleState = {
  currentGame: null,
  currentGuess: '',
  gameState: 'idle',
  stats: null,
  leaderboard: [],
  currentHint: null,
  hintsUsed: 0,
  gameStartTime: 0,
  loading: false,
  error: null,
  keyboardState: {},
};

// Async thunks
export const startChemWordleGame = createAsyncThunk(
  'chemWordle/startGame',
  async ({ difficulty }: { difficulty?: string } = {}, { rejectWithValue }) => {
    try {
      const params = difficulty ? `?difficulty=${difficulty}` : '';
      const response = await api.get(`games/chemwordle/start_game/${params}`);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Error al iniciar juego');
    }
  }
);

export const submitGuess = createAsyncThunk(
  'chemWordle/submitGuess',
  async (params: { game_id: number; guess: string; time_taken: number }, { rejectWithValue }) => {
    try {
      const response = await api.post('games/chemwordle/submit_guess/', params);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Error al enviar adivinanza');
    }
  }
);

export const getHint = createAsyncThunk(
  'chemWordle/getHint',
  async (params: { game_id: number; hint_level: number }, { rejectWithValue }) => {
    try {
      const response = await api.post('games/chemwordle/get_hint/', params);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Error al obtener pista');
    }
  }
);

export const fetchChemWordleStats = createAsyncThunk(
  'chemWordle/fetchStats',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('games/chemwordle/stats/');
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Error al obtener estadísticas');
    }
  }
);

export const fetchChemWordleLeaderboard = createAsyncThunk(
  'chemWordle/fetchLeaderboard',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('games/chemwordle/leaderboard/');
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Error al obtener clasificación');
    }
  }
);

const chemWordleSlice = createSlice({
  name: 'chemWordle',
  initialState,
  reducers: {
    setCurrentGuess: (state, action: PayloadAction<string>) => {
      if (state.gameState === 'playing') {
        state.currentGuess = action.payload.toUpperCase();
      }
    },
    addLetter: (state, action: PayloadAction<string>) => {
      if (state.gameState === 'playing' && state.currentGame) {
        const letter = action.payload.toUpperCase();
        if (state.currentGuess.length < state.currentGame.word_length) {
          state.currentGuess += letter;
        }
      }
    },
    removeLetter: (state) => {
      if (state.gameState === 'playing') {
        state.currentGuess = state.currentGuess.slice(0, -1);
      }
    },
    resetGame: (state) => {
      Object.assign(state, initialState);
    },
    clearError: (state) => {
      state.error = null;
    },
    updateKeyboardState: (state, action: PayloadAction<LetterResult[]>) => {
      action.payload.forEach(result => {
        const currentState = state.keyboardState[result.letter];
        // Solo actualizar si el nuevo estado es mejor (correct > present > absent)
        if (!currentState || 
            (result.state === 'correct') ||
            (result.state === 'present' && currentState !== 'correct')) {
          state.keyboardState[result.letter] = result.state;
        }
      });
    },
  },
  extraReducers: (builder) => {
    builder
      // Start Game
      .addCase(startChemWordleGame.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(startChemWordleGame.fulfilled, (state, action) => {
        state.loading = false;
        if (action.payload?.success && action.payload?.game) {
          state.currentGame = action.payload.game;
          state.gameState = action.payload.game.is_completed ? 'completed' : 'playing';
          state.gameStartTime = Date.now();
          state.currentGuess = '';
          state.hintsUsed = action.payload.game.hints_revealed?.length || 0;
          
          // Actualizar estado del teclado con intentos previos
          state.keyboardState = {};
          action.payload.game.guesses?.forEach((guess: GuessResult) => {
            guess.results.forEach(result => {
              const currentState = state.keyboardState[result.letter];
              if (!currentState || 
                  (result.state === 'correct') ||
                  (result.state === 'present' && currentState !== 'correct')) {
                state.keyboardState[result.letter] = result.state;
              }
            });
          });
        }
      })
      .addCase(startChemWordleGame.rejected, (state, action) => {
        state.loading = false;
        state.gameState = 'error';
        state.error = action.payload as string;
      })
      
      // Submit Guess
      .addCase(submitGuess.pending, (state) => {
        state.gameState = 'submitting';
      })
      .addCase(submitGuess.fulfilled, (state, action) => {
        if (action.payload?.success) {
          state.currentGame = action.payload.game;
          state.currentGuess = '';
          
          // Actualizar estado del teclado
          if (action.payload.attempt?.letter_results) {
            action.payload.attempt.letter_results.forEach((result: LetterResult) => {
              const currentState = state.keyboardState[result.letter];
              if (!currentState || 
                  (result.state === 'correct') ||
                  (result.state === 'present' && currentState !== 'correct')) {
                state.keyboardState[result.letter] = result.state;
              }
            });
          }
          
          if (action.payload.game_completed) {
            state.gameState = 'completed';
          } else {
            state.gameState = 'playing';
          }
        } else {
          state.gameState = 'playing';
          state.error = action.payload?.error || 'Error al procesar adivinanza';
        }
      })
      .addCase(submitGuess.rejected, (state, action) => {
        state.gameState = 'playing';
        state.error = action.payload as string;
      })
      
      // Get Hint
      .addCase(getHint.fulfilled, (state, action) => {
        if (action.payload?.success) {
          state.currentHint = action.payload.hint;
          state.hintsUsed = action.payload.hints_revealed?.length || state.hintsUsed + 1;
        }
      })
      
      // Fetch Stats
      .addCase(fetchChemWordleStats.fulfilled, (state, action) => {
        if (action.payload?.success) {
          state.stats = action.payload.stats;
        }
      })
      
      // Fetch Leaderboard
      .addCase(fetchChemWordleLeaderboard.fulfilled, (state, action) => {
        if (action.payload?.success) {
          state.leaderboard = action.payload.leaderboard || [];
        }
      });
  },
});

export const {
  setCurrentGuess,
  addLetter,
  removeLetter,
  resetGame,
  clearError,
  updateKeyboardState
} = chemWordleSlice.actions;

export default chemWordleSlice.reducer;