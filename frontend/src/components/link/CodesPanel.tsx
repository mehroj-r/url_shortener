import { CircleSlash, Clock, Play, Plus, QrCode, Trash2 } from 'lucide-react'
import { useState, type FormEvent } from 'react'

import { ApiError } from '../../api/client'
import { useCreateCode, useDeleteCode, useUpdateCode } from '../../api/queries'
import type { Link, ShortCode } from '../../api/types'
import { formatDateTime, formatNumber, plural, SHORT_HOST } from '../../lib/format'
import { useToast } from '../../lib/toast'
import { Button, CopyCodeButton, Dialog, Field, FormError, IconButton, Panel, StatusBadge, TextInput } from '../ui'
import styles from './link.module.css'
import { QrDialog } from './QrDialog'

function toLocalInput(iso: string | null): string {
  if (!iso) return ''
  const date = new Date(iso)
  const offset = date.getTimezoneOffset() * 60_000
  return new Date(date.getTime() - offset).toISOString().slice(0, 16)
}

function ExpiryDialog({ code, onClose }: { code: ShortCode | null; onClose: () => void }) {
  const update = useUpdateCode()
  const [value, setValue] = useState('')
  const error = update.error instanceof ApiError ? update.error : null

  return (
    <Dialog
      open={code !== null}
      onClose={onClose}
      title="Expiry"
      width={420}
      footer={
        <>
          {code?.expires_at && (
            <Button
              variant="ghost"
              onClick={async () => {
                await update.mutateAsync({ id: code.id, expires_at: null })
                onClose()
              }}
            >
              Never expire
            </Button>
          )}
          <Button onClick={onClose}>Cancel</Button>
          <Button
            variant="primary"
            loading={update.isPending}
            disabled={!value}
            onClick={async () => {
              if (!code) return
              const ok = await update
                .mutateAsync({ id: code.id, expires_at: new Date(value).toISOString() })
                .then(() => true, () => false)
              if (ok) onClose()
            }}
          >
            Save
          </Button>
        </>
      }
    >
      {code && (
        <Field
          label={`${SHORT_HOST}/${code.short_url} stops redirecting at`}
          error={error?.field('expires_at') ?? (error ? error.message : undefined)}
        >
          {(props) => (
            <TextInput
              {...props}
              type="datetime-local"
              defaultValue={toLocalInput(code.expires_at)}
              onChange={(event) => setValue(event.target.value)}
            />
          )}
        </Field>
      )}
    </Dialog>
  )
}

function AddCode({ link }: { link: Link }) {
  const create = useCreateCode(link.id)
  const toast = useToast()
  const [code, setCode] = useState('')
  const error = create.error instanceof ApiError ? create.error : null

  async function submit(event: FormEvent) {
    event.preventDefault()
    const created = await create.mutateAsync({ short_url: code.trim() || undefined }).catch(() => null)
    if (created) {
      setCode('')
      toast(`Added ${SHORT_HOST}/${created.short_url}`)
    }
  }

  return (
    <form className={styles.addCode} onSubmit={submit}>
      <Field
        label="Another code for this link"
        hint="Use separate codes per channel to compare where clicks come from."
        error={error?.field('short_url') ?? (error && !error.field('short_url') ? error.message : undefined)}
      >
        {(props) => (
          <div className={styles.addCodeRow}>
            <span className={styles.host}>{SHORT_HOST}/</span>
            <TextInput
              {...props}
              className={styles.codeInput}
              placeholder="auto"
              maxLength={64}
              spellCheck={false}
              value={code}
              onChange={(event) => setCode(event.target.value)}
            />
            <Button type="submit" loading={create.isPending}>
              <Plus size={15} aria-hidden /> Add code
            </Button>
          </div>
        )}
      </Field>
    </form>
  )
}

export function CodesPanel({ link }: { link: Link }) {
  const update = useUpdateCode()
  const remove = useDeleteCode()
  const toast = useToast()
  const [qr, setQr] = useState<string | null>(null)
  const [expiry, setExpiry] = useState<ShortCode | null>(null)
  const [deleting, setDeleting] = useState<ShortCode | null>(null)

  const toggle = async (code: ShortCode) => {
    await update
      .mutateAsync({ id: code.id, is_active: !code.is_active })
      .then(
        () => toast(code.is_active ? `Paused ${code.short_url}` : `Resumed ${code.short_url}`),
        () => toast('Could not update the code.', 'error'),
      )
  }

  return (
    <Panel title="Short codes">
      <ul className={styles.codes}>
        {link.short_urls.map((code) => (
          <li key={code.id} className={styles.codeRow} data-status={code.status}>
            <div className={styles.specimen}>
              <span className={styles.specimenHost}>{SHORT_HOST}/</span>
              <span className={styles.specimenCode}>{code.short_url}</span>
            </div>
            <div className={styles.codeMeta}>
              <StatusBadge status={code.status} expiresAt={code.expires_at} />
              <span className="num">{plural(code.clicks, 'click')}</span>
              {code.expires_at && (
                <span className={styles.expiry}>
                  <Clock size={13} aria-hidden /> {code.status === 'expired' ? 'Expired' : 'Expires'}{' '}
                  {formatDateTime(code.expires_at)}
                </span>
              )}
            </div>
            <div className={styles.codeActions}>
              <CopyCodeButton code={code.short_url} size="md" />
              <IconButton label={`QR code for ${code.short_url}`} onClick={() => setQr(code.short_url)}>
                <QrCode size={16} aria-hidden />
              </IconButton>
              <IconButton label={`Set expiry for ${code.short_url}`} onClick={() => setExpiry(code)}>
                <Clock size={16} aria-hidden />
              </IconButton>
              <IconButton
                label={code.is_active ? `Pause ${code.short_url}` : `Resume ${code.short_url}`}
                onClick={() => toggle(code)}
              >
                {code.is_active ? <CircleSlash size={16} aria-hidden /> : <Play size={16} aria-hidden />}
              </IconButton>
              <IconButton label={`Delete ${code.short_url}`} onClick={() => setDeleting(code)}>
                <Trash2 size={16} aria-hidden />
              </IconButton>
            </div>
          </li>
        ))}
      </ul>
      {link.short_urls.length === 0 && (
        <p className={styles.noCodes}>This link has no codes, so nothing points to it. Add one below.</p>
      )}
      <AddCode link={link} />

      <QrDialog code={qr} onClose={() => setQr(null)} />
      <ExpiryDialog key={expiry?.id ?? 'none'} code={expiry} onClose={() => setExpiry(null)} />
      <Dialog
        open={deleting !== null}
        onClose={() => setDeleting(null)}
        title={`Delete ${deleting?.short_url}?`}
        footer={
          <>
            <Button onClick={() => setDeleting(null)}>Cancel</Button>
            <Button
              variant="danger"
              loading={remove.isPending}
              onClick={async () => {
                if (!deleting) return
                await remove.mutateAsync(deleting.id).catch(() => toast('Could not delete the code.', 'error'))
                setDeleting(null)
              }}
            >
              Delete code
            </Button>
          </>
        }
      >
        <p>
          {SHORT_HOST}/{deleting?.short_url} stops redirecting. Its {formatNumber(deleting?.clicks ?? 0)} recorded clicks
          leave the totals, and the code stays reserved so nobody else can take it.
        </p>
        <FormError message={remove.error instanceof ApiError ? remove.error.message : undefined} />
      </Dialog>
    </Panel>
  )
}
