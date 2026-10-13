import { CircleSlash, Play, Plus, Search, Trash2, X } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link as RouterLink, useNavigate, useSearchParams } from 'react-router'

import { ApiError } from '../api/client'
import { useBulkLinks, useCollections, useLinks, useTags, type BulkAction, type LinkFilters } from '../api/queries'
import type { Collection, Tag } from '../api/types'
import { useOpenCreate } from '../components/AppShell'
import {
  Button,
  Code,
  CopyCodeButton,
  Dialog,
  EmptyState,
  Pagination,
  Select,
  Sign,
  Skeleton,
  StatusBadge,
  TagChip,
  TextInput,
  LineName,
  ui,
} from '../components/ui'
import { displayUrl, formatNumber, timeAgo } from '../lib/format'
import { useToast } from '../lib/toast'
import styles from './LinksPage.module.css'

const PAGE_SIZE = 25

const SORTS = [
  { value: '-created_at', label: 'Newest first' },
  { value: '-clicks', label: 'Most clicked' },
  { value: '-last_clicked_at', label: 'Recently clicked' },
  { value: 'name', label: 'Name A–Z' },
]

function useFilters() {
  const [params, setParams] = useSearchParams()
  const filters: LinkFilters = {
    search: params.get('search') ?? undefined,
    collection: params.get('collection') === 'none' ? 'none' : Number(params.get('collection')) || undefined,
    tag: Number(params.get('tag')) || undefined,
    status: (params.get('status') as LinkFilters['status']) ?? undefined,
    ordering: params.get('ordering') ?? '-created_at',
    page: Number(params.get('page')) || 1,
    page_size: PAGE_SIZE,
  }
  const update = useCallback(
    (changes: Record<string, string | number | undefined>) => {
      setParams((current) => {
        const next = new URLSearchParams(current)
        for (const [key, value] of Object.entries(changes)) {
          if (value === undefined || value === '') next.delete(key)
          else next.set(key, String(value))
        }
        if (!('page' in changes)) next.delete('page')
        return next
      })
    },
    [setParams],
  )
  const active = Boolean(filters.search || filters.collection || filters.tag || filters.status)
  return { filters, update, active, clear: () => setParams({}) }
}

function BulkBar({
  ids,
  collections,
  tags,
  onDone,
}: {
  ids: number[]
  collections: Collection[]
  tags: Tag[]
  onDone: () => void
}) {
  const bulk = useBulkLinks()
  const toast = useToast()
  const [confirming, setConfirming] = useState(false)

  const run = async (action: BulkAction, message: (count: number) => string) => {
    try {
      const { count } = await bulk.mutateAsync({ ids, ...action })
      toast(message(count))
      onDone()
    } catch (error) {
      toast(error instanceof ApiError ? error.message : 'That did not work. Try again.', 'error')
    }
  }

  return (
    <div className={styles.bulkBar} role="toolbar" aria-label="Selected links">
      <strong className="num">{ids.length} selected</strong>
      <Select
        aria-label="Move to collection"
        value=""
        onChange={(event) => {
          const value = event.target.value
          if (!value) return
          const collection = value === 'none' ? null : Number(value)
          run({ action: 'move', collection }, (n) => `Moved ${n} links`)
        }}
      >
        <option value="">Move to…</option>
        <option value="none">No collection</option>
        {collections.map((item) => (
          <option key={item.id} value={item.id}>
            {item.name}
          </option>
        ))}
      </Select>
      <Select
        aria-label="Add tag"
        value=""
        onChange={(event) => {
          if (event.target.value) run({ action: 'add_tag', tag: Number(event.target.value) }, (n) => `Tagged ${n} links`)
        }}
      >
        <option value="">Add tag…</option>
        {tags.map((tag) => (
          <option key={tag.id} value={tag.id}>
            {tag.name}
          </option>
        ))}
      </Select>
      <Button size="sm" onClick={() => run({ action: 'deactivate' }, (n) => `Paused ${n} links`)}>
        <CircleSlash size={14} aria-hidden /> Pause
      </Button>
      <Button size="sm" onClick={() => run({ action: 'activate' }, (n) => `Resumed ${n} links`)}>
        <Play size={14} aria-hidden /> Resume
      </Button>
      <Button size="sm" variant="danger" onClick={() => setConfirming(true)}>
        <Trash2 size={14} aria-hidden /> Delete
      </Button>
      <Button size="sm" variant="ghost" onClick={onDone}>
        <X size={14} aria-hidden /> Clear
      </Button>
      <Dialog
        open={confirming}
        onClose={() => setConfirming(false)}
        title={`Delete ${ids.length} links?`}
        footer={
          <>
            <Button onClick={() => setConfirming(false)}>Cancel</Button>
            <Button
              variant="danger"
              loading={bulk.isPending}
              onClick={async () => {
                await run({ action: 'delete' }, (n) => `Deleted ${n} links`)
                setConfirming(false)
              }}
            >
              Delete links
            </Button>
          </>
        }
      >
        <p>Their short codes stop redirecting and stay reserved, so nobody else can take them.</p>
      </Dialog>
    </div>
  )
}

