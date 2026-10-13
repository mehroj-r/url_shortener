import { useQuery } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { Link as RouterLink, Navigate, useNavigate, useParams } from 'react-router'

import { api, ApiError } from '../api/client'
import { useAuth, type Registration } from '../auth/AuthProvider'
import { Button, Field, FormError, Skeleton, TextInput, ui } from '../components/ui'
import styles from './AuthPage.module.css'
import { AuthScreen } from './LoginPage'

export default function JoinPage() {
  const token = useParams().token ?? ''
  const { status, register } = useAuth()
  const navigate = useNavigate()
  const check = useQuery({
    queryKey: ['invite-check', token],
    queryFn: () => api<{ valid: boolean; invited_by: string | null }>(`/auth/invites/check/${token}/`, { auth: false }),
    retry: false,
  })
  const [form, setForm] = useState<Omit<Registration, 'invite'>>({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    password_repeat: '',
  })
  const [error, setError] = useState<ApiError | null>(null)
  const [pending, setPending] = useState(false)

  if (status === 'authenticated') return <Navigate to="/" replace />

  const set = (key: keyof typeof form) => (event: { target: { value: string } }) =>
    setForm((current) => ({ ...current, [key]: event.target.value }))

  async function submit(event: FormEvent) {
    event.preventDefault()
    setPending(true)
    setError(null)
    try {
      await register({ ...form, invite: token })
      navigate('/', { replace: true })
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : new ApiError(0, 'Could not reach the server. Check your connection.'))
    } finally {
      setPending(false)
    }
  }

  if (check.isPending) {
    return (
      <AuthScreen>
        <Skeleton height={28} width={200} />
      </AuthScreen>
    )
  }

  if (!check.data?.valid) {
    return (
      <AuthScreen>
        <h1>This invite can’t be used</h1>
        <p className={styles.lead}>
          It was already used, has expired or was revoked. Ask the person who invited you for a new link.
        </p>
        <RouterLink to="/login">Sign in instead</RouterLink>
      </AuthScreen>
    )
  }

  const general = error && !['first_name', 'last_name', 'email', 'password', 'password_repeat'].some((f) => error.field(f))

  return (
    <AuthScreen>
      <h1>Join Spur</h1>
      <p className={styles.lead}>{check.data.invited_by} invited you. Create your account to start shortening links.</p>
      <form className={styles.form} onSubmit={submit}>
        <div className={ui.formRow}>
          <Field label="First name" error={error?.field('first_name')}>
            {(props) => <TextInput {...props} autoComplete="given-name" required maxLength={30} value={form.first_name} onChange={set('first_name')} />}
          </Field>
          <Field label="Last name" error={error?.field('last_name')}>
            {(props) => <TextInput {...props} autoComplete="family-name" required maxLength={30} value={form.last_name} onChange={set('last_name')} />}
          </Field>
        </div>
        <Field label="Email" error={error?.field('email')}>
          {(props) => <TextInput {...props} type="email" autoComplete="email" required value={form.email} onChange={set('email')} />}
        </Field>
        <Field label="Password" hint="At least 8 characters, not too common." error={error?.field('password')}>
          {(props) => <TextInput {...props} type="password" autoComplete="new-password" required value={form.password} onChange={set('password')} />}
        </Field>
        <Field label="Repeat password" error={error?.field('password_repeat')}>
          {(props) => (
            <TextInput {...props} type="password" autoComplete="new-password" required value={form.password_repeat} onChange={set('password_repeat')} />
          )}
        </Field>
        <FormError message={general ? (error.field('invite') ?? error.message) : undefined} />
        <Button type="submit" variant="primary" size="lg" loading={pending} className={styles.wide}>
          Create account
        </Button>
      </form>
    </AuthScreen>
  )
}
