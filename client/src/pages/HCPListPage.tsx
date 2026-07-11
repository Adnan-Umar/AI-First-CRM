import {
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
} from '@mui/material'
import { useEffect, useMemo, useState } from 'react'

import { useAppDispatch, useAppSelector } from '../app/hooks'
import { PageHeader } from '../components/PageHeader'
import { fetchHCPs } from '../features/hcp/hcpSlice'

export function HCPListPage() {
  const dispatch = useAppDispatch()
  const [search, setSearch] = useState('')
  const hcps = useAppSelector((state) => state.hcps.records)

  useEffect(() => {
    dispatch(fetchHCPs())
  }, [dispatch])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return hcps
    return hcps.filter(
      (hcp) =>
        hcp.fullName.toLowerCase().includes(q) ||
        hcp.specialty.toLowerCase().includes(q) ||
        hcp.organization.toLowerCase().includes(q),
    )
  }, [hcps, search])

  return (
    <>
      <PageHeader
        title="HCP List"
        subtitle="Manage your healthcare professional network and prioritize engagements."
      />
      <Card>
        <CardContent>
          <TextField
            fullWidth
            label="Search by name, specialty, organization"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            sx={{ mb: 2 }}
          />
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Specialty</TableCell>
                  <TableCell>Organization</TableCell>
                  <TableCell>City</TableCell>
                  <TableCell>Last Interaction</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filtered.map((hcp) => (
                  <TableRow key={hcp.id} hover>
                    <TableCell>{hcp.fullName}</TableCell>
                    <TableCell>{hcp.specialty}</TableCell>
                    <TableCell>{hcp.organization}</TableCell>
                    <TableCell>{hcp.city}</TableCell>
                    <TableCell>{hcp.lastInteraction}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </>
  )
}