export default function LinksPage() {
  const navigate = useNavigate()
  const openCreate = useOpenCreate()
  const { filters, update, active, clear } = useFilters()
  const [search, setSearch] = useState(filters.search ?? '')
  const [selected, setSelected] = useState<number[]>([])
  const links = useLinks(filters)
  const collections = useCollections()
  const tags = useTags()

  // Debounce typing into the search filter
  const appliedSearch = filters.search ?? ''
  useEffect(() => {
    if (search.trim() === appliedSearch) return
    const timer = window.setTimeout(() => update({ search: search.trim() || undefined }), 250)
    return () => window.clearTimeout(timer)
  }, [search, appliedSearch, update])

  // Follow the URL (e.g. the top bar search) without eating a space the user is still typing
  const [seenSearch, setSeenSearch] = useState(appliedSearch)
  if (seenSearch !== appliedSearch) {
    setSeenSearch(appliedSearch)
    if (search.trim() !== appliedSearch) setSearch(appliedSearch)
  }

  const collectionMap = useMemo(() => new Map((collections.data ?? []).map((c) => [c.id, c])), [collections.data])
  const tagMap = useMemo(() => new Map((tags.data ?? []).map((t) => [t.id, t])), [tags.data])
  const rows = links.data?.results ?? []
  const allSelected = rows.length > 0 && rows.every((row) => selected.includes(row.id))

  return (
    <div className={styles.page}>
      <div className={styles.heading}>
        <h1>Links</h1>
        <Button variant="primary" onClick={openCreate}>
          <Plus size={15} aria-hidden /> New link
        </Button>
      </div>

      <div className={styles.filters}>
        <div className={styles.search}>
          <Search size={15} aria-hidden />
          <TextInput
            type="search"
            aria-label="Search links"
            placeholder="Name, destination or code"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <Select
          aria-label="Collection"
          value={filters.collection ?? ''}
          onChange={(event) => update({ collection: event.target.value || undefined })}
        >
          <option value="">All collections</option>
          <option value="none">No collection</option>
          {collections.data?.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </Select>
        <Select aria-label="Tag" value={filters.tag ?? ''} onChange={(event) => update({ tag: event.target.value || undefined })}>
          <option value="">All tags</option>
          {tags.data?.map((tag) => (
            <option key={tag.id} value={tag.id}>
              {tag.name}
            </option>
          ))}
        </Select>
        <Select
          aria-label="Status"
          value={filters.status ?? ''}
          onChange={(event) => update({ status: event.target.value || undefined })}
        >
          <option value="">Any status</option>
          <option value="active">Active</option>
          <option value="expired">Expired</option>
          <option value="inactive">Paused</option>
        </Select>
        <Select aria-label="Sort" value={filters.ordering} onChange={(event) => update({ ordering: event.target.value })}>
          {SORTS.map((sort) => (
            <option key={sort.value} value={sort.value}>
              {sort.label}
            </option>
          ))}
        </Select>
        {active && (
          <Button variant="ghost" size="sm" onClick={clear}>
            Clear filters
          </Button>
        )}
      </div>

      {selected.length > 0 && (
        <BulkBar
          ids={selected}
          collections={collections.data ?? []}
          tags={tags.data ?? []}
          onDone={() => setSelected([])}
        />
      )}

      <section className={styles.tablePanel} aria-label="Links" data-stale={links.isPlaceholderData}>
        {links.isPending ? (
          <div className={styles.skeleton}>
            {Array.from({ length: 6 }, (_, i) => (
              <Skeleton key={i} height={18} />
            ))}
          </div>
        ) : rows.length === 0 ? (
          active ? (
            <EmptyState title="No links match these filters" action={<Button onClick={clear}>Clear filters</Button>} />
          ) : (
            <EmptyState
              title="No links yet"
              action={
                <Button variant="primary" onClick={openCreate}>
                  <Plus size={15} aria-hidden /> Shorten your first link
                </Button>
              }
            >
              Paste a long URL, pick a code or let Spur make one, and share {window.location.host}/your-code.
            </EmptyState>
          )
        ) : (
          <div className={ui.tableWrap}>
            <table className={`${ui.table} ${styles.table}`}>
              <thead>
                <tr>
                  <th scope="col" className={styles.check}>
                    <input
                      type="checkbox"
                      className={ui.checkbox}
                      aria-label="Select all links on this page"
                      checked={allSelected}
                      onChange={() =>
                        setSelected(allSelected ? [] : Array.from(new Set([...selected, ...rows.map((row) => row.id)])))
                      }
                    />
                  </th>
                  <th scope="col"><Sign>Link</Sign></th>
                  <th scope="col" className={styles.wide}><Sign>Destination</Sign></th>
                  <th scope="col" className={styles.medium}><Sign>Collection</Sign></th>
                  <th scope="col" className={styles.wide}><Sign>Tags</Sign></th>
                  <th scope="col" className={ui.numeric}><Sign>Clicks</Sign></th>
                  <th scope="col" className={styles.medium}><Sign>Last click</Sign></th>
                </tr>
              </thead>
              <tbody>
                {rows.map((link) => {
                  const code = link.short_urls[0]
                  const collection = link.collection ? collectionMap.get(link.collection) : undefined
                  const checked = selected.includes(link.id)
                  return (
                    <tr
                      key={link.id}
                      className={styles.row}
                      data-selected={checked}
                      onClick={(event) => {
                        if ((event.target as HTMLElement).closest('button, input, a')) return
                        navigate(`/links/${link.id}`)
                      }}
                    >
                      <td className={styles.check}>
                        <input
                          type="checkbox"
                          className={ui.checkbox}
                          aria-label={`Select ${link.name}`}
                          checked={checked}
                          onChange={() =>
                            setSelected(checked ? selected.filter((id) => id !== link.id) : [...selected, link.id])
                          }
                        />
                      </td>
                      {/* The cell is labelled by its link text, which the rule cannot see through RouterLink */}
                      {/* oxlint-disable-next-line jsx-a11y/control-has-associated-label */}
                      <td>
                        <div className={styles.linkCell}>
                          <RouterLink to={`/links/${link.id}`} className={styles.linkName}>
                            {link.name}
                          </RouterLink>
                          <span className={styles.codeLine}>
                            {code ? <Code code={code.short_url} /> : <span className={styles.muted}>No code</span>}
                            {code && <CopyCodeButton code={code.short_url} />}
                            {link.short_urls.length > 1 && (
                              <span className={styles.muted}>+{link.short_urls.length - 1}</span>
                            )}
                            <StatusBadge status={link.status} expiresAt={code?.expires_at} />
                          </span>
                        </div>
                      </td>
                      <td className={styles.wide}>
                        <span className={styles.destination} title={link.url}>
                          {displayUrl(link.url)}
                        </span>
                      </td>
                      <td className={styles.medium}>
                        {collection ? (
                          <LineName name={collection.name} color={collection.color} />
                        ) : (
                          <span className={styles.muted}>—</span>
                        )}
                      </td>
                      <td className={styles.wide}>
                        <span className={styles.tags}>
                          {link.tags.map((id) => {
                            const tag = tagMap.get(id)
                            return tag ? <TagChip key={id} name={tag.name} color={tag.color} /> : null
                          })}
                        </span>
                      </td>
                      <td className={`${ui.numeric} ${styles.clicks}`}>{formatNumber(link.clicks)}</td>
                      <td className={`${styles.medium} ${styles.muted}`}>
                        {link.last_clicked_at ? timeAgo(link.last_clicked_at) : 'Never'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
        <Pagination
          page={filters.page ?? 1}
          pageSize={PAGE_SIZE}
          count={links.data?.count ?? 0}
          onPage={(page) => update({ page })}
        />
      </section>
    </div>
  )
}

