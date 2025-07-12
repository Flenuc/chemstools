import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import moleculesReducer from './moleculesSlice';
import notificationsReducer from './notificationsSlice';
import filterReducer from './filterSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    molecules: moleculesReducer,
    notifications: notificationsReducer,
    filters: filterReducer, 
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;