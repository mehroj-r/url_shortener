import { useState, type FormEvent, type ReactNode } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router'

import { ApiError } from '../api/client'
import { useAuth } from '../auth/AuthProvider'
import { Button, Field, FormError, TextInput } from '../components/ui'
import { Wordmark } from '../components/Wordmark'
import styles from './AuthPage.module.css'

export function AuthScreen({ children }: { children: ReactNode }) {
  return (
    <main className={styles.screen}>
      <div className={styles.brand}>
        <Wordmark />
      </div>
      <div className={styles.card}>{children}</div>
    </main>
  )
}

export default function LoginPage() {
  const { status, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string>()
  const [pending, setPending] = useState(false)

  if (status === 'authenticated') {
    return <Navigate to={(location.state as { from?: string } | null)?.from ?? '/'} replace />
  }

  async function submit(event: FormEvent) {
    event.preventDefault()
    setPending(true)
    setError(undefined)
    try {
      await login({ identifier, password })
      navigate((location.state as { from?: string } | null)?.from ?? '/', { replace: true })
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.status === 400
            ? 'That email, username or phone and password don’t match an active account.'
            : caught.message
          : 'Could not reach the server. Check your connection.',
      )
    } finally {
      setPending(false)
    }
  }

  return (
    <AuthScreen>
      <h1>Sign in</h1>
      <p className={styles.lead}>Your short links on {window.location.host}.</p>
      <form className={styles.form} onSubmit={submit}>
        <Field label="Email, username or phone">
          {(props) => (
            <TextInput
              {...props}
              autoComplete="username"
              // The page has one job; focus starts where it is done
              // oxlint-disable-next-line jsx-a11y/no-autofocus
              autoFocus
              required
              value={identifier}
              onChange={(event) => setIdentifier(event.target.value)}
            />
          )}
        </Field>
        <Field label="Password">
          {(props) => (
            <TextInput
              {...props}
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          )}
        </Field>
        <FormError message={error} />
        <Button type="submit" variant="primary" size="lg" loading={pending} className={styles.wide}>
          Sign in
        </Button>
      </form>
      <p className={styles.footnote}>New here? Accounts are by invitation. Ask someone who uses Spur for an invite link.</p>
    </AuthScreen>
  )
}
