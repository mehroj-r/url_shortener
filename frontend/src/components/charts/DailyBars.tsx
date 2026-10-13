import { useCallback, useId, useMemo, useRef, useState, type PointerEvent } from 'react'

import { formatDay, formatNumber } from '../../lib/format'
import styles from './charts.module.css'

export interface DayCount {
  date: string
  clicks: number
}

/**
 * The first day of the most recent run of unusually busy days: at least five clicks
 * and three times the typical (median non-zero) day. Null when nothing stands out.
 */
export function findSpikeOnset(series: DayCount[]): number | null {
  const busy = series.map((day) => day.clicks).filter((n) => n > 0).sort((a, b) => a - b)
  if (busy.length < 3) return null
  const median = busy[Math.floor(busy.length / 2)]
  const threshold = Math.max(5, median * 3)
  for (let i = series.length - 1; i >= 0; i--) {
    if (series[i].clicks >= threshold && (i === 0 || series[i - 1].clicks < threshold)) return i
  }
  return null
}

const HEIGHT = 120
const AXIS = 22

/** Daily clicks as a bar strip, with the onset of the latest spike marked. */
export function DailyBars({ series, label }: { series: DayCount[]; label: string }) {
  const [active, setActive] = useState<number | null>(null)
  const [width, setWidth] = useState(0)
  const observer = useRef<ResizeObserver | null>(null)
  const tableId = useId()
  const [showTable, setShowTable] = useState(false)

  const measure = useCallback((node: SVGSVGElement | null) => {
    observer.current?.disconnect()
    if (!node) return
    observer.current = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width))
    observer.current.observe(node)
  }, [])

  const max = Math.max(1, ...series.map((day) => day.clicks))
  const niceMax = useMemo(() => {
    const step = 10 ** Math.floor(Math.log10(max))
    return Math.ceil(max / step) * step
  }, [max])
  const onset = findSpikeOnset(series)
  const slot = series.length ? width / series.length : 0
  const barWidth = Math.max(1, Math.min(24, slot - 2))
  const radius = Math.min(4, barWidth / 2)
  const plotHeight = HEIGHT - AXIS
  const y = (value: number) => plotHeight - (value / niceMax) * (plotHeight - 8)

  const pick = (event: PointerEvent<SVGSVGElement>) => {
    const rect = event.currentTarget.getBoundingClientRect()
    const index = Math.floor(((event.clientX - rect.left) / rect.width) * series.length)
    setActive(Math.min(series.length - 1, Math.max(0, index)))
  }

  const ticks = series.length > 1 ? [0, Math.floor((series.length - 1) / 2), series.length - 1] : [0]
  const activeDay = active !== null ? series[active] : null

  return (
    <div className={styles.bars}>
      <div className={styles.annotations} aria-hidden={onset === null}>
        {onset !== null && width > 0 && (
          <span className={styles.onsetLabel} style={{ left: Math.min(onset * slot, width - 120) }}>
            Spike from {formatDay(series[onset].date)}
          </span>
        )}
      </div>
      <div className={styles.plot}>
        {/* The hover readout is an enhancement for pointers; every value is in the table view below */}
        {/* oxlint-disable-next-line jsx-a11y/no-noninteractive-element-interactions */}
        <svg
          ref={measure}
          className={styles.svg}
          height={HEIGHT}
          role="img"
          aria-label={`${label}. Open the table view for each day's count.`}
          onPointerMove={pick}
          onPointerLeave={() => setActive(null)}
        >
          <line className={styles.baseline} x1={0} x2={width} y1={plotHeight + 0.5} y2={plotHeight + 0.5} />
          <line className={styles.grid} x1={0} x2={width} y1={y(niceMax) + 0.5} y2={y(niceMax) + 0.5} />
          {width > 0 &&
            series.map((day, i) => {
              const top = Math.min(y(day.clicks), plotHeight - radius)
              const x = i * slot + (slot - barWidth) / 2
              const today = i === series.length - 1
              return (
                <g key={day.date}>
                  {day.clicks > 0 && (
                    <path
                      className={styles.bar}
                      data-today={today}
                      data-active={i === active}
                      d={`M${x},${plotHeight} V${top + radius} Q${x},${top} ${x + radius},${top} H${x + barWidth - radius} Q${x + barWidth},${top} ${x + barWidth},${top + radius} V${plotHeight} Z`}
                    />
                  )}
                </g>
              )
            })}
          {onset !== null && width > 0 && (
            <g className={styles.onset}>
              <line x1={onset * slot + 0.5} x2={onset * slot + 0.5} y1={0} y2={plotHeight} />
            </g>
          )}
          {activeDay && width > 0 && (
            <line
              className={styles.crosshair}
              x1={active! * slot + slot / 2}
              x2={active! * slot + slot / 2}
              y1={0}
              y2={plotHeight}
            />
          )}
          <text className={styles.tick} x={0} y={y(niceMax) - 4}>
            {formatNumber(niceMax)}
          </text>
          {width > 0 &&
            ticks.map((i) => (
              <text
                key={i}
                className={styles.tick}
                x={i === 0 ? 0 : i === series.length - 1 ? width : i * slot + slot / 2}
                y={HEIGHT - 4}
                textAnchor={i === 0 ? 'start' : i === series.length - 1 ? 'end' : 'middle'}
              >
                {i === series.length - 1 ? 'Today' : formatDay(series[i].date)}
              </text>
            ))}
        </svg>
        {activeDay && (
          <div
            className={styles.tooltip}
            style={{ left: Math.min(Math.max(active! * slot + slot / 2, 60), width - 60) }}
            aria-hidden
          >
            <strong className="num">{formatNumber(activeDay.clicks)}</strong>
            <span>{formatDay(activeDay.date)}</span>
          </div>
        )}
      </div>
      <button
        type="button"
        className={styles.tableToggle}
        aria-expanded={showTable}
        aria-controls={tableId}
        onClick={() => setShowTable((open) => !open)}
      >
        {showTable ? 'Hide table' : 'View as table'}
      </button>
      {showTable && (
        <div id={tableId} className={styles.dataTable}>
          <table>
            <caption className="visually-hidden">{label}</caption>
            <thead>
              <tr>
                <th scope="col">Day</th>
                <th scope="col">Clicks</th>
              </tr>
            </thead>
            <tbody>
              {[...series].reverse().map((day) => (
                <tr key={day.date}>
                  <td>{formatDay(day.date)}</td>
                  <td className="num">{formatNumber(day.clicks)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
