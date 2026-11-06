import { useQuery } from '@tanstack/react-query'
import { useCallback, useState } from 'react'
import { Link, Navigate, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { ChatPanel } from '../features/chat/components/ChatPanel'
import { ComparePanel } from '../features/compare/components/ComparePanel'
import { DoesItPanel } from '../features/does-it/components/DoesItPanel'
import { IdeaVsCodePanel } from '../features/idea-vs-code/components/IdeaVsCodePanel'
import { CitationViewer } from '../features/citations/components/CitationViewer'
import { LensSelector } from '../features/lens/components/LensSelector'
import { useLens } from '../features/lens/hooks/useLens'
import { OverviewPanel } from '../features/overview/components/OverviewPanel'
import { useStartProcessing } from '../features/processing/hooks/useProcessing'
import { errorMessage } from '../shared/api/client'
import type { TextCitation } from '../shared/api/lens'
import { projectQuery } from '../shared/api/projects'
import { Alert } from '../shared/ui/Alert'
import { Button } from '../shared/ui/Button'
import { ProjectStatusBadge } from '../shared/ui/ProjectStatusBadge'
import { Spinner } from '../shared/ui/Spinner'
import { Tabs, type TabItem } from '../shared/ui/Tabs'

type Tab = 'overview' | 'chat' | 'compare' | 'does-it' | 'idea-vs-code' | 'flows'

const TABS: TabItem<Tab>[] = [
  { value: 'overview', label: 'Visão geral' },
  { value: 'chat', label: 'Chat' },
  { value: 'compare', label: 'Lado a lado' },
  { value: 'does-it', label: 'Isso faz?' },
  { value: 'idea-vs-code', label: 'Ideia × Código' },
  { value: 'flows', label: 'Fluxos', disabled: true, hint: 'Chega na Fase 9' },
]

function isActiveTab(value: string | null): value is Tab {
  return TABS.some((tab) => tab.value === value && !tab.disabled)
}

export function ProjectPage() {
  const { projectId = '' } = useParams()
  const navigate = useNavigate()
  const [params, setParams] = useSearchParams()
  const project = useQuery(projectQuery(projectId))
  const reprocess = useStartProcessing(projectId)
  const { lens } = useLens()
  const [citation, setCitation] = useState<TextCitation | null>(null)
  const closeCitation = useCallback(() => setCitation(null), [])

  const tabParam = params.get('tab')
  const tab: Tab = isActiveTab(tabParam) ? tabParam : 'overview'

  if (project.isPending) return <Spinner label="Carregando o projeto…" />
  if (project.isError) return <Alert tone="error">{errorMessage(project.error)}</Alert>
  const detail = project.data
  if (detail.status === 'processing') {
    return <Navigate to={`/projects/${projectId}/processing`} replace />
  }

  return (
    <>
      <div className="flex flex-col gap-4">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm text-gray-500">
              <Link to="/" className="hover:underline">
                Projetos
              </Link>
            </p>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">{detail.name}</h1>
              <ProjectStatusBadge status={detail.status} />
            </div>
            <Link
              to={`/projects/${projectId}/material`}
              className="text-sm text-indigo-700 hover:underline"
            >
              Ver ou editar o material
            </Link>
          </div>
          <LensSelector />
        </div>

        {detail.base_outdated && (
          <Alert
            tone="warning"
            title="O material mudou"
            action={
              <Button
                size="sm"
                disabled={reprocess.isPending}
                onClick={() =>
                  reprocess.mutate(undefined, {
                    onSuccess: () => navigate(`/projects/${projectId}/processing`),
                  })
                }
              >
                Reprocessar
              </Button>
            }
          >
            As explicações abaixo ainda usam a base anterior. Reprocesse para incluir as mudanças.
          </Alert>
        )}
        {detail.status === 'failed' && !detail.base_outdated && (
          <Alert tone="error" title="O último processamento falhou">
            {detail.status_detail}
          </Alert>
        )}
        {reprocess.isError && <Alert tone="error">{errorMessage(reprocess.error)}</Alert>}
      </div>

      <Tabs
        items={TABS}
        value={tab}
        onChange={(next) => setParams({ tab: next }, { replace: true })}
      />

      {tab === 'overview' && (
        <OverviewPanel projectId={projectId} lens={lens} onOpenCitation={setCitation} />
      )}
      {tab === 'chat' && (
        <ChatPanel projectId={projectId} lens={lens} onOpenCitation={setCitation} />
      )}
      {tab === 'compare' && <ComparePanel projectId={projectId} onOpenCitation={setCitation} />}
      {tab === 'idea-vs-code' && (
        <IdeaVsCodePanel projectId={projectId} onOpenCitation={setCitation} />
      )}
      {tab === 'does-it' && (
        <DoesItPanel projectId={projectId} lens={lens} onOpenCitation={setCitation} />
      )}

      <CitationViewer projectId={projectId} citation={citation} onClose={closeCitation} />
    </>
  )
}
