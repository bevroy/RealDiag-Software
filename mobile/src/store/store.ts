/**
 * Redux Store Configuration
 */
import {configureStore} from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import diagnosticsReducer from './slices/diagnosticsSlice';
import patientReducer from './slices/patientSlice';
import settingsReducer from './slices/settingsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    diagnostics: diagnosticsReducer,
    patient: patientReducer,
    settings: settingsReducer,
  },
  middleware: getDefaultMiddleware =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['diagnostics/setSearchResults'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
