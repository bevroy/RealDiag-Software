/**
 * Patient Redux Slice
 */
import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {PatientState, Patient} from '../../types';

const initialState: PatientState = {
  currentPatient: null,
  isLoading: false,
  error: null,
};

const patientSlice = createSlice({
  name: 'patient',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setPatient: (state, action: PayloadAction<Patient>) => {
      state.currentPatient = action.payload;
      state.isLoading = false;
      state.error = null;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    clearPatient: state => {
      state.currentPatient = null;
      state.error = null;
    },
  },
});

export const {setLoading, setPatient, setError, clearPatient} =
  patientSlice.actions;
export default patientSlice.reducer;
