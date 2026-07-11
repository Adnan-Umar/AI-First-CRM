import {
  Card,
  CardContent,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
} from '@mui/material'
import { useMemo, useState } from 'react'

import { useAppSelector } from '../app/hooks'
import { PageHeader } from '../components/PageHeader'

export function InteractionHistoryPage() {
  const [channel, setChannel] = useState('All')
  const interactions = useAppSelector((state) => state.interactions.records)

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
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </>
  )
}
