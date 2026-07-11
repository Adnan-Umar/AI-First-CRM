import {
  Box,
  Card,
  CardContent,
  CircularProgress,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import { useEffect, useMemo, useState } from 'react'

import { useAppDispatch, useAppSelector } from '../app/hooks'
import { PageHeader } from '../components/PageHeader'
import { fetchInteractions } from '../features/interactions/interactionSlice'

export function InteractionHistoryPage() {
  const dispatch = useAppDispatch()
  const [channel, setChannel] = useState('All')
  const interactions = useAppSelector((state) => state.interactions.records)
  const loading = useAppSelector((state) => state.interactions.loading)
  const error = useAppSelector((state) => state.interactions.error)

  useEffect(() => {
    dispatch(fetchInteractions())
  }, [dispatch])

  const filtered = useMemo(() => {
    if (channel === 'All') return interactions
    return interactions.filter((item) => item.channel === channel)
  }, [channel, interactions])

  return (
    <>
      <PageHeader
        title="Interaction History"
        subtitle="Review all submitted engagements and track follow-up quality."
      />
      <Card>
        <CardContent>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 2 }}>
            <TextField
              select
              label="Channel"
              value={channel}
              onChange={(event) => setChannel(event.target.value)}
              sx={{ minWidth: 200 }}
            >
              <MenuItem value="All">All</MenuItem>
              <MenuItem value="In-person">In-person</MenuItem>
              <MenuItem value="Call">Call</MenuItem>
              <MenuItem value="Video">Video</MenuItem>
            </TextField>
          </Stack>

          {loading && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 2 }}>
              <CircularProgress size={20} />
              <Typography variant="body2" color="text.secondary">
                Loading interactions…
              </Typography>
            </Box>
          )}

          {error && (
            <Typography variant="body2" color="error" sx={{ py: 2 }}>
              {error}
            </Typography>
          )}

          {!loading && (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>HCP</TableCell>
                  <TableCell>Channel</TableCell>
                  <TableCell>Objective</TableCell>
                  <TableCell>Outcome</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filtered.map((interaction) => (
                  <TableRow key={interaction.id} hover>
                    <TableCell>{interaction.date}</TableCell>
                    <TableCell>{interaction.hcpName}</TableCell>
                    <TableCell>{interaction.channel}</TableCell>
                    <TableCell>{interaction.objective}</TableCell>
                    <TableCell>{interaction.outcome}</TableCell>
                  </TableRow>
                ))}
                {filtered.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} align="center" sx={{ color: 'text.secondary', py: 3 }}>
                      No interactions found.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </>
  )
}
