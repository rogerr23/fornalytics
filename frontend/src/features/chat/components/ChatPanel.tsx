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
import { FIELD } from '../../../shared/ui/field'
import { Icon } from '../../../shared/ui/Icon'
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
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-grey-500">
          Respostas na lente <span className="font-semibold text-ink">{LENS_LABEL[lens]}</span>, só
          com base no material do projeto.
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
          <Icon name="plus" size={16} />
          Nova conversa
        </Button>
      </div>

      <div className="flex flex-col gap-5">
        {conversation.isLoading && <Spinner label="Carregando a conversa…" />}
        {empty && !conversation.isLoading && (
          <div className="flex flex-col gap-3 rounded-lg border border-dashed border-grey-300 p-6">
            <p className="eyebrow text-grey-500">Comece por uma destas</p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTIONS[lens].map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => ask(suggestion)}
                  className="min-h-9 rounded-full border border-grey-300 px-3.5 py-1.5 text-[13px] font-medium transition-colors duration-150 hover:border-ink hover:bg-grey-50"
                >
                  {suggestion}
                </button>
              ))}
            </div>
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

      <form
        onSubmit={submit}
        className="sticky bottom-0 flex gap-2 border-t border-grey-200 bg-white/95 py-4 backdrop-blur"
      >
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          onKeyDown={onKeyDown}
          rows={2}
          maxLength={2000}
          placeholder="Pergunte algo sobre o produto… (Enter envia, Shift+Enter quebra a linha)"
          aria-label="Sua pergunta"
          className={`${FIELD} min-w-0 flex-1 resize-none`}
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
    <div className="ml-auto max-w-[85%] rounded-lg bg-ink px-4 py-3 text-sm whitespace-pre-wrap text-white sm:max-w-[70%]">
      {text}
    </div>
  )
}

function Answer({ lens, children }: { lens: Lens; children: ReactNode }) {
  return (
    <div className="flex max-w-full flex-col gap-3 rounded-lg border border-grey-200 bg-white px-5 py-4 sm:max-w-[90%]">
      <span className="self-start">
        <Badge tone="neutral">Lente {LENS_LABEL[lens]}</Badge>
      </span>
      {children}
    </div>
  )
}
