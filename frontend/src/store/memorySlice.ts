import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

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

interface MemoryState {
  currentGame: MemoryGame | null;
  stats: MemoryStats | null;
  leaderboard: LeaderboardEntry[];
  loading: boolean;
  error: string | null;
  selectedCards: number[];
  isChecking: boolean;
}

const initialState: MemoryState = {
  currentGame: null,
  stats: null,
  leaderboard: [],
  loading: false,
  error: null,
  selectedCards: [],
  isChecking: false,
};

// Async thunks
export const startMemoryGame = createAsyncThunk(
  'memory/startGame',
  async (params: { difficulty: string; total_pairs: number }, { getState }) => {
    const response = await fetch('/api/games/memory/start_game/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(params)
    });

    const data = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Error starting game');
    }
    return data.game;
  }
);

export const revealCard = createAsyncThunk(
  'memory/revealCard',
  async (params: { game_id: number; card_position: number }) => {
    const response = await fetch('/api/games/memory/reveal_card/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(params)
    });

    const data = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Error revealing card');
    }
    return { result: data.result, game: data.game, cardPosition: params.card_position };
  }
);

export const hideCards = createAsyncThunk(
  'memory/hideCards',
  async (game_id: number) => {
    const response = await fetch('/api/games/memory/hide_cards/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({ game_id })
    });

    const data = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Error hiding cards');
    }
    return data.game;
  }
);

export const loadCurrentGame = createAsyncThunk(
  'memory/loadCurrentGame',
  async () => {
    const response = await fetch('/api/games/memory/current_game/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });

    const data = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Error loading current game');
    }
    return data.game;
  }
);

export const loadMemoryStats = createAsyncThunk(
  'memory/loadStats',
  async () => {
    const response = await fetch('/api/games/memory/stats/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });

    const data = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Error loading stats');
    }
    return data.stats;
  }
);

export const loadLeaderboard = createAsyncThunk(
  'memory/loadLeaderboard',
  async () => {
    const response = await fetch('/api/games/memory/leaderboard/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });

    const data = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Error loading leaderboard');
    }
    return data.leaderboard;
  }
);

export const endGame = createAsyncThunk(
  'memory/endGame',
  async () => {
    const response = await fetch('/api/games/memory/end_game/', {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });

    const data = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Error ending game');
    }
    return data;
  }
);

// Slice
const memorySlice = createSlice({
  name: 'memory',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setSelectedCards: (state, action: PayloadAction<number[]>) => {
      state.selectedCards = action.payload;
    },
    setIsChecking: (state, action: PayloadAction<boolean>) => {
      state.isChecking = action.payload;
    },
    resetGame: (state) => {
      state.currentGame = null;
      state.selectedCards = [];
      state.isChecking = false;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Start Game
      .addCase(startMemoryGame.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(startMemoryGame.fulfilled, (state, action) => {
        state.loading = false;
        state.currentGame = action.payload;
        state.selectedCards = [];
        state.isChecking = false;
      })
      .addCase(startMemoryGame.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Error starting game';
      })
      
      // Reveal Card
      .addCase(revealCard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(revealCard.fulfilled, (state, action) => {
        state.loading = false;
        state.currentGame = action.payload.game;
        state.selectedCards.push(action.payload.cardPosition);
        
        // If this was the second card, start checking
        if (state.selectedCards.length === 2) {
          state.isChecking = true;
        }
      })
      .addCase(revealCard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Error revealing card';
      })
      
      // Hide Cards
      .addCase(hideCards.fulfilled, (state, action) => {
        state.currentGame = action.payload;
        state.selectedCards = [];
        state.isChecking = false;
      })
      
      // Load Current Game
      .addCase(loadCurrentGame.fulfilled, (state, action) => {
        state.currentGame = action.payload;
      })
      
      // Load Stats
      .addCase(loadMemoryStats.pending, (state) => {
        state.loading = true;
      })
      .addCase(loadMemoryStats.fulfilled, (state, action) => {
        state.loading = false;
        state.stats = action.payload;
      })
      .addCase(loadMemoryStats.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Error loading stats';
      })
      
      // Load Leaderboard
      .addCase(loadLeaderboard.fulfilled, (state, action) => {
        state.leaderboard = action.payload;
      })
      
      // End Game
      .addCase(endGame.fulfilled, (state) => {
        state.currentGame = null;
        state.selectedCards = [];
        state.isChecking = false;
      });
  },
});

export const { clearError, setSelectedCards, setIsChecking, resetGame } = memorySlice.actions;
export default memorySlice.reducer;