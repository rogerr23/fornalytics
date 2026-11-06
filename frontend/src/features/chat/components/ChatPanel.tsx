import {
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type KeyboardEvent,
  type ReactNode,
} from 'react'
import { ApiError, errorMessage } from '../../../shared/api/client'
import { LENS_LABEL, type Lens, type TextCitation } from '../../../shared/api/lens'
import { Alert } from '../../../shared/ui/Alert'
import { AnswerMarkdown } from '../../../shared/ui/AnswerMarkdown'
import { Badge } from '../../../shared/ui/Badge'
import { Button } from '../../../shared/ui/Button'
import { Spinner } from '../../../shared/ui/Spinner'
import { useConversation, useConversationId, useSendMessage } from '../hooks/useChat'

const SUGGESTIONS: Record<Lens, string[]> = {
  cliente: ['O que este produto resolve para mim?', 'Quais são os principais benefícios?'],
  nao_tecnico: ['Como funciona o fluxo principal?', 'Quais regras de negócio existem?'],
  tecnico: ['Qual é a arquitetura do backend?', 'Onde ficam as regras de validação?'],
}

interface ChatPanelProps {
  projectId: string
  lens: Lens
  onOpenCitation: (citation: TextCitation) => void
}

export function ChatPanel({ projectId, lens, onOpenCitation }: ChatPanelProps) {
  const [conversationId, setConversationId] = useConversationId(projectId)
  const conversation = useConversation(projectId, conversationId)
  const chat = useSendMessage(projectId, conversationId, setConversationId)
  const [question, setQuestion] = useState('')
  const bottom = useRef<HTMLDivElement>(null)

  // A conversation removed from the server (project deleted, database reset): start fresh.
  const gone = conversation.error instanceof ApiError && conversation.error.status === 404
  useEffect(() => {
    if (gone) setConversationId(null)
  }, [gone, setConversationId])

  const pending = chat.pending
  const saved = conversation.data?.messages ?? []
  // The server saves the question before answering: do not show it twice while streaming.
  const last = saved.at(-1)
  const messages =
    pending && last?.role === 'user' && last.content === pending.question
      ? saved.slice(0, -1)
      : saved
  useEffect(() => {
    bottom.current?.scrollIntoView({ block: 'end' })
  }, [messages.length, pending?.answer.text])

  function ask(text: string) {
    const trimmed = text.trim()
    if (!trimmed || chat.sending) return
    chat.send({ question: trimmed, lens })
    setQuestion('')
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    ask(question)
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      ask(question)
    }
  }

  const empty = messages.length === 0 && !pending

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500">
          Respostas na lente <span className="font-medium text-gray-800">{LENS_LABEL[lens]}</span>,
          só com base no material do projeto.
        </p>
        <Button
          variant="ghost"
          size="sm"
          disabled={chat.sending || (conversationId === null && !pending)}
          onClick={() => {
            chat.clear()
            setConversationId(null)
          }}
        >
          Nova conversa
        </Button>
      </div>

      <div className="flex flex-col gap-4">
        {conversation.isLoading && <Spinner label="Carregando a conversa…" />}
        {empty && !conversation.isLoading && (
          <div className="flex flex-wrap gap-2">
            {SUGGESTIONS[lens].map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => ask(suggestion)}
                className="rounded-full border border-gray-200 px-3 py-1.5 text-sm text-gray-700 hover:border-indigo-300 hover:text-indigo-700"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
        {messages.map((message) =>
          message.role === 'user' ? (
            <Question key={message.id} text={message.content} />
          ) : (
            <Answer key={message.id} lens={message.lens}>
              <AnswerMarkdown
                text={message.content}
                citations={message.citations}
                onOpenCitation={onOpenCitation}
              />
            </Answer>
          ),
        )}
        {pending && (
          <>
            <Question text={pending.question} />
            <Answer lens={pending.lens}>
              {pending.answer.text ? (
                <AnswerMarkdown
                  text={pending.answer.text}
                  citations={pending.answer.citations}
                  onOpenCitation={onOpenCitation}
                />
              ) : (
                !pending.answer.error && <Spinner label="Pensando…" />
              )}
              {pending.answer.error && <Alert tone="error">{pending.answer.error}</Alert>}
            </Answer>
          </>
        )}
        {chat.error && <Alert tone="error">{errorMessage(chat.error)}</Alert>}
        <div ref={bottom} />
      </div>

      <form onSubmit={submit} className="sticky bottom-0 flex gap-2 bg-gray-50 py-3">
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          onKeyDown={onKeyDown}
          rows={2}
          maxLength={2000}
          placeholder="Pergunte algo sobre o produto… (Enter envia, Shift+Enter quebra a linha)"
          className="flex-1 resize-none rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
        />
        <Button type="submit" disabled={!question.trim() || chat.sending}>
          {chat.sending ? 'Respondendo…' : 'Enviar'}
        </Button>
      </form>
    </div>
  )
}

function Question({ text }: { text: string }) {
  return (
    <div className="ml-auto max-w-[80%] whitespace-pre-wrap rounded-2xl rounded-br-sm bg-indigo-600 px-4 py-2 text-sm text-white">
      {text}
    </div>
  )
}

function Answer({ lens, children }: { lens: Lens; children: ReactNode }) {
  return (
    <div className="flex max-w-[90%] flex-col gap-2 rounded-2xl rounded-bl-sm border border-gray-200 bg-white px-4 py-3">
      <span className="self-start">
        <Badge tone="indigo">{LENS_LABEL[lens]}</Badge>
      </span>
      {children}
    </div>
  )
}
