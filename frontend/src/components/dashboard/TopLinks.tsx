import { useNavigate } from 'react-router'

import type { Collection, Link, Summary } from '../../api/types'
import { formatNumber } from '../../lib/format'
import { Code, EmptyState, LineName, Sign, ui } from '../ui'
import { useHighlightTarget } from './highlight'
import styles from './dashboard.module.css'

function Row({
  row,
  total,
  collection,
}: {
  row: Summary['top_links'][number]
  total: number
  collection: Collection | null | undefined
}) {
  const navigate = useNavigate()
  const { active, props } = useHighlightTarget(row.id)
  const share = total ? row.clicks / total : 0
  return (
    <tr
      className={styles.clickableRow}
      data-active={active}
      tabIndex={0}
      onClick={() => navigate(`/links/${row.id}`)}
      onKeyDown={(event) => {
        if (event.key === 'Enter') navigate(`/links/${row.id}`)
      }}
      {...props}
    >
      <td>
        <span className={styles.linkCell}>
          <strong>{row.name}</strong>
          <Code code={row.code} />
        </span>
      </td>
      <td className={styles.hideNarrow}>
        {collection ? <LineName name={collection.name} color={collection.color} /> : <span className={styles.muted}>—</span>}
      </td>
      <td className={ui.numeric}>
        <span className={styles.clicksCell}>
          <span className={styles.shareTrack} aria-hidden>
            <span style={{ width: `${share * 100}%` }} />
          </span>
          {formatNumber(row.clicks)}
        </span>
      </td>
    </tr>
  )
}

export function TopLinks({
  summary,
  links,
  collections,
}: {
  summary: Summary
  links: Map<number, Link>
  collections: Map<number, Collection>
}) {
  if (summary.top_links.length === 0) {
    return (
      <EmptyState title="No clicks in this range">
        Share a short link and its first clicks show up here, ranked.
      </EmptyState>
    )
  }
  return (
    <div className={ui.tableWrap}>
      <table className={ui.table}>
        <thead>
          <tr>
            <th scope="col"><Sign>Link</Sign></th>
            <th scope="col" className={styles.hideNarrow}><Sign>Collection</Sign></th>
            <th scope="col" className={ui.numeric}><Sign>Clicks</Sign></th>
          </tr>
        </thead>
        <tbody>
          {summary.top_links.map((row) => {
            const collectionId = links.get(row.id)?.collection
            return (
              <Row
                key={row.id}
                row={row}
                total={summary.totals.clicks}
                collection={collectionId ? collections.get(collectionId) : null}
              />
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
