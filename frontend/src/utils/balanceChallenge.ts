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

export interface BalanceChallengeLeaderboardEntry {
  rank: number;
  username: string;
  games_played: number;
  games_correct: number;
  accuracy_rate: number;
  best_streak: number;
  current_streak: number;
  average_time: number;
}