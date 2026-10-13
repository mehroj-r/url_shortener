import { useQuery, useQueryClient } from '@tanstack/react-query'
import { createContext, use, useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import { api, refreshAccessToken, session } from '../api/client'
import type { Profile } from '../api/types'

interface LoginResponse {
  user: Profile
  token: { access: string; refresh: string }
}

export interface Credentials {
  identifier: string
  password: string
}

export interface Registration {
  first_name: string
  last_name: string
  email: string
  password: string
  password_repeat: string
  invite: string
}

type Status = 'loading' | 'anonymous' | 'authenticated'

interface AuthContextValue {
  status: Status
  user: Profile | undefined
  login: (credentials: Credentials) => Promise<void>
  register: (data: Registration) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

/** Email, phone or username, judged by what the person typed. */
export function loginField(identifier: string): 'email' | 'phone' | 'username' {
  if (identifier.includes('@')) return 'email'
  if (/^\+?[\d\s()-]{7,}$/.test(identifier)) return 'phone'
  return 'username'
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const client = useQueryClient()
  const [status, setStatus] = useState<Status>(session.hasRefreshToken ? 'loading' : 'anonymous')

  const me = useQuery({
    queryKey: ['me'],
    queryFn: () => api<Profile>('/auth/me/'),
    enabled: status === 'authenticated',
    staleTime: Infinity,
  })

  // Restore the session from the stored refresh token
  useEffect(() => {
    if (status !== 'loading') return
    refreshAccessToken().then((ok) => setStatus(ok ? 'authenticated' : 'anonymous'))
  }, [status])

  useEffect(() => {
    session.onUnauthorized(() => {
      client.clear()
      setStatus('anonymous')
    })
  }, [client])

  const login = useCallback(
    async ({ identifier, password }: Credentials) => {
      const data = await api<LoginResponse>('/auth/login/', {
        method: 'POST',
        auth: false,
        body: { [loginField(identifier)]: identifier.trim(), password },
      })
      session.store(data.token.access, data.token.refresh)
      client.setQueryData(['me'], data.user)
      setStatus('authenticated')
    },
    [client],
  )

  const register = useCallback(
    async (data: Registration) => {
      await api('/auth/register/', { method: 'POST', auth: false, body: data })
      await login({ identifier: data.email, password: data.password })
    },
    [login],
  )

  const logout = useCallback(async () => {
    const refresh = session.refreshToken
    if (refresh) {
      await api('/auth/logout/', { method: 'POST', auth: false, body: { refresh } }).catch(() => undefined)
    }
    session.clear()
    client.clear()
    setStatus('anonymous')
  }, [client])

  const value = useMemo(
    () => ({ status, user: me.data, login, register, logout }),
    [status, me.data, login, register, logout],
  )
  return <AuthContext value={value}>{children}</AuthContext>
}

export function useAuth(): AuthContextValue {
  const value = use(AuthContext)
  if (!value) throw new Error('useAuth must be used inside AuthProvider')
  return value
}
