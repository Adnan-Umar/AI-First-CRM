import { configureStore } from '@reduxjs/toolkit'

import hcpReducer from '../features/hcp/hcpSlice'
import interactionReducer from '../features/interactions/interactionSlice'
import logInteractionReducer from '../features/logInteraction/logInteractionSlice'

export const store = configureStore({
  reducer: {
    hcps: hcpReducer,
    interactions: interactionReducer,
    logInteraction: logInteractionReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
