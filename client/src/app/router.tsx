import { ThemeProvider } from '@mui/material/styles'
import { createBrowserRouter } from 'react-router-dom'

import { CRMLayout } from '../layouts/CRMLayout'
import { DashboardPage } from '../pages/DashboardPage'
import { HCPListPage } from '../pages/HCPListPage'
import { InteractionHistoryPage } from '../pages/InteractionHistoryPage'
import { LogInteractionPage } from '../pages/LogInteractionPage'
import { crmTheme } from './theme'

export const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <ThemeProvider theme={crmTheme}>
        <CRMLayout />
      </ThemeProvider>
    ),
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'hcps', element: <HCPListPage /> },
      { path: 'log-interaction', element: <LogInteractionPage /> },
      { path: 'interaction-history', element: <InteractionHistoryPage /> },
    ],
  },
])
