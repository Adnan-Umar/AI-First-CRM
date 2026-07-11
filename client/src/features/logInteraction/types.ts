export type InteractionMode = 'form' | 'chat'

export type VisitType = 'In-person' | 'Call' | 'Video'

export interface InteractionFormState {
  doctorId: string
  visitType: VisitType
  date: string
  productsDiscussed: string
  notes: string
  followUpDate: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  createdAt: string
}

