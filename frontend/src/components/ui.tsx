import { CircleAlert, CircleSlash, Clock, Copy, TimerOff, X } from 'lucide-react'
import {
  useEffect,
  useId,
  useRef,
  useState,
  type ButtonHTMLAttributes,
  type CSSProperties,
  type InputHTMLAttributes,
  type ReactNode,
  type SelectHTMLAttributes,
} from 'react'

import type { CodeStatus, TagColor } from '../api/types'
import { lineColor } from '../lib/colors'
import { SHORT_HOST, shortLink } from '../lib/format'
import { copyText, useToast } from '../lib/toast'
import styles from './ui.module.css'

export { styles as ui }

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
}

export function Button({
  variant = 'secondary',
  size = 'md',
  loading = false,
  className,
  children,
  disabled,
  type = 'button',
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={[styles.button, className].filter(Boolean).join(' ')}
      data-variant={variant}
      data-size={size}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...props}
    >
      {loading && <span className={styles.spinner} aria-hidden />}
      {children}
    </button>
  )
}

export function IconButton({
  label,
  size = 'md',
  variant = 'ghost',
  children,
  ...props
}: Omit<ButtonProps, 'aria-label'> & { label: string }) {
  return (
    <Button
      variant={variant}
      size={size}
      className={styles.iconButton}
      aria-label={label}
      title={label}
      {...props}
    >
      {children}
    </Button>
  )
}

interface FieldProps {
  label: ReactNode
  hint?: ReactNode
  error?: string
  children: (props: { id: string; 'aria-invalid'?: boolean; 'aria-describedby'?: string }) => ReactNode
  className?: string
}

/** Label, control, hint and error wired together for assistive tech. */
export function Field({ label, hint, error, children, className }: FieldProps) {
  const id = useId()
  const hintId = `${id}-hint`
  const errorId = `${id}-error`
  const describedBy = [hint && hintId, error && errorId].filter(Boolean).join(' ') || undefined
  return (
    <div className={[styles.field, className].filter(Boolean).join(' ')}>
      <label className={styles.label} htmlFor={id}>
        {label}
      </label>
      {children({ id, 'aria-invalid': error ? true : undefined, 'aria-describedby': describedBy })}
      {hint && !error && (
        <p id={hintId} className={styles.hint}>
          {hint}
        </p>
      )}
      {error && (
        <p id={errorId} className={styles.error}>
          <CircleAlert size={14} aria-hidden />
          {error}
        </p>
      )}
    </div>
  )
}

export function TextInput({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={[styles.input, className].filter(Boolean).join(' ')} {...props} />
}

export function Select({ className, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={[styles.select, className].filter(Boolean).join(' ')} {...props} />
}

export function FormError({ message }: { message?: string }) {
  if (!message) return null
  return (
    <div className={styles.formError} role="alert">
      <CircleAlert size={16} aria-hidden style={{ flex: 'none', marginTop: 2 }} />
      <span>{message}</span>
    </div>
  )
}

export function Panel({
  title,
  actions,
  children,
  className,
  bodyClassName,
  id,
}: {
  title?: ReactNode
  actions?: ReactNode
  children: ReactNode
  className?: string
  bodyClassName?: string
  id?: string
}) {
  const headingId = useId()
  return (
    <section
      id={id}
      className={[styles.panel, className].filter(Boolean).join(' ')}
      aria-labelledby={title ? headingId : undefined}
    >
      {(title || actions) && (
        <header className={styles.panelHeader}>
          {title && (
            <h2 id={headingId} className={styles.panelTitle}>
              {title}
            </h2>
          )}
          {actions}
        </header>
      )}
      <div className={[styles.panelBody, bodyClassName].filter(Boolean).join(' ')}>{children}</div>
    </section>
  )
}

export function Segmented<T extends string | number>({
  value,
  options,
  onChange,
  label,
}: {
  value: T
  options: { value: T; label: string }[]
  onChange: (value: T) => void
  label: string
}) {
  return (
    <div className={styles.segmented} role="group" aria-label={label}>
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          className={styles.segment}
          aria-pressed={option.value === value}
          onClick={() => onChange(option.value)}
        >
          {option.label}
        </button>
      ))}
    </div>
  )
}

export function Sign({ children, className }: { children: ReactNode; className?: string }) {
  return <span className={[styles.sign, className].filter(Boolean).join(' ')}>{children}</span>
}

export function LineDot({ color, className }: { color: TagColor | null | undefined; className?: string }) {
  return (
    <span
      className={[styles.lineDot, className].filter(Boolean).join(' ')}
      style={{ '--dot': lineColor(color) } as CSSProperties}
      aria-hidden
    />
  )
}

/** A collection's marker: a short length of its line ending in a station. Tags use the plain dot. */
export function LineMark({ color, className }: { color: TagColor | null | undefined; className?: string }) {
  return (
    <span
      className={[styles.lineMark, className].filter(Boolean).join(' ')}
      style={{ '--dot': lineColor(color) } as CSSProperties}
      aria-hidden
    />
  )
}

export function LineName({ name, color }: { name: string; color: TagColor | null | undefined }) {
  return (
    <span className={styles.lineName}>
      <LineMark color={color} />
      <span>{name}</span>
    </span>
  )
}

