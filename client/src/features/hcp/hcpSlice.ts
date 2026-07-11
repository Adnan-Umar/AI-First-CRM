import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'

import { apiClient } from '../../services/apiClient'
import type { HCP } from './types'

interface HCPState {
  records: HCP[]
  loading: boolean
  error: string | null
}

const initialState: HCPState = {
  records: [],
  loading: false,
  error: null,
}

interface BackendHCP {
  id: string
  first_name: string
  last_name: string
  full_name: string
  specialty: string
  organization_id: string | null
  organization_name: string | null
  city: string | null
  created_at: string
  updated_at: string
}

export const fetchHCPs = createAsyncThunk<HCP[], void, { rejectValue: string }>(
  'hcps/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get<BackendHCP[]>('/hcps')
      return response.data.map((hcp) => ({
        id: hcp.id,
        fullName: hcp.full_name ?? `${hcp.first_name} ${hcp.last_name}`.trim(),
        specialty: hcp.specialty,
        organization: hcp.organization_name ?? '',
        city: hcp.city ?? '',
        lastInteraction: '',
      }))
    } catch {
      return rejectWithValue('Failed to load healthcare professionals.')
    }
  },
)

const hcpSlice = createSlice({
  name: 'hcps',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchHCPs.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchHCPs.fulfilled, (state, action) => {
        state.loading = false
        state.records = action.payload
      })
      .addCase(fetchHCPs.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload ?? 'Unknown error'
      })
  },
})

export default hcpSlice.reducer
