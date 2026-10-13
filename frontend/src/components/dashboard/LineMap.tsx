import { CircleSlash, Clock, TimerOff } from 'lucide-react'
import { useCallback, useRef, useState, type CSSProperties, type ReactNode } from 'react'
import { Link as RouterLink } from 'react-router'

import type { Collection, Link } from '../../api/types'
import { lineColor } from '../../lib/colors'
import { formatNumber, plural } from '../../lib/format'
import { LineMark, useNow } from '../ui'
import { useHighlightTarget, useHighlight } from './highlight'
import styles from './LineMap.module.css'

interface Line {
  key: string
  collection: Collection | null
  links: Link[]
  clicks: number
}

const STATION_SPACING = 112
const NARROW_STATION_SPACING = 84
const MIN_SIZE = 12
const MAX_SIZE = 26
const WEEK = 7 * 86_400_000

type StationState = 'open' | 'expiring' | 'closed'

/** Paused or expired links are closed stations; one expiring within a week gets a warning ring. */
function stationState(link: Link, now: number): { state: StationState; label: string | null; icon: ReactNode } {
  if (link.status === 'inactive') return { state: 'closed', label: 'Paused', icon: <CircleSlash size={12} aria-hidden /> }
  if (link.status === 'expired') return { state: 'closed', label: 'Expired', icon: <TimerOff size={12} aria-hidden /> }
  const soonest = link.short_urls
    .filter((code) => code.status === 'active' && code.expires_at)
    .map((code) => new Date(code.expires_at!).getTime() - now)
    .sort((a, b) => a - b)[0]
  if (soonest !== undefined && soonest < WEEK) {
    const days = Math.max(1, Math.ceil(soonest / 86_400_000))
    return { state: 'expiring', label: `Expires in ${days}d`, icon: <Clock size={12} aria-hidden /> }
  }
  return { state: 'open', label: null, icon: null }
}

function Station({
  link,
  clicks,
  size,
  days,
  now,
}: {
  link: Link
  clicks: number
  size: number
  days: number
  now: number
}) {
  const { active, props } = useHighlightTarget(link.id)
  const { arrivingId } = useHighlight()
  const code = link.short_urls[0]?.short_url ?? '—'
  const { state, label, icon } = stationState(link, now)
  return (
    <li className={styles.station} data-active={active} data-arriving={arrivingId === link.id} data-state={state}>
      <RouterLink
        to={`/links/${link.id}`}
        className={styles.stationLink}
        aria-label={`${link.name}, ${code}: ${plural(clicks, 'click')} in ${days} days${label ? `, ${label}` : ''}`}
        {...props}
      >
        <span className={styles.marker} style={{ '--size': `${size}px` } as CSSProperties} data-quiet={clicks === 0} />
        <span className={styles.stationCode}>{code}</span>
        <span className={styles.stationTip} aria-hidden>
          <strong>{link.name}</strong>
          <span className="num">{plural(clicks, 'click')}</span>
          {label && (
            <span className={styles.tipState}>
              {icon}
              {label}
            </span>
          )}
        </span>
      </RouterLink>
    </li>
  )
}

/**
 * Collections drawn as lines: each link is a station on its collection's line,
 * sized by its clicks in the selected range on one scale for the whole map.
 */
export function LineMap({
  collections,
  links,
  clicksByLink,
  days,
}: {
  collections: Collection[]
  links: Link[]
  clicksByLink: Map<number, number>
  days: number
}) {
  const now = useNow()
  const [trackWidth, setTrackWidth] = useState(0)
  const observer = useRef<ResizeObserver | null>(null)
  const measure = useCallback((node: HTMLElement | null) => {
    observer.current?.disconnect()
    if (!node) return
    observer.current = new ResizeObserver(([entry]) => setTrackWidth(entry.contentRect.width))
    observer.current.observe(node)
  }, [])

  const clicksOf = (link: Link) => clicksByLink.get(link.id) ?? 0
  const byCollection = new Map<number | null, Link[]>()
  for (const link of links) {
    const key = link.collection
    byCollection.set(key, [...(byCollection.get(key) ?? []), link])
  }

  const lines: Line[] = [
    ...collections
      .filter((collection) => byCollection.has(collection.id))
      .map((collection) => ({ key: String(collection.id), collection, links: byCollection.get(collection.id)! })),
    ...(byCollection.has(null) ? [{ key: 'none', collection: null, links: byCollection.get(null)! }] : []),
  ]
    .map((line) => ({
      ...line,
      links: [...line.links].sort((a, b) => clicksOf(b) - clicksOf(a) || b.created_at.localeCompare(a.created_at)),
      clicks: line.links.reduce((sum, link) => sum + clicksOf(link), 0),
    }))
    .sort((a, b) => b.clicks - a.clicks || a.key.localeCompare(b.key))

  const spacing = trackWidth < 480 ? NARROW_STATION_SPACING : STATION_SPACING
  const capacity = Math.max(2, Math.floor(trackWidth / spacing))
  const shown = lines.map((line) => line.links.slice(0, line.links.length > capacity ? capacity - 1 : capacity))
  const maxClicks = Math.max(1, ...shown.flat().map(clicksOf))
  const sizeOf = (clicks: number) => Math.round(MIN_SIZE + (MAX_SIZE - MIN_SIZE) * Math.sqrt(clicks / maxClicks))

  return (
    <div className={styles.mapWrap}>
    <ul className={styles.key} aria-label="Map key">
      <li>
        <span className={styles.keyMarker} aria-hidden />
        Size = clicks in the last {days} days
      </li>
      <li>
        <span className={styles.keyMarker} data-state="expiring" aria-hidden />
        Expires within a week
      </li>
      <li>
        <span className={styles.keyMarker} data-state="closed" aria-hidden />
        Paused or expired
      </li>
    </ul>
    <ol className={styles.map} aria-label="Collections as lines">
      {lines.map((line, index) => {
        const stations = shown[index]
        const hidden = line.links.length - stations.length
        // Each station gets an equal share of the track, so short lines have room for whole codes
        const slots = stations.length + (hidden > 0 ? 1 : 0)
        const slot = trackWidth > 0 ? `${Math.min(STATION_SPACING, Math.floor((trackWidth - 8) / slots))}px` : undefined
        const name = line.collection?.name ?? 'No collection'
        const filter = line.collection ? `collection=${line.collection.id}` : 'collection=none'
        return (
          <li key={line.key} className={styles.line} style={{ '--line': lineColor(line.collection?.color ?? 'slate') } as CSSProperties}>
            <div className={styles.lineLabel}>
              <RouterLink to={`/links?${filter}`} className={styles.lineName}>
                <LineMark color={line.collection?.color ?? 'slate'} />
                {name}
              </RouterLink>
              <span className={styles.lineMeta}>
                {plural(line.links.length, 'link')} · <span className="num">{formatNumber(line.clicks)}</span> clicks
              </span>
            </div>
            <ol
              className={styles.track}
              ref={index === 0 ? measure : undefined}
              style={{ '--slot': slot } as CSSProperties}
              aria-label={`${name} links`}
            >
              {stations.map((link) => (
                <Station
                  key={link.id}
                  link={link}
                  clicks={clicksOf(link)}
                  size={sizeOf(clicksOf(link))}
                  days={days}
                  now={now}
                />
              ))}
              {hidden > 0 && (
                <li className={styles.terminus}>
                  <RouterLink to={`/links?${filter}`} aria-label={`${hidden} more links in ${name}`}>
                    +{hidden}
                  </RouterLink>
                </li>
              )}
            </ol>
          </li>
        )
      })}
    </ol>
    </div>
  )
}
