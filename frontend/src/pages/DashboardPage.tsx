import { useMemo, useState } from 'react'
import { Link as RouterLink } from 'react-router'

import { useClicks, useCollections, useLinks, useSummary } from '../api/queries'
import type { Collection, Link } from '../api/types'
import { BreakdownList } from '../components/charts/Breakdown'
import { ClicksOverview } from '../components/charts/ClicksOverview'
import { CreateLinkForm } from '../components/CreateLinkForm'
import { HighlightProvider, useHighlight } from '../components/dashboard/highlight'
import { LineMap } from '../components/dashboard/LineMap'
import { RecentClicks } from '../components/dashboard/RecentClicks'
import { TopLinks } from '../components/dashboard/TopLinks'
import { EmptyState, Panel, Segmented, Select, Skeleton } from '../components/ui'
import styles from './DashboardPage.module.css'

const RANGES = [
  { value: 7, label: '7 days' },
  { value: 30, label: '30 days' },
  { value: 90, label: '90 days' },
]

type Source = 'referrers' | 'devices' | 'browsers' | 'os'
const SOURCES: { value: Source; label: string }[] = [
  { value: 'referrers', label: 'Referrers' },
  { value: 'devices', label: 'Devices' },
  { value: 'browsers', label: 'Browsers' },
  { value: 'os', label: 'Systems' },
]

function Dashboard() {
  const [days, setDays] = useState(30)
  const [collectionId, setCollectionId] = useState<number | undefined>()
  const [source, setSource] = useState<Source>('referrers')
  const { setArrivingId } = useHighlight()

  const summary = useSummary({ days, collection: collectionId })
  const collections = useCollections()
  const links = useLinks({ page_size: 100, ordering: '-clicks', collection: collectionId })
  const clicks = useClicks({ page_size: 8, collection: collectionId })

  const linkMap = useMemo(() => new Map((links.data?.results ?? []).map((link) => [link.id, link] as [number, Link])), [links.data])
  const collectionMap = useMemo(
    () => new Map((collections.data ?? []).map((item) => [item.id, item] as [number, Collection])),
    [collections.data],
  )
  const clicksByLink = useMemo(
    () => new Map((summary.data?.link_clicks ?? []).map((row) => [row.id, row.clicks] as [number, number])),
    [summary.data],
  )
  const visibleCollections = (collections.data ?? []).filter((item) => !collectionId || item.id === collectionId)
  const hasLinks = (links.data?.count ?? 0) > 0

  return (
    <div className={styles.page}>
      <section className={styles.ticket} aria-label="Shorten a link">
        <CreateLinkForm
          variant="ticket"
          defaultCollection={collectionId ?? null}
          onCreated={(link) => {
            setArrivingId(link.id)
            window.setTimeout(() => setArrivingId(null), 800)
          }}
        />
      </section>

      <div className={styles.heading}>
        <h1>Dashboard</h1>
        <div className={styles.filters}>
          <Segmented label="Date range" value={days} options={RANGES} onChange={setDays} />
          <Select
            aria-label="Collection"
            className={styles.collectionFilter}
            value={collectionId ?? ''}
            onChange={(event) => setCollectionId(event.target.value ? Number(event.target.value) : undefined)}
          >
            <option value="">All collections</option>
            {collections.data?.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </Select>
        </div>
      </div>

      <div className={styles.top}>
        <Panel
          title="Collections"
          className={styles.lines}
          actions={
            <RouterLink to="/collections" className={styles.panelLink}>
              Manage
            </RouterLink>
          }
        >
          {links.isPending ? (
            <div className={styles.skeletonLines}>
              <Skeleton height={26} />
              <Skeleton height={26} />
            </div>
          ) : hasLinks ? (
            <LineMap
              collections={visibleCollections}
              links={links.data?.results ?? []}
              clicksByLink={clicksByLink}
              days={days}
            />
          ) : (
            <EmptyState title="No links yet">
              Each collection is drawn here as a line, with its links sized by clicks. Shorten your first link above,
              then group links into collections.
            </EmptyState>
          )}
        </Panel>

        <Panel title="Clicks" className={styles.clicksPanel}>
          <ClicksOverview summary={summary.data} loading={summary.isFetching} />
        </Panel>
      </div>

      <div className={styles.bottom}>
        <Panel
          title="Top links"
          className={styles.topLinks}
          actions={
            <RouterLink to="/links?ordering=-clicks" className={styles.panelLink}>
              All links
            </RouterLink>
          }
        >
          {summary.data ? (
            <TopLinks summary={summary.data} links={linkMap} collections={collectionMap} />
          ) : (
            <Skeleton height={120} />
          )}
        </Panel>

        <Panel
          title="Sources"
          actions={<Segmented label="Break down by" value={source} options={SOURCES} onChange={setSource} />}
        >
          {summary.data ? (
            <BreakdownList
              rows={summary.data[source]}
              total={summary.data.totals.clicks}
              kind={source === 'referrers' ? 'referrer' : source === 'devices' ? 'device' : 'plain'}
              empty="Sources appear once your links get clicks."
            />
          ) : (
            <Skeleton height={120} />
          )}
        </Panel>

        <Panel title="Recent clicks" className={styles.recent}>
          <RecentClicks
            clicks={clicks.data?.results}
            loading={clicks.isPending}
            links={linkMap}
            collections={collectionMap}
          />
        </Panel>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  return (
    <HighlightProvider>
      <Dashboard />
    </HighlightProvider>
  )
}
