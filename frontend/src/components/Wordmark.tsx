import styles from './Wordmark.module.css'

/** The Spur mark (a short branch leaving a main line) and the product name. */
export function Wordmark() {
  return (
    <span className={styles.wordmark}>
      <svg className={styles.mark} width="20" height="20" viewBox="0 0 20 20" aria-hidden>
        <g fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <path d="M2 14.5h16" />
          <path d="M5 14.5c4.2 0 4.6-8 9.5-8" />
        </g>
        <circle cx="15" cy="6.5" r="2.4" className={styles.dot} />
      </svg>
      Spur
    </span>
  )
}
