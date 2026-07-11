export interface Interaction {
  id: string
  hcpName: string
  channel: 'In-person' | 'Call' | 'Video'
  objective: string
  summary: string
  outcome: string
  date: string
}
