import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import moleculesReducer from './moleculesSlice';
import notificationsReducer from './notificationsSlice';
import filterReducer from './filterSlice';
import calculatorsReducer from './calculatorsSlice';
import quizReducer from './quizSlice';

import chemWordleReducer from './chemWordleSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    molecules: moleculesReducer,
    notifications: notificationsReducer,
    filters: filterReducer, 
    calculators: calculatorsReducer,
    quiz: quizReducer,
    chemWordle: chemWordleReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;