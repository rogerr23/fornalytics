import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useState } from 'react'
import { ApiError } from '../../../shared/api/client'
import { EMPTY_ANSWER, reduceAnswer, type AnswerState, type Lens } from '../../../shared/api/lens'
import { readStored, writeStored } from '../../../shared/lib/storage'
import { getConversation, streamChat } from '../api'

const storageKey = (projectId: string) => `fornalytics.chat.${projectId}`
const conversationKey = (projectId: string, id: string | null) =>
  ['projects', projectId, 'conversations', id] as const

/** The conversation of this project, kept in the browser so a reload resumes it. */
export function useConversationId(projectId: string) {
  const [id, setIdState] = useState<string | null>(() => readStored(storageKey(projectId)))
  const setId = useCallback(
    (next: string | null) => {
      setIdState(next)
      writeStored(storageKey(projectId), next)
    },
    [projectId],
  )
  return [id, setId] as const
}

export function useConversation(projectId: string, conversationId: string | null) {
  return useQuery({
    queryKey: conversationKey(projectId, conversationId),
    queryFn: ({ signal }) => getConversation(projectId, conversationId!, signal),
    enabled: conversationId !== null,
    retry: (count, error) => !(error instanceof ApiError && error.status === 404) && count < 1,
  })
}

export interface PendingExchange {
  question: string
  lens: Lens
  answer: AnswerState
}

/** Sends a question and streams the answer; once saved, the conversation is reloaded. */
export function useSendMessage(
  projectId: string,
  conversationId: string | null,
  onConversation: (id: string) => void,
) {
  const queryClient = useQueryClient()
  const [pending, setPending] = useState<PendingExchange | null>(null)

  const mutation = useMutation({
    mutationFn: async ({ question, lens }: { question: string; lens: Lens }) => {
      let answer = EMPTY_ANSWER
      let id = conversationId
      setPending({ question, lens, answer })
      for await (const event of streamChat(projectId, {
        lens,
        question,
        conversation_id: conversationId,
      })) {
        if (event.type === 'conversation') {
          id = event.conversation_id
          onConversation(id)
        }
        answer = reduceAnswer(answer, event)
        setPending({ question, lens, answer })
      }
      if (id) await queryClient.invalidateQueries({ queryKey: conversationKey(projectId, id) })
      // Saved answers come from the server now; a failed one stays visible with its error.
      if (!answer.error) setPending(null)
      return answer
    },
    onError: () => setPending(null),
  })

  function clear() {
    setPending(null)
    mutation.reset()
  }

  return {
    send: mutation.mutate,
    sending: mutation.isPending,
    error: mutation.error,
    pending,
    clear,
  }
}
