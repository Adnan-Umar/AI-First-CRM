import { Box, Card, CardContent, Grid, Stack, Typography } from '@mui/material'

import { PageHeader } from '../components/PageHeader'
import { useAppSelector } from '../app/hooks'

export function DashboardPage() {
  const hcps = useAppSelector((state) => state.hcps.records)
  const interactions = useAppSelector((state) => state.interactions.records)

  const todayInteractions = interactions.filter((item) => item.date === '2026-07-10').length

  return (
    <Box>
      <PageHeader
        title="Dashboard"
        subtitle="Track field activities and relationship quality across your HCP base."
      />

      <Grid container spacing={2.5}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary">Total HCPs</Typography>
              <Typography variant="h4">{hcps.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary">Logged Interactions</Typography>
              <Typography variant="h4">{interactions.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary">Today&apos;s Interactions</Typography>
              <Typography variant="h4">{todayInteractions}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Recent Activities
              </Typography>
              <Stack spacing={1.5}>
                {interactions.slice(0, 3).map((item) => (
                  <Box
                    key={item.id}
                    sx={{
                      p: 1.5,
                      borderRadius: 2,
                      border: '1px solid',
                      borderColor: 'divider',
                    }}
                  >
                    <Typography sx={{ fontWeight: 600 }}>
                      {item.hcpName} • {item.channel}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {item.summary}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}
