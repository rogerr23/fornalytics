import { createBrowserRouter } from 'react-router-dom'
import { ProjectsPage } from '../pages/ProjectsPage'

export const router = createBrowserRouter([{ path: '/', element: <ProjectsPage /> }])
