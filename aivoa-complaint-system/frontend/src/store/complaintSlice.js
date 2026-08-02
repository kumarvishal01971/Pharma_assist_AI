import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { api } from '../api/client'

const emptyForm = {
  complaint_source: '',
  customer_name: '',
  product_name: '',
  product_strength_grade: '',
  batch_lot_number: '',
  manufacturing_date: '',
  expiry_date: '',
  quantity_affected: '',
  complaint_type: '',
  complaint_date: '',
  detailed_description: '',
  initial_severity: '',
  priority: '',
}

const initialState = {
  form: emptyForm,
  savedComplaintId: null,
  status: 'Pending Triage',

  // AI extraction state
  extractionStatus: 'idle', // idle | loading | succeeded | failed
  extractionProgressLabel: '',
  extractionError: null,
  completenessScore: null,
  missingFields: [],
  aiRiskClassification: null,
  aiRiskRationale: null,
  aiSummary: null,
  extractionConfidence: null,
  possibleDuplicateIds: [],

  // Save state
  saveStatus: 'idle',
  saveError: null,

  // Chat
  chatMessages: [
    {
      role: 'assistant',
      content:
        'Upload a complaint document or paste text above. I will automatically extract the details and populate the form for you.',
    },
  ],
  chatStatus: 'idle',
}

export const extractFromText = createAsyncThunk(
  'complaint/extractFromText',
  async (text) => api.extractFromText(text)
)

export const extractFromFile = createAsyncThunk(
  'complaint/extractFromFile',
  async (file) => api.extractFromFile(file)
)

export const saveComplaint = createAsyncThunk(
  'complaint/saveComplaint',
  async (_, { getState }) => {
    const { form } = getState().complaint
    // omit empty-string fields so the backend gets nulls, not ""
    const cleaned = Object.fromEntries(
      Object.entries(form).map(([k, v]) => [k, v === '' ? null : v])
    )
    return api.saveComplaint(cleaned)
  }
)

export const sendChatMessage = createAsyncThunk(
  'complaint/sendChatMessage',
  async (message, { getState }) => {
    const { savedComplaintId } = getState().complaint
    const reply = await api.chat(message, savedComplaintId)
    return reply.reply
  }
)

const complaintSlice = createSlice({
  name: 'complaint',
  initialState,
  reducers: {
    setField(state, action) {
      const { field, value } = action.payload
      state.form[field] = value
    },
    resetForm() {
      return initialState
    },
  },
  extraReducers: (builder) => {
    builder
      // --- Extraction (shared by text + file paths) ---
      .addCase(extractFromText.pending, (state) => {
        state.extractionStatus = 'loading'
        state.extractionProgressLabel = 'Analyzing complaint text and extracting key details...'
        state.extractionError = null
      })
      .addCase(extractFromFile.pending, (state) => {
        state.extractionStatus = 'loading'
        state.extractionProgressLabel = 'Analyzing document content and extracting key details...'
        state.extractionError = null
      })

      // --- Save ---
      .addCase(saveComplaint.pending, (state) => {
        state.saveStatus = 'loading'
        state.saveError = null
      })
      .addCase(saveComplaint.fulfilled, (state, action) => {
        state.saveStatus = 'succeeded'
        state.savedComplaintId = action.payload.id
        state.status = action.payload.status
      })
      .addCase(saveComplaint.rejected, (state, action) => {
        state.saveStatus = 'failed'
        state.saveError = action.error.message
      })

      // --- Chat ---
      .addCase(sendChatMessage.pending, (state, action) => {
        state.chatStatus = 'loading'
        state.chatMessages.push({ role: 'user', content: action.meta.arg })
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.chatStatus = 'idle'
        state.chatMessages.push({ role: 'assistant', content: action.payload })
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.chatStatus = 'idle'
        state.chatMessages.push({
          role: 'assistant',
          content: `Sorry, something went wrong: ${action.error.message}`,
        })
      })
      .addMatcher(
        (action) => action.type.endsWith('/fulfilled') && action.type.startsWith('complaint/extract'),
        (state, action) => {
          const result = action.payload
          state.extractionStatus = 'succeeded'
          state.form = {
            ...state.form,
            ...Object.fromEntries(
              Object.entries(result.extracted).map(([k, v]) => [k, v ?? ''])
            ),
          }
          state.status = 'Pending Triage'
          state.completenessScore = result.completeness_score
          state.missingFields = result.missing_fields
          state.aiRiskClassification = result.ai_risk_classification
          state.aiRiskRationale = result.ai_risk_rationale
          state.aiSummary = result.ai_summary
          state.extractionConfidence = result.extraction_confidence
          state.possibleDuplicateIds = result.possible_duplicate_ids
        }
      )
      .addMatcher(
        (action) => action.type.endsWith('/rejected') && action.type.startsWith('complaint/extract'),
        (state, action) => {
          state.extractionStatus = 'failed'
          state.extractionError = action.error.message
        }
      )
  },
})

export const { setField, resetForm } = complaintSlice.actions
export default complaintSlice.reducer
