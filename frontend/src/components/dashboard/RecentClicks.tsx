import { Link as RouterLink } from 'react-router'

import type { Click, Collection, Link } from '../../api/types'
import { formatDateTime, formatDay, formatTime } from '../../lib/format'
import { deviceIcon } from '../charts/Breakdown'
import { Code, EmptyState, LineDot, Skeleton } from '../ui'
import { useHighlight } from './highlight'
import styles from './dashboard.module.css'

function describe(click: Click) {
  return [click.browser, click.os].filter(Boolean).join(' on ') || 'Unknown browser'
}

/** "14:32" today, "Oct 12" before that; the full moment is in the tooltip. */
function when(iso: string) {
  const date = new Date(iso)
  const today = new Date()
  return date.toDateString() === today.toDateString() ? formatTime(iso) : formatDay(iso.slice(0, 10))
}

/** The latest people through the turnstiles, newest first. */
export function RecentClicks({
  clicks,
  loading,
  links,
  collections,
  showLink = true,
}: {
  clicks: Click[] | undefined
  loading: boolean
  links?: Map<number, Link>
  collections?: Map<number, Collection>
  showLink?: boolean
}) {
  const { linkId, setLinkId } = useHighlight()

  if (loading && !clicks) {
    return (
      <div className={styles.skeletonList}>
        {Array.from({ length: 5 }, (_, i) => (
          <Skeleton key={i} height={14} />
        ))}
      </div>
    )
  }
  if (!clicks?.length) {
    return <EmptyState title="Nobody has clicked yet">Each visit appears here the moment it happens.</EmptyState>
  }

  return (
    <ol className={styles.clicks}>
      {clicks.map((click) => {
        const collectionId = links?.get(click.link)?.collection
        const color = collectionId ? collections?.get(collectionId)?.color : 'slate'
        return (
          <li
            key={click.id}
            data-active={linkId === click.link}
            onPointerEnter={() => setLinkId(click.link)}
            onPointerLeave={() => setLinkId(null)}
          >
            <time className={styles.clickTime} dateTime={click.created_at} title={formatDateTime(click.created_at)}>
              {when(click.created_at)}
            </time>
            <span className={styles.clickMain}>
              {showLink ? (
                <RouterLink to={`/links/${click.link}`} className={styles.clickLink}>
                  <LineDot color={color} />
                  <Code code={click.code} />
                </RouterLink>
              ) : (
                <span className={styles.clickSourceStrong}>{click.referer_domain ?? 'Direct'}</span>
              )}
              <span className={styles.clickDetail}>
                {deviceIcon(click.device)}
                <span>
                  {showLink && `${click.referer_domain ?? 'Direct'} · `}
                  {describe(click)}
                </span>
              </span>
            </span>
          </li>
        )
      })}
    </ol>
  )
}
