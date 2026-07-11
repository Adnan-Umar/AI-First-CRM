import { createTheme } from '@mui/material/styles'

export const crmTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0f4c81',
    },
    secondary: {
      main: '#2f8f9d',
    },
    background: {
      default: '#f5f7fb',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: 'Inter, Roboto, "Helvetica Neue", Arial, sans-serif',
    h4: {
      fontWeight: 700,
    },
    h6: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 10,
  },
})
