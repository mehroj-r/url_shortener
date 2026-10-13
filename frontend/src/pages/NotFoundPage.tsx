import { Link as RouterLink } from 'react-router'

import { EmptyState } from '../components/ui'

export default function NotFoundPage() {
  return (
    <EmptyState title="No such page" action={<RouterLink to="/">Back to the dashboard</RouterLink>}>
      The link or page you followed doesn’t exist, or it belongs to someone else.
    </EmptyState>
  )
}
