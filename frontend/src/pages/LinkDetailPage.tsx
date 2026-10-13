import { ChevronLeft, ExternalLink, Pencil, Trash2 } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link as RouterLink, useNavigate, useParams } from 'react-router'

import { ApiError } from '../api/client'
import { useClicks, useCollections, useDeleteLink, useLink, useSummary, useTags } from '../api/queries'
import { BreakdownList, HourStrip } from '../components/charts/Breakdown'
import { ClicksOverview } from '../components/charts/ClicksOverview'
import { RecentClicks } from '../components/dashboard/RecentClicks'
import { HighlightProvider } from '../components/dashboard/highlight'
import { CodesPanel } from '../components/link/CodesPanel'
import { EditLinkDialog } from '../components/link/EditLinkDialog'
import {
  Button,
  Dialog,
  EmptyState,
  LineName,
  Pagination,
  Panel,
  Segmented,
  Skeleton,
  TagChip,
} from '../components/ui'
import { formatDate } from '../lib/format'
import NotFoundPage from './NotFoundPage'
import styles from './LinkDetailPage.module.css'

const RANGES = [
  { value: 7, label: '7 days' },
  { value: 30, label: '30 days' },
  { value: 90, label: '90 days' },
]

type Source = 'referrers' | 'devices' | 'browsers' | 'os'

export default function LinkDetailPage() {
  const id = Number(useParams().id)
  const navigate = useNavigate()
  const link = useLink(id)
  const collections = useCollections()
  const tags = useTags()
  const [days, setDays] = useState(30)
  const [source, setSource] = useState<Source>('referrers')
  const [page, setPage] = useState(1)
  const [editing, setEditing] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const summary = useSummary({ days, url: id })
  const clicks = useClicks({ url_id: id, page, page_size: 10 })
  const remove = useDeleteLink()

  const tagMap = useMemo(() => new Map((tags.data ?? []).map((tag) => [tag.id, tag])), [tags.data])

  if (link.error instanceof ApiError && link.error.status === 404) return <NotFoundPage />
  if (!link.data) {
    return (
      <div className={styles.page}>
        <Skeleton width={240} height={28} />
        <Skeleton height={160} />
      </div>
    )
  }

  const data = link.data
  const collection = collections.data?.find((item) => item.id === data.collection)

  return (
    <HighlightProvider>
      <div className={styles.page}>
        <RouterLink to="/links" className={styles.back}>
          <ChevronLeft size={15} aria-hidden /> Links
        </RouterLink>

        <header className={styles.header}>
          <div className={styles.titleBlock}>
            <h1>{data.name}</h1>
            <a href={data.url} target="_blank" rel="noreferrer" className={styles.destination}>
              <span>{data.url}</span>
              <ExternalLink size={14} aria-hidden />
            </a>
            <div className={styles.labels}>
              {collection ? (
                <RouterLink to={`/links?collection=${collection.id}`} className={styles.lineLink}>
                  <LineName name={collection.name} color={collection.color} />
                </RouterLink>
              ) : (
                <span className={styles.muted}>No collection</span>
              )}
              {data.tags.map((tagId) => {
                const tag = tagMap.get(tagId)
                return tag ? <TagChip key={tagId} name={tag.name} color={tag.color} /> : null
              })}
              <span className={styles.muted}>Created {formatDate(data.created_at)}</span>
            </div>
          </div>
          <div className={styles.actions}>
            <Button onClick={() => setEditing(true)}>
              <Pencil size={15} aria-hidden /> Edit
            </Button>
            <Button variant="ghost" onClick={() => setDeleting(true)}>
              <Trash2 size={15} aria-hidden /> Delete
            </Button>
          </div>
        </header>

        <CodesPanel link={data} />

        <div className={styles.analyticsHeading}>
          <h2>Clicks</h2>
          <Segmented label="Date range" value={days} options={RANGES} onChange={setDays} />
        </div>

        <div className={styles.grid}>
          <Panel title="Over time" className={styles.span2}>
            <ClicksOverview summary={summary.data} loading={summary.isFetching} />
          </Panel>
          <Panel title="Time of day">
            {summary.data ? <HourStrip hours={summary.data.hours} /> : <Skeleton height={72} />}
          </Panel>
          <Panel
            title="Sources"
            actions={
              <Segmented
                label="Break down by"
                value={source}
                onChange={setSource}
                options={[
                  { value: 'referrers', label: 'Referrers' },
                  { value: 'devices', label: 'Devices' },
                  { value: 'browsers', label: 'Browsers' },
                  { value: 'os', label: 'Systems' },
                ]}
              />
            }
          >
            {summary.data ? (
              <BreakdownList
                rows={summary.data[source]}
                total={summary.data.totals.clicks}
                kind={source === 'referrers' ? 'referrer' : source === 'devices' ? 'device' : 'plain'}
                empty="Sources appear once this link gets clicks."
              />
            ) : (
              <Skeleton height={120} />
            )}
          </Panel>
          <Panel title="Every click" className={styles.span2}>
            {clicks.data?.count === 0 ? (
              <EmptyState title="No clicks yet">
                Share one of the codes above. Each visit is listed here with its source and device.
              </EmptyState>
            ) : (
              <>
                <RecentClicks clicks={clicks.data?.results} loading={clicks.isPending} showLink={data.short_urls.length > 1} />
                <Pagination page={page} pageSize={10} count={clicks.data?.count ?? 0} onPage={setPage} />
              </>
            )}
          </Panel>
        </div>

        {editing && <EditLinkDialog link={data} open={editing} onClose={() => setEditing(false)} />}
        <Dialog
          open={deleting}
          onClose={() => setDeleting(false)}
          title={`Delete ${data.name}?`}
          footer={
            <>
              <Button onClick={() => setDeleting(false)}>Cancel</Button>
              <Button
                variant="danger"
                loading={remove.isPending}
                onClick={async () => {
                  await remove.mutateAsync(data.id)
                  navigate('/links')
                }}
              >
                Delete link
              </Button>
            </>
          }
        >
          <p>
            All {data.short_urls.length} of its codes stop redirecting and stay reserved, so nobody else can take them.
          </p>
        </Dialog>
      </div>
    </HighlightProvider>
  )
}
