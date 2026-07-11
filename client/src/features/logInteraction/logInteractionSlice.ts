import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'

import type { AppDispatch, RootState } from '../../app/store'
import { createInteraction } from '../interactions/interactionSlice'
import { apiClient } from '../../services/apiClient'
import type {
  ChatApiResponse,
  ChatMessage,
  ExtractedFields,
  InteractionFormState,
  InteractionMode,
  VisitType,
} from './types'

interface LogInteractionState {
  mode: InteractionMode
  form: InteractionFormState
  chat: {
    messages: ChatMessage[]
    sending: boolean
    error: string | null
    lastIntent: string | null
    lastIntentLabel: string | null
  }
  save: {
    saving: boolean
    error: string | null
    savedId: string | null
  }
}

const initialState: LogInteractionState = {
  mode: 'form',
  form: {
    doctorId: '',
    visitType: 'In-person',
    date: new Date().toISOString().slice(0, 10),
    productsDiscussed: '',
    notes: '',
    followUpDate: '',
    objective: '',
    summary: '',
    outcome: '',
  },
  chat: {
    messages: [
      {
        id: 'assistant-welcome',
        role: 'assistant',
        content:
          'Hello! Share the interaction details, and I will help you structure notes for CRM logging.',
        createdAt: new Date().toISOString(),
      },
    ],
    sending: false,
    error: null,
    lastIntent: null,
    lastIntentLabel: null,
  },
  save: {
    saving: false,
    error: null,
    savedId: null,
  },
}

const createId = (prefix: string): string =>
  `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`

export function mergeExtractedFields(
  form: InteractionFormState,
  fields: ExtractedFields,
): InteractionFormState {
  return {
    doctorId: fields.doctorId || form.doctorId,
    visitType: (fields.visitType as VisitType) || form.visitType,
    date: fields.date || form.date,
    productsDiscussed:
      fields.productsDiscussed !== undefined ? fields.productsDiscussed : form.productsDiscussed,
    notes: fields.notes !== undefined ? fields.notes : form.notes,
    followUpDate: fields.followUpDate !== undefined ? fields.followUpDate : form.followUpDate,
    objective: fields.objective !== undefined ? fields.objective : form.objective,
    summary: fields.summary !== undefined ? fields.summary : form.summary,
    outcome: fields.outcome !== undefined ? fields.outcome : form.outcome,
  }
}

export function buildInteractionPayload(form: InteractionFormState) {
  return {
    hcp_id: form.doctorId,
    visit_type: form.visitType,
    date: form.date,
    products_discussed: form.productsDiscussed
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean),
    notes: form.notes || null,
    follow_up_date: form.followUpDate ? form.followUpDate : null,
    objective: form.objective || null,
    summary: form.summary || null,
    outcome: form.outcome || null,
  }
}

export const sendChatMessage = createAsyncThunk<
  {
    message: ChatMessage
    extractedFields: ExtractedFields | null
    intent: string | null
    intentLabel: string | null
    savedId: string | null
    saveError: string | null
    mergedForm: InteractionFormState | null
  },
  string,
  { state: RootState; rejectValue: string; dispatch: AppDispatch }
>('logInteraction/sendChatMessage', async (message, { getState, rejectWithValue, dispatch }) => {
  try {
    const { form } = getState().logInteraction
    const response = await apiClient.post<ChatApiResponse>('/ai/chat/messages', {
      message,
      doctor_id: form.doctorId || null,
      visit_type: form.visitType,
      interaction_date: form.date || null,
      products_discussed: form.productsDiscussed
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean),
      notes: form.notes || null,
      follow_up_date: form.followUpDate || null,
    })

    const extractedFields = response.data.extracted_fields ?? null
    const intent = response.data.intent ?? extractedFields?.intent ?? null
    const intentLabel = extractedFields?.intentLabel ?? null

    let savedId: string | null = null
    let saveError: string | null = null
    let mergedForm: InteractionFormState | null = null

    if (intent === 'log_interaction' && extractedFields) {
      mergedForm = mergeExtractedFields(form, extractedFields)

      if (mergedForm.doctorId && mergedForm.date) {
        try {
          savedId = await dispatch(saveInteraction(mergedForm)).unwrap()
        } catch {
          saveError =
            'Interaction details were extracted but could not be saved. Review the form and try again.'
        }
      } else {
        saveError =
          'Missing doctor or date in the extracted details. Switch to Form Mode to complete and save manually.'
      }
    }

    return {
      message: {
        id: createId('assistant'),
        role: 'assistant',
        content: response.data.reply,
        createdAt: new Date().toISOString(),
      },
      extractedFields,
      intent,
      intentLabel,
      savedId,
      saveError,
      mergedForm,
    }
  } catch {
    return rejectWithValue('Unable to reach assistant service. Please try again.')
  }
})

