import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import moleculesReducer from './moleculesSlice';
import notificationsReducer from './notificationsSlice';
import filterReducer from './filterSlice';
import calculatorsReducer from './calculatorsSlice';
import quizReducer from './quizSlice';
import chemWordleReducer from './chemWordleSlice';
import memoryReducer from './memorySlice';
import balanceChallengeReducer from './balanceChallengeSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    molecules: moleculesReducer,
    notifications: notificationsReducer,
    filters: filterReducer, 
    calculators: calculatorsReducer,
    quiz: quizReducer,
    chemWordle: chemWordleReducer,
    memory: memoryReducer,
    balanceChallenge: balanceChallengeReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;