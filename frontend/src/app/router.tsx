import { createBrowserRouter } from 'react-router-dom'
import { NewProjectPage } from '../pages/NewProjectPage'
import { ProcessingPage } from '../pages/ProcessingPage'
import { ProjectPage } from '../pages/ProjectPage'
import { ProjectsPage } from '../pages/ProjectsPage'
import { Layout } from './Layout'

export const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: '/', element: <ProjectsPage /> },
      { path: '/projects/new', element: <NewProjectPage /> },
      { path: '/projects/:projectId/material', element: <NewProjectPage /> },
      { path: '/projects/:projectId/processing', element: <ProcessingPage /> },
      { path: '/projects/:projectId', element: <ProjectPage /> },
    ],
  },
])
