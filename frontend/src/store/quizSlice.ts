import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '../services/api';

interface Question {
  id: number;
  question_text: string;
  options: string[];
  difficulty: string;
  category: string;
  points: number;
}

interface QuizSession {
  id: number;
  total_questions: number;
  current_question_index: number;
  score: number;
  is_completed: boolean;
  started_at: string;
}

interface QuizAnswer {
  id: number;
  selected_option: number;
  is_correct: boolean;
  time_taken_seconds: number;
  points_earned: number;
  question_data: Question & {
    correct_option: number;
    explanation: string;
  };
}

interface LeaderboardEntry {
  username: string;
  best_score: number;
  total_games: number;
  average_score: number;
  fastest_completion: number | null;
}

interface QuizState {
  currentSession: QuizSession | null;
  currentQuestion: Question | null;
  currentQuestionIndex: number;
  totalQuestions: number;
  score: number;
  timeRemaining: number;
  gameState: 'idle' | 'starting' | 'playing' | 'answering' | 'completed' | 'error';
  lastAnswer: QuizAnswer | null;
  leaderboard: LeaderboardEntry[];
  userStats: LeaderboardEntry | null;
  loading: boolean;
  error: string | null;
}

const initialState: QuizState = {
  currentSession: null,
  currentQuestion: null,
  currentQuestionIndex: 0,
  totalQuestions: 10,
  score: 0,
  timeRemaining: 300, // 5 minutos
  gameState: 'idle',
  lastAnswer: null,
  leaderboard: [],
  userStats: null,
  loading: false,
  error: null,
};

// Async thunks con manejo de errores mejorado
export const startQuizSession = createAsyncThunk(
  'quiz/startSession',
  async (params: { difficulty?: string; category?: string; total_questions?: number }, { rejectWithValue }) => {
    try {
      const response = await api.post('games/quiz/start_session/', params);
      console.log('Start session response:', response); // Debug log
      return response;
    } catch (error: any) {
      console.error('Start session error:', error);
      return rejectWithValue(error.message || 'Error al iniciar sesión');
    }
  }
);

export const getCurrentQuestion = createAsyncThunk(
  'quiz/getCurrentQuestion',
  async (sessionId: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`games/quiz/get_question/?session_id=${sessionId}`);
      console.log('Get question response:', response); // Debug log
      return response;
    } catch (error: any) {
      console.error('Get question error:', error);
      return rejectWithValue(error.message || 'Error al obtener pregunta');
    }
  }
);

export const submitAnswer = createAsyncThunk(
  'quiz/submitAnswer',
  async (params: {
    session_id: number;
    question_id: number;
    selected_option: number;
    time_taken: number;
  }, { rejectWithValue }) => {
    try {
      const response = await api.post('games/quiz/submit_answer/', params);
      console.log('Submit answer response:', response); // Debug log
      return response;
    } catch (error: any) {
      console.error('Submit answer error:', error);
      return rejectWithValue(error.message || 'Error al enviar respuesta');
    }
  }
);

export const fetchLeaderboard = createAsyncThunk(
  'quiz/fetchLeaderboard',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('games/quiz/leaderboard/');
      console.log('Leaderboard response:', response); // Debug log
      return response;
    } catch (error: any) {
      console.error('Leaderboard error:', error);
      return rejectWithValue(error.message || 'Error al obtener clasificación');
    }
  }
);

export const fetchUserStats = createAsyncThunk(
  'quiz/fetchUserStats',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('games/quiz/my_stats/');
      console.log('User stats response:', response); // Debug log
      return response;
    } catch (error: any) {
      console.error('User stats error:', error);
      return rejectWithValue(error.message || 'Error al obtener estadísticas');
    }
  }
);

