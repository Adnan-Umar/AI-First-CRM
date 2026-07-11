import { Send as SendIcon } from '@mui/icons-material'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Divider,
  Grid,
  MenuItem,
  ToggleButton,
  ToggleButtonGroup,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useState } from 'react'

import { useAppDispatch, useAppSelector } from '../app/hooks'
import { PageHeader } from '../components/PageHeader'
import {
  addUserMessage,
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
  const [message, setMessage] = useState('')
  const hcps = useAppSelector((state) => state.hcps.records)
  const { mode, form, chat } = useAppSelector((state) => state.logInteraction)

  const handleSendMessage = () => {
    const trimmed = message.trim()
    if (!trimmed || chat.sending) {
      return
    }
    dispatch(addUserMessage(trimmed))
    dispatch(sendChatMessage(trimmed))
    setMessage('')
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
                >
                  {hcps.map((hcp) => (
                    <MenuItem key={hcp.id} value={hcp.id}>
                      {hcp.fullName}
                    </MenuItem>
                  ))}
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
                <Button variant="contained">Save Interaction</Button>
              </Grid>
            </Grid>
          ) : (
            <Stack spacing={2}>
              <Box
                sx={{
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 2,
                  p: 2,
                  minHeight: 220,
                  bgcolor: 'grey.50',
                }}
              >
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
                      <Typography variant="body2">{item.content}</Typography>
                    </Box>
                  ))}
                </Stack>
              </Box>
              {chat.error && (
                <Alert severity="error" variant="outlined">
                  {chat.error}
                </Alert>
              )}
              <Stack direction="row" spacing={1}>
                <TextField
                  fullWidth
                  label="Type your message"
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' && !event.shiftKey) {
                      event.preventDefault()
                      handleSendMessage()
                    }
                  }}
                />
                <Button
                  variant="contained"
                  endIcon={<SendIcon />}
                  onClick={handleSendMessage}
                  disabled={chat.sending}
                >
                  Send
                </Button>
              </Stack>
            </Stack>
          )}
        </CardContent>
      </Card>
    </>
  )
}
