import { LogOut } from 'lucide-react'
import { useState, type FormEvent } from 'react'

import { ApiError } from '../api/client'
import { useChangePassword, useUpdateProfile } from '../api/queries'
import type { Profile } from '../api/types'
import { useAuth } from '../auth/AuthProvider'
import { Button, Field, FormError, Panel, Segmented, Skeleton, TextInput, ui } from '../components/ui'
import { setThemePreference, THEME_OPTIONS, useThemePreference } from '../lib/theme'
import { useToast } from '../lib/toast'
import styles from './ManagePage.module.css'

function ProfileForm({ user }: { user: Profile }) {
  const update = useUpdateProfile()
  const toast = useToast()
  const [form, setForm] = useState({
    first_name: user.first_name,
    last_name: user.last_name,
    username: user.username ?? '',
    phone: user.phone ?? '',
  })
  const error = update.error instanceof ApiError ? update.error : null
  const set = (key: keyof typeof form) => (event: { target: { value: string } }) =>
    setForm((current) => ({ ...current, [key]: event.target.value }))

  async function submit(event: FormEvent) {
    event.preventDefault()
    const ok = await update
      .mutateAsync({ ...form, username: form.username.trim() || null, phone: form.phone.trim() || null })
      .then(() => true, () => false)
    if (ok) toast('Profile saved')
  }

  return (
    <form className={ui.formGrid} onSubmit={submit}>
      <div className={ui.formRow}>
        <Field label="First name" error={error?.field('first_name')}>
          {(props) => <TextInput {...props} required maxLength={30} value={form.first_name} onChange={set('first_name')} />}
        </Field>
        <Field label="Last name" error={error?.field('last_name')}>
          {(props) => <TextInput {...props} required maxLength={30} value={form.last_name} onChange={set('last_name')} />}
        </Field>
      </div>
      <div className={ui.formRow}>
        <Field label="Username" hint="Optional. You can sign in with it." error={error?.field('username')}>
          {(props) => <TextInput {...props} maxLength={150} value={form.username} onChange={set('username')} />}
        </Field>
        <Field label="Phone" hint="Optional. International format, e.g. +998 90 123 45 67." error={error?.field('phone')}>
          {(props) => <TextInput {...props} type="tel" value={form.phone} onChange={set('phone')} />}
        </Field>
      </div>
      <Field label="Email" hint="Your sign-in email can't be changed here.">
        {(props) => <TextInput {...props} value={user.email} disabled />}
      </Field>
      <div>
        <Button type="submit" variant="primary" loading={update.isPending}>
          Save profile
        </Button>
      </div>
    </form>
  )
}

function PasswordForm() {
  const change = useChangePassword()
  const toast = useToast()
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const error = change.error instanceof ApiError ? change.error : null

  async function submit(event: FormEvent) {
    event.preventDefault()
    const ok = await change.mutateAsync({ current_password: current, new_password: next }).then(() => true, () => false)
    if (ok) {
      setCurrent('')
      setNext('')
      toast('Password changed')
    }
  }

  return (
    <form className={ui.formGrid} onSubmit={submit}>
      <div className={ui.formRow}>
        <Field label="Current password" error={error?.field('current_password')}>
          {(props) => (
            <TextInput {...props} type="password" autoComplete="current-password" required value={current} onChange={(e) => setCurrent(e.target.value)} />
          )}
        </Field>
        <Field label="New password" hint="At least 8 characters, not too common." error={error?.field('new_password')}>
          {(props) => (
            <TextInput {...props} type="password" autoComplete="new-password" required value={next} onChange={(e) => setNext(e.target.value)} />
          )}
        </Field>
      </div>
      <FormError message={error && !error.field('current_password') && !error.field('new_password') ? error.message : undefined} />
      <div>
        <Button type="submit" loading={change.isPending}>
          Change password
        </Button>
      </div>
    </form>
  )
}

function AppearanceForm() {
  const theme = useThemePreference()
  return (
    <div className={styles.appearance}>
      <Segmented label="Theme" value={theme} options={THEME_OPTIONS} onChange={setThemePreference} />
      <p className={ui.hint}>System follows your device's light or dark setting. The choice is saved in this browser.</p>
    </div>
  )
}

export default function SettingsPage() {
  const { user, logout } = useAuth()
  return (
    <div className={styles.page}>
      <div className={styles.heading}>
        <h1>Settings</h1>
      </div>
      <Panel title="Profile">{user ? <ProfileForm user={user} /> : <Skeleton height={160} />}</Panel>
      <Panel title="Appearance">
        <AppearanceForm />
      </Panel>
      <Panel title="Password">
        <PasswordForm />
      </Panel>
      <Panel title="Session">
        <Button onClick={() => logout()}>
          <LogOut size={15} aria-hidden /> Sign out on this device
        </Button>
      </Panel>
    </div>
  )
}