const quizSlice = createSlice({
  name: 'quiz',
  initialState,
  reducers: {
    resetQuiz: (state) => {
      Object.assign(state, initialState);
    },
    updateTimeRemaining: (state, action: PayloadAction<number>) => {
      state.timeRemaining = action.payload;
    },
    setGameState: (state, action: PayloadAction<QuizState['gameState']>) => {
      state.gameState = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Start Quiz Session
      .addCase(startQuizSession.pending, (state) => {
        state.loading = true;
        state.gameState = 'starting';
        state.error = null;
      })
      .addCase(startQuizSession.fulfilled, (state, action) => {
        state.loading = false;
        console.log('Processing start session payload:', action.payload);
        
        // Manejo seguro de la respuesta - la estructura puede variar
        const payload = action.payload;
        if (payload && payload.success && payload.session) {
          state.currentSession = payload.session;
          state.totalQuestions = payload.session.total_questions;
          state.gameState = 'playing';
          state.timeRemaining = 300; // Reset timer
        } else {
          // Si la respuesta no tiene la estructura esperada, marcar como error
          state.gameState = 'error';
          state.error = payload?.error || 'Estructura de respuesta inesperada';
        }
      })
      .addCase(startQuizSession.rejected, (state, action) => {
        state.loading = false;
        state.gameState = 'error';
        state.error = action.payload as string || action.error.message || 'Error al iniciar quiz';
      })
      
      // Get Current Question
      .addCase(getCurrentQuestion.pending, (state) => {
        state.loading = true;
      })
      .addCase(getCurrentQuestion.fulfilled, (state, action) => {
        state.loading = false;
        console.log('Processing get question payload:', action.payload);
        
        const payload = action.payload;
        if (payload && payload.success && payload.question) {
          state.currentQuestion = payload.question;
          state.currentQuestionIndex = payload.current_index ?? state.currentQuestionIndex;
          state.score = payload.current_score ?? state.score;
        } else {
          state.error = payload?.error || 'No se pudo obtener la pregunta';
        }
      })
      .addCase(getCurrentQuestion.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string || action.error.message || 'Error al obtener pregunta';
      })
      
      // Submit Answer
      .addCase(submitAnswer.pending, (state) => {
        state.gameState = 'answering';
      })
      .addCase(submitAnswer.fulfilled, (state, action) => {
        console.log('Processing submit answer payload:', action.payload);
        
        const payload = action.payload;
        if (payload && payload.success && payload.answer) {
          state.lastAnswer = payload.answer;
          
          // Actualizar puntuación si está disponible
          if (payload.final_score !== undefined) {
            state.score = payload.final_score;
          }
          
          // Verificar si el quiz está completado
          if (payload.session_completed) {
            state.gameState = 'completed';
          } else {
            state.gameState = 'playing';
          }
        } else {
          state.gameState = 'error';
          state.error = payload?.error || 'Error al procesar respuesta';
        }
      })
      .addCase(submitAnswer.rejected, (state, action) => {
        state.gameState = 'error';
        state.error = action.payload as string || action.error.message || 'Error al enviar respuesta';
      })
      
      // Leaderboard
      .addCase(fetchLeaderboard.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchLeaderboard.fulfilled, (state, action) => {
        state.loading = false;
        console.log('Processing leaderboard payload:', action.payload);
        
        const payload = action.payload;
        if (payload && payload.success) {
          // La respuesta puede tener 'leaderboard' o ser un array directamente
          state.leaderboard = payload.leaderboard || payload || [];
        } else {
          state.leaderboard = [];
          state.error = payload?.error || 'Error al cargar clasificación';
        }
      })
      .addCase(fetchLeaderboard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string || action.error.message || 'Error al obtener clasificación';
      })
      
      // User Stats
      .addCase(fetchUserStats.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchUserStats.fulfilled, (state, action) => {
        state.loading = false;
        console.log('Processing user stats payload:', action.payload);
        
        const payload = action.payload;
        if (payload && payload.success) {
          // stats puede ser null si el usuario no tiene estadísticas
          state.userStats = payload.stats || null;
        } else {
          state.userStats = null;
          if (payload?.error) {
            state.error = payload.error;
          }
        }
      })
      .addCase(fetchUserStats.rejected, (state, action) => {
        state.loading = false;
        state.userStats = null;
        state.error = action.payload as string || action.error.message || 'Error al obtener estadísticas';
      });
  },
});

export const { resetQuiz, updateTimeRemaining, setGameState, clearError } = quizSlice.actions;
export default quizSlice.reducer;