import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../services/api';

export interface BalanceChallengeGame {
  id: number;
  original_equation: string;
  difficulty: 'easy' | 'medium' | 'hard';
  is_completed: boolean;
  is_correct: boolean;
  attempts: number;
  max_attempts: number;
  user_coefficients: number[];
  hints_used: string[];
  started_at: string;
  completed_at?: string;
  time_elapsed: number;
  compounds: {
    reactants: string[];
    products: string[];
    all_compounds: string[];
  };
}

export interface BalanceChallengeAttempt {
  attempt_number: number;
  is_correct: boolean;
  coefficients_submitted: number[];
  validation_result: {
    is_correct: boolean;
    is_balanced: boolean;
    is_exact_match: boolean;
    user_equation: string;
    target_equation: string;
    validation_details?: any;
  };
  time_taken_seconds: number;
}

export interface BalanceChallengeStats {
  username: string;
  games_played: number;
  games_completed: number;
  games_correct: number;
  completion_rate: number;
  accuracy_rate: number;
  easy_completed: number;
  easy_correct: number;
  medium_completed: number;
  medium_correct: number;
  hard_completed: number;
  hard_correct: number;
  average_time_per_game: number;
  best_time_easy?: number;
  best_time_medium?: number;
  best_time_hard?: number;
  current_streak: number;
  best_streak: number;
}

interface BalanceChallengeState {
  currentGame: BalanceChallengeGame | null;
  stats: BalanceChallengeStats | null;
  leaderboard: any[];
  loading: boolean;
  error: string | null;
  hints: Array<{
    type: string;
    message: string;
    timestamp: number;
  }>;
}

const initialState: BalanceChallengeState = {
  currentGame: null,
  stats: null,
  leaderboard: [],
  loading: false,
  error: null,
  hints: [],
};

// Async thunks
export const startChallenge = createAsyncThunk(
  'balanceChallenge/startChallenge',
  async (difficulty: 'easy' | 'medium' | 'hard') => {
    const response = await api.post('/games/balance-challenge/start_challenge/', {
      difficulty,
    });
    console.log('API response for startChallenge:', response); // Debug log
    return response;
  }
);

export const submitCoefficients = createAsyncThunk(
  'balanceChallenge/submitCoefficients',
  async ({
    gameId,
    coefficients,
    timeTaken,
  }: {
    gameId: number;
    coefficients: number[];
    timeTaken: number;
  }) => {
    const response = await api.post('/games/balance-challenge/submit_coefficients/', {
      game_id: gameId,
      coefficients,
      time_taken: timeTaken,
    });
    console.log('API response for submitCoefficients:', response); // Debug log
    return response;
  }
);

export const getHint = createAsyncThunk(
  'balanceChallenge/getHint',
  async ({
    gameId,
    hintType,
  }: {
    gameId: number;
    hintType: 'element' | 'coefficient' | 'method';
  }) => {
    const response = await api.post('/games/balance-challenge/get_hint/', {
      game_id: gameId,
      hint_type: hintType,
    });
    console.log('API response for getHint:', response); // Debug log
    return response;
  }
);

export const getCurrentChallenge = createAsyncThunk(
  'balanceChallenge/getCurrentChallenge',
  async () => {
    const response = await api.get('/games/balance-challenge/current_challenge/');
    console.log('API response for getCurrentChallenge:', response); // Debug log
    return response;
  }
);

export const getChallengeStats = createAsyncThunk(
  'balanceChallenge/getChallengeStats',
  async () => {
    const response = await api.get('/games/balance-challenge/stats/');
    console.log('API response for getChallengeStats:', response); // Debug log
    return response;
  }
);

export const getChallengeLeaderboard = createAsyncThunk(
  'balanceChallenge/getChallengeLeaderboard',
  async () => {
    const response = await api.get('/games/balance-challenge/leaderboard/');
    return response.data;
  }
);

export const endChallenge = createAsyncThunk(
  'balanceChallenge/endChallenge',
  async () => {
    const response = await api.delete('/games/balance-challenge/end_challenge/');
    console.log('API response for endChallenge:', response); // Debug log
    return response;
  }
);