export const saveInteraction = createAsyncThunk<
  string,
  Partial<InteractionFormState> | void,
  { state: RootState; rejectValue: string; dispatch: AppDispatch }
>('logInteraction/saveInteraction', async (formOverride, { getState, rejectWithValue, dispatch }) => {
  try {
    const form = {
      ...getState().logInteraction.form,
      ...(formOverride ?? {}),
    }

    if (!form.doctorId || !form.date) {
      return rejectWithValue('Doctor and date are required to save an interaction.')
    }

    return await dispatch(createInteraction(buildInteractionPayload(form))).unwrap().then(
      (interaction) => interaction.id,
    )
  } catch {
    return rejectWithValue('Failed to save interaction. Please try again.')
  }
})

const logInteractionSlice = createSlice({
  name: 'logInteraction',
  initialState,
  reducers: {
    setMode(state, action: PayloadAction<InteractionMode>) {
      state.mode = action.payload
    },
    setDoctorId(state, action: PayloadAction<string>) {
      state.form.doctorId = action.payload
    },
    setVisitType(state, action: PayloadAction<VisitType>) {
      state.form.visitType = action.payload
    },
    setDate(state, action: PayloadAction<string>) {
      state.form.date = action.payload
    },
    setProductsDiscussed(state, action: PayloadAction<string>) {
      state.form.productsDiscussed = action.payload
    },
    setNotes(state, action: PayloadAction<string>) {
      state.form.notes = action.payload
    },
    setFollowUpDate(state, action: PayloadAction<string>) {
      state.form.followUpDate = action.payload
    },
    addUserMessage(state, action: PayloadAction<string>) {
      state.chat.messages.push({
        id: createId('user'),
        role: 'user',
        content: action.payload,
        createdAt: new Date().toISOString(),
      })
      state.chat.error = null
    },
    resetSave(state) {
      state.save.saving = false
      state.save.error = null
      state.save.savedId = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.chat.sending = true
        state.chat.error = null
        state.save.error = null
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.chat.sending = false
        state.chat.messages.push(action.payload.message)
        state.chat.lastIntent = action.payload.intent
        state.chat.lastIntentLabel = action.payload.intentLabel

        if (action.payload.intent === 'log_interaction') {
          if (action.payload.mergedForm) {
            state.form = action.payload.mergedForm
          } else if (action.payload.extractedFields) {
            state.form = mergeExtractedFields(state.form, action.payload.extractedFields)
          }
        }

        if (action.payload.savedId) {
          state.save.savedId = action.payload.savedId
          state.save.error = null
        } else if (action.payload.saveError) {
          state.save.error = action.payload.saveError
        }
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.chat.sending = false
        state.chat.error = action.payload ?? 'Failed to send message.'
      })
      .addCase(saveInteraction.pending, (state) => {
        state.save.saving = true
        state.save.error = null
        state.save.savedId = null
      })
      .addCase(saveInteraction.fulfilled, (state, action) => {
        state.save.saving = false
        state.save.savedId = action.payload
        const formOverride = action.meta.arg
        if (formOverride) {
          state.form = { ...state.form, ...formOverride }
        }
      })
      .addCase(saveInteraction.rejected, (state, action) => {
        state.save.saving = false
        state.save.error = action.payload ?? 'Failed to save.'
      })
  },
})

export const {
  setMode,
  setDoctorId,
  setVisitType,
  setDate,
  setProductsDiscussed,
  setNotes,
  setFollowUpDate,
  addUserMessage,
  resetSave,
} = logInteractionSlice.actions

export default logInteractionSlice.reducer
