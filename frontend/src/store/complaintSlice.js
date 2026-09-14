import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  formData: {
    complaint_source: '',
    customer_name: '',
    product_name: '',
    product_strength_grade: '',
    batch_number: '',
    manufacturing_date: '',
    expiry_date: '',
    quantity_affected: '',
    complaint_type: '',
    complaint_date: '',
    detailed_description: '',
    initial_severity: 'Minor',
    priority: 'Low',
  },
  riskAssessment: {
    severity_classification: 'Minor',
    risk_justification: 'Awaiting AI copilot risk assessment...',
    suggested_next_action: 'Awaiting triage...',
    capa_recommendation: '',
    regulatory_impact: 'No immediate recall required',
  },
  isProcessing: false,
};

export const complaintSlice = createSlice({
  name: 'complaint',
  initialState,
  reducers: {
    setProcessing: (state, action) => {
      state.isProcessing = action.payload;
    },
    syncCopilotData: (state, action) => {
      state.formData = { ...state.formData, ...action.payload.form_data };
      if (action.payload.risk_assessment) {
        state.riskAssessment = { ...state.riskAssessment, ...action.payload.risk_assessment };
      }
      state.isProcessing = false;
    },
    resetAll: () => initialState,
  },
});

export const { setProcessing, syncCopilotData, resetAll } = complaintSlice.actions;
export default complaintSlice.reducer;