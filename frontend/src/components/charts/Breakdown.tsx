import { Bot, Globe, Monitor, Smartphone, Tablet } from 'lucide-react'
import type { ReactNode } from 'react'

import type { Breakdown as Row } from '../../api/types'
import { formatNumber } from '../../lib/format'
import styles from './charts.module.css'

const DEVICE_ICONS: Record<string, ReactNode> = {
  desktop: <Monitor size={14} aria-hidden />,
  mobile: <Smartphone size={14} aria-hidden />,
  tablet: <Tablet size={14} aria-hidden />,
  bot: <Bot size={14} aria-hidden />,
}

export function deviceIcon(device: string) {
  return DEVICE_ICONS[device] ?? <Globe size={14} aria-hidden />
}

const LABELS: Record<string, string> = { desktop: 'Desktop', mobile: 'Mobile', tablet: 'Tablet', other: 'Other' }

/**
 * Share of all clicks in the range, so every breakdown uses the same scale:
 * a bar half the track long is half the clicks.
 */
export function BreakdownList({
  rows,
  total,
  kind,
  empty,
}: {
  rows: Row[]
  total: number
  kind: 'referrer' | 'device' | 'plain'
  empty: string
}) {
  if (rows.length === 0 || total === 0) return <p className={styles.emptyText}>{empty}</p>
  return (
    <ul className={styles.breakdown}>
      {rows.map((row) => {
        const share = row.clicks / total
        const name =
          kind === 'referrer' ? (row.name ?? 'Direct') : kind === 'device' ? (LABELS[row.name ?? ''] ?? row.name) : row.name || 'Unknown'
        return (
          <li key={row.name ?? 'none'}>
            <span className={styles.breakdownName}>
              {kind === 'device' && deviceIcon(row.name ?? '')}
              <span>{name}</span>
            </span>
            <span className={styles.breakdownTrack} aria-hidden>
              <span style={{ width: `${Math.max(share * 100, 1.5)}%` }} />
            </span>
            <span className={styles.breakdownValue}>
              <strong className="num">{formatNumber(row.clicks)}</strong>
              <span className="num">{Math.round(share * 100)}%</span>
            </span>
          </li>
        )
      })}
    </ul>
  )
}

/** Clicks by hour of day, local time. */
export function HourStrip({ hours }: { hours: number[] }) {
  const max = Math.max(1, ...hours)
  const total = hours.reduce((sum, n) => sum + n, 0)
  if (total === 0) return <p className={styles.emptyText}>No clicks in this range yet.</p>
  const busiest = hours.indexOf(Math.max(...hours))
  return (
    <figure className={styles.hours}>
      <div className={styles.hourBars} role="img" aria-label={`Busiest hour: ${busiest}:00 to ${busiest + 1}:00`}>
        {hours.map((count, hour) => (
          <span key={hour} title={`${String(hour).padStart(2, '0')}:00 · ${formatNumber(count)} clicks`}>
            <span style={{ height: `${(count / max) * 100}%` }} data-peak={hour === busiest} />
          </span>
        ))}
      </div>
      <figcaption className={styles.hourAxis}>
        <span>00</span>
        <span>06</span>
        <span>12</span>
        <span>18</span>
        <span>23</span>
      </figcaption>
    </figure>
  )
}
