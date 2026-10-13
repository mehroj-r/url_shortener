import type { Summary } from '../../api/types'
import { formatCount, formatNumber, plural } from '../../lib/format'
import { Skeleton } from '../ui'
import { DailyBars } from './DailyBars'
import styles from './ClicksOverview.module.css'

/** "654 clicks from 649 visitors in the last 30 days, 2.3× the previous 30." */
export function rangeSentence({ totals, range }: Pick<Summary, 'totals' | 'range'>): string {
  const base = `${plural(totals.clicks, 'click')} from ${plural(totals.visitors, 'visitor')} in the last ${range.days} days`
  const { clicks, previous_clicks: previous } = totals
  if (previous === 0) return `${base}.`
  const ratio = clicks / previous
  if (ratio >= 1.1) return `${base}, ${ratio.toFixed(1).replace(/\.0$/, '')}× the previous ${range.days}.`
  if (ratio <= 0.9) return `${base}, down from ${formatNumber(previous)} the previous ${range.days}.`
  return `${base}, about the same as the previous ${range.days}.`
}

/** Today's count over its daily history; the range total reads as a sentence underneath. */
export function ClicksOverview({ summary, loading }: { summary: Summary | undefined; loading: boolean }) {
  if (!summary) {
    return (
      <div className={styles.loading} aria-busy={loading}>
        <Skeleton width={120} height={48} />
        <Skeleton height={100} />
      </div>
    )
  }
  const { series, range } = summary
  const today = series.at(-1)?.clicks ?? 0

  return (
    <div className={styles.overview} data-stale={loading}>
      <p className={styles.today}>
        <span className={styles.hero}>{formatCount(today)}</span>
        <span className={styles.heroLabel}>{today === 1 ? 'click today' : 'clicks today'}</span>
      </p>
      <DailyBars series={series} label={`Clicks per day over the last ${range.days} days`} />
      <p className={styles.sentence}>{rangeSentence(summary)}</p>
      {summary.totals.bots > 0 && (
        <p className={styles.note}>
          {plural(summary.totals.bots, 'link preview')} from apps like Telegram and WhatsApp not counted.
        </p>
      )}
    </div>
  )
}
