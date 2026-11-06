import type { Lens, TextCitation } from '../../shared/api/lens'

export interface ChatMessage {
  id: string
  lens: Lens
  role: 'user' | 'assistant'
  content: string
  citations: TextCitation[]
  created_at: string
}

export interface Conversation {
  id: string
  messages: ChatMessage[]
}
