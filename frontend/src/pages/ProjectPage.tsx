import { useQuery } from '@tanstack/react-query'
import { useCallback, useState } from 'react'
import { Navigate, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { ChatPanel } from '../features/chat/components/ChatPanel'
import { ComparePanel } from '../features/compare/components/ComparePanel'
import { DoesItPanel } from '../features/does-it/components/DoesItPanel'
import { FlowsPanel } from '../features/flows/components/FlowsPanel'
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
import { Button, ButtonLink } from '../shared/ui/Button'
import { Icon } from '../shared/ui/Icon'
import { Breadcrumbs, HeroBand, PageBody, Stat } from '../shared/ui/Page'
import { ProjectStatusBadge } from '../shared/ui/ProjectStatusBadge'
import { SkeletonText } from '../shared/ui/Skeleton'
import { formatTokens } from '../shared/lib/format'
import { Tabs, type TabItem } from '../shared/ui/Tabs'

type Tab = 'overview' | 'chat' | 'compare' | 'does-it' | 'idea-vs-code' | 'flows'

const TABS: TabItem<Tab>[] = [
  { value: 'overview', label: 'Visão geral', icon: 'info' },
  { value: 'chat', label: 'Chat', icon: 'chat' },
  { value: 'compare', label: 'Lado a lado', icon: 'layers' },
  { value: 'does-it', label: 'Isso faz?', icon: 'search' },
  { value: 'idea-vs-code', label: 'Ideia × Código', icon: 'check' },
  { value: 'flows', label: 'Fluxos', icon: 'flow' },
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

  if (project.isPending) {
    return (
      <PageBody>
        <SkeletonText lines={3} label="Carregando o projeto…" />
      </PageBody>
    )
  }
  if (project.isError) {
    return (
      <PageBody>
        <Alert tone="error">{errorMessage(project.error)}</Alert>
      </PageBody>
    )
  }
  const detail = project.data
  if (detail.status === 'processing') {
    return <Navigate to={`/projects/${projectId}/processing`} replace />
  }

  const files = detail.sources.reduce((total, source) => total + source.file_count, 0)
  const tokens = detail.sources.reduce((total, source) => total + source.token_estimate, 0)

  return (
    <>
      <HeroBand>
        <div className="flex flex-wrap items-end justify-between gap-x-10 gap-y-8">
          <div className="flex min-w-0 flex-col gap-3">
            <Breadcrumbs inverse items={[{ label: 'Projetos', to: '/' }, { label: detail.name }]} />
            <h1 className="text-4xl leading-[1.04] font-extrabold tracking-tight break-words sm:text-6xl">
              {detail.name}
            </h1>
            <div className="flex flex-wrap items-center gap-3">
              <ProjectStatusBadge status={detail.status} />
              <ButtonLink to={`/projects/${projectId}/material`} variant="ghostInverse" size="sm">
                Ver ou editar o material
                <Icon name="arrow" size={16} />
              </ButtonLink>
            </div>
          </div>
          <div className="flex flex-wrap gap-x-10 gap-y-6">
            <Stat
              inverse
              value={String(detail.sources.length)}
              strong="Fontes"
              rest="de material"
            />
            <Stat inverse value={String(files)} strong="Arquivos" rest="analisados" />
            <Stat
              inverse
              value={formatTokens(tokens).replace(' tokens', '')}
              strong="Tokens"
              rest="estimados"
            />
          </div>
        </div>
        <LensSelector inverse />
      </HeroBand>

      <PageBody className="gap-6">
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
                <Icon name="refresh" size={16} />
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

        <Tabs
          items={TABS}
          value={tab}
          label="Abas do projeto"
          onChange={(next) => setParams({ tab: next }, { replace: true })}
        />

        <div
          role="tabpanel"
          aria-label={TABS.find((item) => item.value === tab)?.label}
          className="pt-2"
        >
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
          {tab === 'flows' && (
            <FlowsPanel projectId={projectId} lens={lens} onOpenCitation={setCitation} />
          )}
          {tab === 'does-it' && (
            <DoesItPanel projectId={projectId} lens={lens} onOpenCitation={setCitation} />
          )}
        </div>
      </PageBody>

      <CitationViewer projectId={projectId} citation={citation} onClose={closeCitation} />
    </>
  )
}
