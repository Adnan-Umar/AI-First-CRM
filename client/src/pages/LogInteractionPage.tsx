import { Send as SendIcon } from '@mui/icons-material'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  MenuItem,
  Snackbar,
  Stack,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from '@mui/material'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAppDispatch, useAppSelector } from '../app/hooks'
import { PageHeader } from '../components/PageHeader'
import { fetchHCPs } from '../features/hcp/hcpSlice'
import {
  addUserMessage,
  resetSave,
  saveInteraction,
  sendChatMessage,
  setDate,
  setDoctorId,
  setFollowUpDate,
  setMode,
  setNotes,
  setProductsDiscussed,
  setVisitType,
} from '../features/logInteraction/logInteractionSlice'
import type { InteractionMode, VisitType } from '../features/logInteraction/types'

export function LogInteractionPage() {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const [message, setMessage] = useState('')
  const hcps = useAppSelector((state) => state.hcps.records)
  const hcpsLoading = useAppSelector((state) => state.hcps.loading)
  const { mode, form, chat, save } = useAppSelector((state) => state.logInteraction)

  // Load HCPs on mount and default the doctor selection
  useEffect(() => {
    dispatch(fetchHCPs())
  }, [dispatch])

  useEffect(() => {
    if (!form.doctorId && hcps.length > 0) {
      dispatch(setDoctorId(hcps[0].id))
    }
  }, [hcps, form.doctorId, dispatch])

  // Navigate to history when save succeeds
  useEffect(() => {
    if (save.savedId) {
      navigate('/interaction-history')
      dispatch(resetSave())
    }
  }, [save.savedId, navigate, dispatch])

  const handleSendMessage = () => {
    const trimmed = message.trim()
    if (!trimmed || chat.sending) {
      return
    }
    dispatch(addUserMessage(trimmed))
    dispatch(sendChatMessage(trimmed))
    setMessage('')
  }

  const handleSave = () => {
    dispatch(saveInteraction())
  }

  return (
    <>
      <PageHeader
        title="Log Interaction"
        subtitle="Capture complete interaction context through form entry or AI-assisted notes."
      />
      <Card>
        <Box sx={{ px: 2, pt: 2 }}>
          <ToggleButtonGroup
            value={mode}
            exclusive
            color="primary"
            onChange={(_, value: InteractionMode | null) => {
              if (value) {
                dispatch(setMode(value))
              }
            }}
          >
            <ToggleButton value="form">Form Mode</ToggleButton>
            <ToggleButton value="chat">AI Chat Mode</ToggleButton>
          </ToggleButtonGroup>
        </Box>
        <Divider />
        <CardContent>
          {mode === 'form' ? (
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  select
                  label="Doctor"
                  value={form.doctorId}
                  onChange={(event) => dispatch(setDoctorId(event.target.value))}
                  disabled={hcpsLoading}
                  slotProps={{
                    select: {
                      displayEmpty: true,
                    },
                  }}
                >
                  {hcpsLoading ? (
                    <MenuItem value="" disabled>
                      Loading doctors…
                    </MenuItem>
                  ) : (
                    hcps.map((hcp) => (
                      <MenuItem key={hcp.id} value={hcp.id}>
                        {hcp.fullName}
                      </MenuItem>
                    ))
                  )}
                </TextField>
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  select
                  label="Visit Type"
                  value={form.visitType}
                  onChange={(event) => dispatch(setVisitType(event.target.value as VisitType))}
                >
                  <MenuItem value="In-person">In-person</MenuItem>
                  <MenuItem value="Call">Call</MenuItem>
                  <MenuItem value="Video">Video</MenuItem>
                </TextField>
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Date"
                  type="date"
                  value={form.date}
                  onChange={(event) => dispatch(setDate(event.target.value))}
                  slotProps={{ inputLabel: { shrink: true } }}
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Follow-up Date"
                  type="date"
                  value={form.followUpDate}
                  onChange={(event) => dispatch(setFollowUpDate(event.target.value))}
                  slotProps={{ inputLabel: { shrink: true } }}
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField
                  fullWidth
                  label="Products Discussed"
                  placeholder="Comma-separated values, e.g. CardioPlus, GlucoCare"
                  value={form.productsDiscussed}
                  onChange={(event) => dispatch(setProductsDiscussed(event.target.value))}
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField
                  fullWidth
                  multiline
                  minRows={4}
                  label="Notes"
                  value={form.notes}
                  onChange={(event) => dispatch(setNotes(event.target.value))}
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Button
                    variant="contained"
                    onClick={handleSave}
                    disabled={save.saving || !form.doctorId || !form.date}
                    startIcon={save.saving ? <CircularProgress size={16} color="inherit" /> : undefined}
                  >
                    {save.saving ? 'Saving…' : 'Save Interaction'}
                  </Button>
                  {save.error && (
                    <Typography variant="body2" color="error">
                      {save.error}
                    </Typography>
                  )}
                </Box>
              </Grid>
            </Grid>
          ) : (
            <Stack spacing={2}>
              {chat.lastIntentLabel && (
                <Chip
                  size="small"
                  label={`Tool: ${chat.lastIntentLabel}`}
                  color={chat.lastIntent === 'log_interaction' ? 'primary' : 'default'}
                  sx={{ alignSelf: 'flex-start' }}
                />
              )}
              <Box
                sx={{
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 2,
                  p: 2,
                  minHeight: 220,
                  bgcolor: 'grey.50',
                  position: 'relative',
                }}
              >
                {chat.sending && (
                  <Box
                    sx={{
                      position: 'absolute',
                      inset: 0,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: 'rgba(255,255,255,0.7)',
                      borderRadius: 2,
                      zIndex: 1,
                    }}
                  >
                    <CircularProgress size={28} />
                  </Box>
                )}
                <Stack spacing={1.5}>
                  {chat.messages.map((item) => (
                    <Box
                      key={item.id}
                      sx={{
                        alignSelf: item.role === 'user' ? 'flex-end' : 'flex-start',
                        maxWidth: '80%',
                        px: 1.5,
                        py: 1,
                        borderRadius: 2,
                        bgcolor: item.role === 'user' ? 'primary.main' : 'background.paper',
                        color: item.role === 'user' ? 'primary.contrastText' : 'text.primary',
                        border: item.role === 'assistant' ? '1px solid' : 'none',
                        borderColor: 'divider',
                      }}
                    >
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                        {item.content}
                      </Typography>
                    </Box>
                  ))}
                </Stack>
              </Box>
              {save.savedId && mode === 'chat' && (
                <Alert severity="success" variant="outlined">
                  Interaction saved to the database. Redirecting to history…
                </Alert>
              )}
              {chat.error && (
                <Alert severity="error" variant="outlined">
                  {chat.error}
                </Alert>
              )}
              {save.error && (
                <Alert severity="warning" variant="outlined">
                  {save.error}
                </Alert>
              )}
              <Stack direction="row" spacing={1}>
                <TextField
                  fullWidth
                  label="Type your message"
                  placeholder="e.g. Met Dr. Khan today to discuss CardioPlus…"
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' && !event.shiftKey) {
                      event.preventDefault()
                      handleSendMessage()
                    }
                  }}
                  disabled={chat.sending}
                />
                <Button
                  variant="contained"
                  endIcon={chat.sending ? <CircularProgress size={16} color="inherit" /> : <SendIcon />}
                  onClick={handleSendMessage}
                  disabled={chat.sending || save.saving}
                >
                  {chat.sending ? 'Processing…' : 'Send'}
                </Button>
              </Stack>
              <Divider />
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  onClick={handleSave}
                  disabled={save.saving || chat.sending || !form.doctorId || !form.date}
                  startIcon={save.saving ? <CircularProgress size={16} color="inherit" /> : undefined}
                >
                  {save.saving ? 'Saving…' : 'Save Interaction Manually'}
                </Button>
                <Typography variant="caption" color="text.secondary">
                  Log Interaction messages are auto-saved when doctor and date are extracted.
                </Typography>
              </Box>
            </Stack>
          )}
        </CardContent>
      </Card>

      <Snackbar
        open={Boolean(save.error)}
        autoHideDuration={4000}
        onClose={() => dispatch(resetSave())}
        message={save.error}
      />
    </>
  )
}
