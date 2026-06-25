/**
 * Diagnostics Redux Slice
 */
import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {DiagnosticsState, SearchResult, DiagnosticTree} from '../../types';

const initialState: DiagnosticsState = {
  searchResults: [],
  selectedDiagnosis: null,
  isSearching: false,
  error: null,
  offlineRules: [],
};

const diagnosticsSlice = createSlice({
  name: 'diagnostics',
  initialState,
  reducers: {
    setSearching: (state, action: PayloadAction<boolean>) => {
      state.isSearching = action.payload;
    },
    setSearchResults: (state, action: PayloadAction<SearchResult[]>) => {
      state.searchResults = action.payload;
      state.isSearching = false;
      state.error = null;
    },
    setSelectedDiagnosis: (state, action: PayloadAction<DiagnosticTree | null>) => {
      state.selectedDiagnosis = action.payload;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isSearching = false;
    },
    clearSearch: state => {
      state.searchResults = [];
      state.selectedDiagnosis = null;
      state.error = null;
    },
  },
});

export const {
  setSearching,
  setSearchResults,
  setSelectedDiagnosis,
  setError,
  clearSearch,
} = diagnosticsSlice.actions;
export default diagnosticsSlice.reducer;
