import { Link } from 'react-router-dom'
import { HealthStatus } from '../features/health/components/HealthStatus'
import { ProjectList } from '../features/projects/components/ProjectList'
import { Button } from '../shared/ui/Button'

export function ProjectsPage() {
  return (
    <>
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Projetos</h1>
          <p className="text-sm text-gray-600">
            Envie o material de um produto e veja ele explicado para cliente, equipe e devs.
          </p>
        </div>
        <Link to="/projects/new">
          <Button>Novo projeto</Button>
        </Link>
      </div>
      <ProjectList />
      <footer className="border-t border-gray-200 pt-4">
        <HealthStatus />
      </footer>
    </>
  )
}
