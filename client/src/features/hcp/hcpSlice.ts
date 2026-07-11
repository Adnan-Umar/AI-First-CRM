import { createSlice } from '@reduxjs/toolkit'

import type { HCP } from './types'

interface HCPState {
  records: HCP[]
}

const initialState: HCPState = {
  records: [
    {
      id: 'hcp-001',
      fullName: 'Dr. Sarah Khan',
      specialty: 'Cardiology',
      organization: 'City Heart Institute',
      city: 'Lahore',
      lastInteraction: '2026-07-09',
    },
    {
      id: 'hcp-002',
      fullName: 'Dr. Ali Raza',
      specialty: 'Internal Medicine',
      organization: 'MedCare Hospital',
      city: 'Karachi',
      lastInteraction: '2026-07-10',
    },
    {
      id: 'hcp-003',
      fullName: 'Dr. Maryam Nadeem',
      specialty: 'Endocrinology',
      organization: 'Wellness Clinic',
      city: 'Islamabad',
      lastInteraction: '2026-07-08',
    },
  ],
}

const hcpSlice = createSlice({
  name: 'hcps',
  initialState,
  reducers: {},
})

export default hcpSlice.reducer
