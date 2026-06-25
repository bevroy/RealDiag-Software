/**
 * Settings Redux Slice
 */
import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {SettingsState, AppConfig} from '../../types';
import {API_BASE_URL, API_TIMEOUT, SESSION_TIMEOUT, MAX_OFFLINE_RULES} from '../../constants';

const initialState: SettingsState = {
  config: {
    apiBaseUrl: API_BASE_URL,
    apiTimeout: API_TIMEOUT,
    offlineEnabled: true,
    biometricEnabled: true,
    sessionTimeout: SESSION_TIMEOUT,
    maxOfflineRules: MAX_OFFLINE_RULES,
  },
  theme: 'light',
  notifications: {
    enabled: true,
    types: ['alerts', 'updates'],
  },
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    updateConfig: (state, action: PayloadAction<Partial<AppConfig>>) => {
      state.config = {...state.config, ...action.payload};
    },
    setTheme: (state, action: PayloadAction<'light' | 'dark' | 'auto'>) => {
      state.theme = action.payload;
    },
    setNotifications: (
      state,
      action: PayloadAction<{enabled: boolean; types: string[]}>,
    ) => {
      state.notifications = action.payload;
    },
  },
});

export const {updateConfig, setTheme, setNotifications} = settingsSlice.actions;
export default settingsSlice.reducer;
