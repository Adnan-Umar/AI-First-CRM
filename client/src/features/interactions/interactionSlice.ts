import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'

import { apiClient } from '../../services/apiClient'
import type { Interaction } from './types'

interface InteractionState {
  records: Interaction[]
  loading: boolean
  error: string | null
}

const initialState: InteractionState = {
  records: [],
  loading: false,
  error: null,
}

// Shape returned by backend (snake_case) mapped to frontend camelCase
interface BackendInteraction {
  id: string
  hcp_name: string | null
  channel: string | null
  visit_type: string
  objective: string | null
  summary: string | null
  outcome: string | null
  date: string
  hcp_id: string
  products_discussed: string[]
  notes: string | null
  follow_up_date: string | null
  created_at: string
  updated_at: string
}

function mapInteraction(item: BackendInteraction): Interaction {
  return {
    id: item.id,
    hcpName: item.hcp_name ?? 'Unknown',
    channel: (item.channel as Interaction['channel']) ?? 'In-person',
    objective: item.objective ?? '',
    summary: item.summary ?? '',
    outcome: item.outcome ?? '',
    date: item.date,
  }
}

export const fetchInteractions = createAsyncThunk<
  Interaction[],
  void,
  { rejectValue: string }
>('interactions/fetchAll', async (_, { rejectWithValue }) => {
  try {
    const response = await apiClient.get<BackendInteraction[]>('/interactions')
    return response.data.map(mapInteraction)
  } catch {
    return rejectWithValue('Failed to load interactions.')
  }
})

export interface CreateInteractionPayload {
  hcp_id: string
  visit_type: string
  date: string
  products_discussed: string[]
  notes: string | null
  follow_up_date: string | null
  objective?: string | null
  summary?: string | null
  outcome?: string | null
}

export const createInteraction = createAsyncThunk<
  Interaction,
  CreateInteractionPayload,
  { rejectValue: string }
>('interactions/create', async (payload, { rejectWithValue }) => {
  try {
    const response = await apiClient.post<BackendInteraction>('/interactions', payload)
    return mapInteraction(response.data)
  } catch {
    return rejectWithValue('Failed to save interaction.')
  }
})

const interactionSlice = createSlice({
  name: 'interactions',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.loading = false
        state.records = action.payload
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload ?? 'Unknown error'
      })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.records.unshift(action.payload)
      })
  },
})

export default interactionSlice.reducer
