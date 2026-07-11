import { createSlice } from '@reduxjs/toolkit'

import type { Interaction } from './types'

interface InteractionState {
  records: Interaction[]
}

const initialState: InteractionState = {
  records: [
    {
      id: 'int-1001',
      hcpName: 'Dr. Sarah Khan',
      channel: 'In-person',
      objective: 'Discuss adherence outcomes',
      summary: 'HCP requested patient success data for diabetic patients.',
      outcome: 'Follow-up planned with clinical deck.',
      date: '2026-07-10',
    },
    {
      id: 'int-1002',
      hcpName: 'Dr. Ali Raza',
      channel: 'Call',
      objective: 'Product positioning review',
      summary: 'Compared treatment protocol against competitor option.',
      outcome: 'Requested comparative efficacy sheet.',
      date: '2026-07-09',
    },
    {
      id: 'int-1003',
      hcpName: 'Dr. Maryam Nadeem',
      channel: 'Video',
      objective: 'Plan educational session',
      summary: 'Aligned on workshop dates and attendee mix.',
      outcome: 'Pending final confirmation from clinic manager.',
      date: '2026-07-08',
    },
  ],
}

const interactionSlice = createSlice({
  name: 'interactions',
  initialState,
  reducers: {},
})

export default interactionSlice.reducer