export function TagChip({ name, color }: { name: string; color: TagColor }) {
  return (
    <span className={styles.tagChip}>
      <LineDot color={color} />
      {name}
    </span>
  )
}

const STATUS: Record<CodeStatus, { label: string; tone: string; icon: ReactNode } | null> = {
  active: null,
  expired: { label: 'Expired', tone: 'danger', icon: <TimerOff size={12} aria-hidden /> },
  inactive: { label: 'Paused', tone: 'off', icon: <CircleSlash size={12} aria-hidden /> },
}

const DAY = 86_400_000

/** The current time, refreshed every minute so relative labels stay honest. */
export function useNow(intervalMs = 60_000) {
  const [now, setNow] = useState(() => Date.now())
  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), intervalMs)
    return () => window.clearInterval(timer)
  }, [intervalMs])
  return now
}

/** Nothing for a healthy link; a badge when it is paused, expired or about to expire. */
export function StatusBadge({ status, expiresAt }: { status: CodeStatus; expiresAt?: string | null }) {
  const now = useNow()
  const known = STATUS[status]
  if (known) {
    return (
      <span className={styles.badge} data-tone={known.tone}>
        {known.icon}
        {known.label}
      </span>
    )
  }
  if (expiresAt) {
    const left = new Date(expiresAt).getTime() - now
    if (left < 7 * DAY) {
      const days = Math.max(1, Math.ceil(left / DAY))
      return (
        <span className={styles.badge} data-tone="warn">
          <Clock size={12} aria-hidden />
          {left < DAY ? 'Expires today' : `Expires in ${days}d`}
        </span>
      )
    }
  }
  return null
}

export function Code({ code, host = false }: { code: string; host?: boolean }) {
  return (
    <span className={styles.code}>
      {host && <span className={styles.codeHost}>{SHORT_HOST}/</span>}
      <span className={styles.codeValue}>{code}</span>
    </span>
  )
}

export function CopyCodeButton({ code, size = 'sm' }: { code: string; size?: 'sm' | 'md' }) {
  const toast = useToast()
  return (
    <IconButton
      label={`Copy ${SHORT_HOST}/${code}`}
      size={size}
      onClick={async (event) => {
        event.stopPropagation()
        const ok = await copyText(shortLink(code))
        toast(ok ? `Copied ${SHORT_HOST}/${code}` : 'Copy failed. Select the link and copy it manually.', ok ? 'info' : 'error')
      }}
    >
      <Copy size={15} aria-hidden />
    </IconButton>
  )
}

export function EmptyState({ title, children, action }: { title: string; children?: ReactNode; action?: ReactNode }) {
  return (
    <div className={styles.empty}>
      <h3>{title}</h3>
      {children && <p>{children}</p>}
      {action}
    </div>
  )
}

export function Skeleton({ width = '100%', height = 12 }: { width?: number | string; height?: number }) {
  return <span className={styles.skeleton} style={{ width, height }} aria-hidden />
}

/** A modal on the native <dialog> element: focus trap, Escape and the top layer for free. */
export function Dialog({
  open,
  onClose,
  title,
  children,
  footer,
  width,
}: {
  open: boolean
  onClose: () => void
  title: string
  children: ReactNode
  footer?: ReactNode
  width?: number
}) {
  const ref = useRef<HTMLDialogElement>(null)
  useEffect(() => {
    const dialog = ref.current
    if (!dialog) return
    if (open && !dialog.open) {
      dialog.showModal()
      dialog.querySelector<HTMLElement>('[data-autofocus]')?.focus()
    }
    if (!open && dialog.open) dialog.close()
  }, [open])

  // A click on the backdrop lands on the dialog itself; Escape is the keyboard equivalent
  return (
    // oxlint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/no-noninteractive-element-interactions
    <dialog
      ref={ref}
      className={styles.dialog}
      style={width ? { width: `min(${width}px, calc(100vw - 32px))` } : undefined}
      onClose={onClose}
      onClick={(event) => {
        if (event.target === ref.current) onClose()
      }}
      aria-label={title}
    >
      {open && (
        <>
          <div className={styles.dialogHeader}>
            <h2>{title}</h2>
            <IconButton label="Close" size="sm" onClick={onClose}>
              <X size={16} aria-hidden />
            </IconButton>
          </div>
          <div className={styles.dialogBody}>{children}</div>
          {footer && <div className={styles.dialogFooter}>{footer}</div>}
        </>
      )}
    </dialog>
  )
}

export function Pagination({
  page,
  pageSize,
  count,
  onPage,
}: {
  page: number
  pageSize: number
  count: number
  onPage: (page: number) => void
}) {
  const pages = Math.max(1, Math.ceil(count / pageSize))
  if (count <= pageSize) return null
  const first = (page - 1) * pageSize + 1
  const last = Math.min(count, page * pageSize)
  return (
    <nav className={styles.pagination} aria-label="Pagination">
      <span className="num">
        {first}–{last} of {count}
      </span>
      <span style={{ display: 'flex', gap: 8 }}>
        <Button size="sm" disabled={page <= 1} onClick={() => onPage(page - 1)}>
          Previous
        </Button>
        <Button size="sm" disabled={page >= pages} onClick={() => onPage(page + 1)}>
          Next
        </Button>
      </span>
    </nav>
  )
}
