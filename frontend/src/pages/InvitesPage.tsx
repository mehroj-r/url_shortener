import { CircleCheck, Clock, Copy, TimerOff, Trash2 } from 'lucide-react'
import { useState, type FormEvent, type ReactNode } from 'react'

import { ApiError } from '../api/client'
import { useCreateInvite, useInvites, useRevokeInvite } from '../api/queries'
import type { Invite } from '../api/types'
import { Button, EmptyState, Field, FormError, IconButton, Panel, Select, Skeleton, TextInput, ui } from '../components/ui'
import { formatDate, formatDateTime } from '../lib/format'
import { copyText, useToast } from '../lib/toast'
import styles from './ManagePage.module.css'

function inviteUrl(token: string) {
  return `${window.location.origin}/app/join/${token}`
}

const STATUS: Record<Invite['status'], { tone: string; label: string; icon: ReactNode }> = {
  pending: { tone: 'off', label: 'Waiting', icon: <Clock size={12} aria-hidden /> },
  used: { tone: 'off', label: 'Used', icon: <CircleCheck size={12} aria-hidden /> },
  expired: { tone: 'danger', label: 'Expired', icon: <TimerOff size={12} aria-hidden /> },
}

function InviteItem({ invite }: { invite: Invite }) {
  const revoke = useRevokeInvite()
  const toast = useToast()
  const copy = async () => {
    const ok = await copyText(inviteUrl(invite.token))
    toast(ok ? 'Invite link copied' : 'Copy failed. Select the link and copy it manually.', ok ? 'info' : 'error')
  }

  return (
    <li className={styles.item} data-kind="invite">
      <span className={ui.badge} data-tone={STATUS[invite.status].tone}>
        {STATUS[invite.status].icon}
        {STATUS[invite.status].label}
      </span>
      <span className={styles.itemName}>
        <strong>{invite.note || 'Invite'}</strong>
        <span>
          {invite.status === 'used'
            ? `Joined as ${invite.used_by_name} on ${formatDate(invite.used_at!)}`
            : invite.status === 'expired'
              ? `Expired ${formatDate(invite.expires_at)}`
              : `Valid until ${formatDateTime(invite.expires_at)}`}
        </span>
      </span>
      <span className={styles.itemStats}>Created {formatDate(invite.created_at)}</span>
      <span className={styles.itemActions}>
        {invite.status === 'pending' && (
          <>
            <IconButton label="Copy invite link" onClick={copy}>
              <Copy size={15} aria-hidden />
            </IconButton>
            <IconButton
              label="Revoke invite"
              onClick={() =>
                revoke.mutateAsync(invite.id).then(
                  () => toast('Invite revoked'),
                  () => toast('Could not revoke the invite.', 'error'),
                )
              }
            >
              <Trash2 size={15} aria-hidden />
            </IconButton>
          </>
        )}
      </span>
    </li>
  )
}

export default function InvitesPage() {
  const invites = useInvites()
  const create = useCreateInvite()
  const toast = useToast()
  const [note, setNote] = useState('')
  const [days, setDays] = useState(7)
  const [created, setCreated] = useState<Invite | null>(null)
  const error = create.error instanceof ApiError ? create.error : null

  async function submit(event: FormEvent) {
    event.preventDefault()
    const invite = await create.mutateAsync({ note: note.trim(), expires_in_days: days }).catch(() => null)
    if (!invite) return
    setCreated(invite)
    setNote('')
    const ok = await copyText(inviteUrl(invite.token))
    if (ok) toast('Invite link copied. Send it to them.')
  }

  return (
    <div className={styles.page}>
      <div className={styles.heading}>
        <h1>Invites</h1>
        <p>Spur is invite-only. Each invite link creates one account and works once, until it expires.</p>
      </div>

      <Panel title="Invite someone">
        <form className={styles.createRow} onSubmit={submit}>
          <Field label="Who is it for?" hint="Only you see this note." error={error?.field('note')}>
            {(props) => (
              <TextInput {...props} maxLength={120} placeholder="e.g. Aziz from work" value={note} onChange={(e) => setNote(e.target.value)} />
            )}
          </Field>
          <Field label="Valid for">
            {(props) => (
              <Select {...props} value={days} onChange={(e) => setDays(Number(e.target.value))}>
                {[1, 3, 7, 14, 30].map((n) => (
                  <option key={n} value={n}>
                    {n === 1 ? '1 day' : `${n} days`}
                  </option>
                ))}
              </Select>
            )}
          </Field>
          <Button type="submit" variant="primary" loading={create.isPending}>
            Create invite link
          </Button>
        </form>
        <FormError message={error && !error.field('note') ? error.message : undefined} />
        {created && (
          <p className={ui.hint} style={{ marginTop: 12 }} role="status">
            <code>{inviteUrl(created.token)}</code>
          </p>
        )}
      </Panel>

      <Panel title="Sent invites">
        {invites.isPending ? (
          <Skeleton height={80} />
        ) : invites.data?.length ? (
          <ul className={styles.list}>
            {invites.data.map((invite) => (
              <InviteItem key={invite.id} invite={invite} />
            ))}
          </ul>
        ) : (
          <EmptyState title="No invites yet">Create a link above and send it to the person you want to invite.</EmptyState>
        )}
      </Panel>
    </div>
  )
}