const balanceChallengeSlice = createSlice({
  name: 'balanceChallenge',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    addHint: (state, action) => {
      state.hints.push({
        type: action.payload.type,
        message: action.payload.message,
        timestamp: Date.now(),
      });
    },
    clearHints: (state) => {
      state.hints = [];
    },
    resetGame: (state) => {
      state.currentGame = null;
      state.hints = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Start Challenge
    builder
      .addCase(startChallenge.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(startChallenge.fulfilled, (state, action) => {
        state.loading = false;
        console.log('startChallenge fulfilled with payload:', action.payload); // Debug log
        
        // Handle different response structures
        if (action.payload?.success) {
          // Response with success wrapper
          state.currentGame = action.payload.game;
          state.hints = [];
        } else if (action.payload?.id) {
          // Direct game object response
          state.currentGame = action.payload as BalanceChallengeGame;
          state.hints = [];
        } else if (action.payload?.game) {
          // Response with game property but no success flag
          state.currentGame = action.payload.game;
          state.hints = [];
        } else {
          state.error = action.payload?.error || action.payload?.detail || 'Error al iniciar desafío';
        }
      })
      .addCase(startChallenge.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Error al iniciar desafío';
      });

    // Submit Coefficients
    builder
      .addCase(submitCoefficients.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(submitCoefficients.fulfilled, (state, action) => {
        state.loading = false;
        console.log('submitCoefficients fulfilled with payload:', action.payload); // Debug log
        
        // Handle different response structures
        if (action.payload?.success !== undefined) {
          // Response with success wrapper
          if (action.payload.success) {
            state.currentGame = { ...state.currentGame, ...action.payload.game };
          } else {
            state.error = action.payload.error || 'Error al enviar coeficientes';
          }
        } else if (action.payload?.game) {
          // Direct response with game object
          state.currentGame = { ...state.currentGame, ...action.payload.game };
        } else if (action.payload?.is_correct !== undefined) {
          // Direct attempt response
          if (state.currentGame && action.payload) {
            state.currentGame.attempts = action.payload.attempt_number || state.currentGame.attempts + 1;
            if (action.payload.is_correct || action.payload.game_completed) {
              state.currentGame.is_completed = true;
              state.currentGame.is_correct = true;
            }
          }
        } else {
          state.error = action.payload?.error || action.payload?.detail || 'Error al enviar coeficientes';
        }
      })
      .addCase(submitCoefficients.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Error al enviar coeficientes';
      });

    // Get Hint
    builder
      .addCase(getHint.pending, (state) => {
        state.loading = true;
      })
      .addCase(getHint.fulfilled, (state, action) => {
        state.loading = false;
        console.log('getHint fulfilled with payload:', action.payload); // Debug log
        
        if (action.payload?.success) {
          // Response with success wrapper
          state.hints.push({
            type: action.payload.hint_type,
            message: action.payload.hint,
            timestamp: Date.now(),
          });
        } else if (action.payload?.hint) {
          // Direct hint response
          state.hints.push({
            type: action.payload.hint_type || 'general',
            message: action.payload.hint,
            timestamp: Date.now(),
          });
        }
      })
      .addCase(getHint.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Error al obtener pista';
      });

    // Get Current Challenge
    builder
      .addCase(getCurrentChallenge.pending, (state) => {
        state.loading = true;
      })
      .addCase(getCurrentChallenge.fulfilled, (state, action) => {
        state.loading = false;
        console.log('getCurrentChallenge fulfilled with payload:', action.payload); // Debug log
        
        if (action.payload?.success) {
          // Response with success wrapper
          state.currentGame = action.payload.game;
        } else if (action.payload?.id) {
          // Direct game object
          state.currentGame = action.payload as BalanceChallengeGame;
        } else if (action.payload?.game) {
          // Response with game property
          state.currentGame = action.payload.game;
        }
      })
      .addCase(getCurrentChallenge.rejected, (state, action) => {
        state.loading = false;
        // No set error here as this is expected when no game exists
        console.log('No current challenge or error loading it');
      });

    // Get Stats
    builder
      .addCase(getChallengeStats.pending, (state) => {
        state.loading = true;
      })
      .addCase(getChallengeStats.fulfilled, (state, action) => {
        state.loading = false;
        console.log('getChallengeStats fulfilled with payload:', action.payload); // Debug log
        
        if (action.payload?.success) {
          // Response with success wrapper
          state.stats = action.payload.stats;
        } else if (action.payload?.username || action.payload?.games_played !== undefined) {
          // Direct stats object
          state.stats = action.payload as BalanceChallengeStats;
        } else if (action.payload?.stats) {
          // Response with stats property
          state.stats = action.payload.stats;
        }
      })
      .addCase(getChallengeStats.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Error al cargar estadísticas';
      });

    // Get Leaderboard
    builder
      .addCase(getChallengeLeaderboard.pending, (state) => {
        state.loading = true;
      })
      .addCase(getChallengeLeaderboard.fulfilled, (state, action) => {
        state.loading = false;
        if (action.payload?.success) {
          state.leaderboard = action.payload.leaderboard;
        }
      })
      .addCase(getChallengeLeaderboard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Error al cargar tabla de posiciones';
      });

    // End Challenge
    builder
      .addCase(endChallenge.pending, (state) => {
        state.loading = true;
      })
      .addCase(endChallenge.fulfilled, (state, action) => {
        state.loading = false;
        console.log('endChallenge fulfilled with payload:', action.payload); // Debug log
        
        // For DELETE requests, success can be indicated by null response or success flag
        if (action.payload === null || action.payload?.success || action.payload?.message) {
          state.currentGame = null;
          state.hints = [];
        } else if (action.payload?.error || action.payload?.detail) {
          state.error = action.payload.error || action.payload.detail;
        }
      })
      .addCase(endChallenge.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Error al finalizar desafío';
      });
  },
});

export const { clearError, addHint, clearHints, resetGame } = balanceChallengeSlice.actions;
export default balanceChallengeSlice.reducer;