export type InteractionMode = 'form' | 'chat'

export type VisitType = 'In-person' | 'Call' | 'Video'

export interface InteractionFormState {
  doctorId: string
  visitType: VisitType
  date: string
  productsDiscussed: string
  notes: string
  followUpDate: string
  objective: string
  summary: string
  outcome: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  createdAt: string
}

export interface ExtractedFields {
  doctorId?: string
  visitType?: string
  date?: string
  productsDiscussed?: string
  notes?: string
  followUpDate?: string
  objective?: string
  summary?: string
  outcome?: string
  intent?: string
  intentLabel?: string
}

export interface ChatApiResponse {
  reply: string
  extracted_fields: ExtractedFields | null
  intent: string | null
}
