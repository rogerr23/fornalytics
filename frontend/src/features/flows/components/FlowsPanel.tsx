import { errorMessage } from '../../../shared/api/client'
import type { Lens, TextCitation } from '../../../shared/api/lens'
import { useSessionHistory } from '../../../shared/api/sessionHistory'
import { Alert } from '../../../shared/ui/Alert'
import { QuestionForm } from '../../../shared/ui/QuestionForm'
import { Spinner } from '../../../shared/ui/Spinner'
import { useAskFlow, useBaseFlows } from '../hooks/useFlows'
import { flowSuggestions } from '../suggestions'
import type { Flow } from '../types'
import { FlowCard } from './FlowCard'

interface FlowsPanelProps {
  projectId: string
  lens: Lens
  onOpenCitation: (citation: TextCitation) => void
}

export function FlowsPanel({ projectId, lens, onOpenCitation }: FlowsPanelProps) {
  const baseFlows = useBaseFlows(projectId)
  const ask = useAskFlow(projectId)
  const [asked, addAsked] = useSessionHistory<Flow>(['projects', projectId, 'flow-history'])

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-3">
        <p className="text-sm text-gray-500">
          Pergunte o que acontece em uma situação e veja o passo a passo com diagrama. Os fluxos da
          base aparecem abaixo sem gastar cota da IA.
        </p>
        <QuestionForm
          placeholder="O que acontece quando…?"
          suggestions={flowSuggestions(baseFlows.data?.map((flow) => flow.name) ?? [])}
          busy={ask.isPending}
          busyLabel="Montando o fluxo…"
          onAsk={(question) => ask.mutate({ question, lens }, { onSuccess: addAsked })}
        />
        {ask.isPending && <Spinner label="Montando o passo a passo…" />}
        {ask.isError && <Alert tone="error">{errorMessage(ask.error)}</Alert>}
      </div>

      {asked.map((flow, index) => (
        <FlowCard key={`asked-${index}`} flow={flow} onOpenCitation={onOpenCitation} />
      ))}

      <section className="flex flex-col gap-4">
        <h2 className="font-semibold text-gray-900">Fluxos da base do produto</h2>
        {baseFlows.isPending && <Spinner label="Carregando os fluxos…" />}
        {baseFlows.isError && <Alert tone="error">{errorMessage(baseFlows.error)}</Alert>}
        {baseFlows.data?.length === 0 && (
          <p className="text-sm text-gray-500">A base não registrou fluxos para este produto.</p>
        )}
        {baseFlows.data?.map((flow) => (
          <FlowCard key={`base-${flow.name}`} flow={flow} onOpenCitation={onOpenCitation} />
        ))}
      </section>
    </div>
  )
}
