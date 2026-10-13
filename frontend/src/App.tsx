import { lazy, Suspense, type ReactNode } from 'react'
import { createBrowserRouter, Navigate, useLocation } from 'react-router'
import { RouterProvider } from 'react-router/dom'

import { useAuth } from './auth/AuthProvider'
import { AppShell } from './components/AppShell'
import { Skeleton } from './components/ui'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import NotFoundPage from './pages/NotFoundPage'

const LinksPage = lazy(() => import('./pages/LinksPage'))
const LinkDetailPage = lazy(() => import('./pages/LinkDetailPage'))
const CollectionsPage = lazy(() => import('./pages/CollectionsPage'))
const TagsPage = lazy(() => import('./pages/TagsPage'))
const InvitesPage = lazy(() => import('./pages/InvitesPage'))
const SettingsPage = lazy(() => import('./pages/SettingsPage'))
const JoinPage = lazy(() => import('./pages/JoinPage'))

function RequireAuth({ children }: { children: ReactNode }) {
  const { status } = useAuth()
  const location = useLocation()
  if (status === 'loading') return null
  if (status === 'anonymous') return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />
  return children
}

function Page({ children }: { children: ReactNode }) {
  return <Suspense fallback={<Skeleton height={28} width={220} />}>{children}</Suspense>
}

const router = createBrowserRouter(
  [
    { path: '/login', element: <LoginPage /> },
    { path: '/join/:token', element: <Page><JoinPage /></Page> },
    {
      path: '/',
      element: (
        <RequireAuth>
          <AppShell />
        </RequireAuth>
      ),
      children: [
        { index: true, element: <DashboardPage /> },
        { path: 'links', element: <Page><LinksPage /></Page> },
        { path: 'links/:id', element: <Page><LinkDetailPage /></Page> },
        { path: 'collections', element: <Page><CollectionsPage /></Page> },
        { path: 'tags', element: <Page><TagsPage /></Page> },
        { path: 'invites', element: <Page><InvitesPage /></Page> },
        { path: 'settings', element: <Page><SettingsPage /></Page> },
        { path: '*', element: <NotFoundPage /> },
      ],
    },
  ],
  { basename: '/app' },
)

export function App() {
  return <RouterProvider router={router} />
}
