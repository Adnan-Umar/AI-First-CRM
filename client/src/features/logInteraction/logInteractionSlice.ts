import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'

import type { RootState } from '../../app/store'
import { apiClient } from '../../services/apiClient'
import type { ChatMessage, InteractionFormState, InteractionMode, VisitType } from './types'

interface LogInteractionState {
  mode: InteractionMode
  form: InteractionFormState
  chat: {
    messages: ChatMessage[]
    sending: boolean
    error: string | null
  }
}

const initialState: LogInteractionState = {
  mode: 'form',
  form: {
    doctorId: 'hcp-001',
    visitType: 'In-person',
    date: '2026-07-11',
    productsDiscussed: '',
    notes: '',
    followUpDate: '',
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
  },
}

const createId = (prefix: string): string =>
  `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`

export const sendChatMessage = createAsyncThunk<
  ChatMessage,
  string,
  { state: RootState; rejectValue: string }
>('logInteraction/sendChatMessage', async (message, { getState, rejectWithValue }) => {
  try {
    const { form } = getState().logInteraction
    const response = await apiClient.post<{ reply: string }>('/ai/chat/messages', {
      message,
      doctor_id: form.doctorId || null,
      visit_type: form.visitType,
      interaction_date: form.date,
      products_discussed: form.productsDiscussed
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean),
      notes: form.notes || null,
      follow_up_date: form.followUpDate || null,
    })

    return {
      id: createId('assistant'),
      role: 'assistant',
      content: response.data.reply,
      createdAt: new Date().toISOString(),
    }
  } catch {
    return rejectWithValue('Unable to reach assistant service. Please try again.')
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
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.chat.sending = true
        state.chat.error = null
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.chat.sending = false
        state.chat.messages.push(action.payload)
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.chat.sending = false
        state.chat.error = action.payload ?? 'Failed to send message.'
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
} = logInteractionSlice.actions

export default logInteractionSlice.reducer
