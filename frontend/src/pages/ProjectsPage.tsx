import { HealthStatus } from '../features/health/components/HealthStatus'
import { ProjectList } from '../features/projects/components/ProjectList'
import { ButtonLink } from '../shared/ui/Button'
import { Icon } from '../shared/ui/Icon'
import { PageBody, PageHeader } from '../shared/ui/Page'

export function ProjectsPage() {
  return (
    <PageBody>
      <PageHeader
        title={
          <>
            Seus <strong className="font-extrabold">projetos</strong>
          </>
        }
        description="Envie o material de um produto e veja ele explicado para o cliente, para a equipe e para quem desenvolve."
        actions={
          <ButtonLink to="/projects/new">
            <Icon name="plus" size={16} />
            Novo projeto
          </ButtonLink>
        }
      />
      <ProjectList />
      <footer className="mt-auto border-t border-grey-200 pt-4">
        <HealthStatus />
      </footer>
    </PageBody>
  )
}
