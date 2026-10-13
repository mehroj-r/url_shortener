const API_ROOT = '/api/v1'
const REFRESH_KEY = 'spur.refresh'

type FieldErrors = Record<string, string[]>

export class ApiError extends Error {
  readonly status: number
  readonly fields: FieldErrors

  constructor(status: number, message: string, fields: FieldErrors = {}) {
    super(message)
    this.status = status
    this.fields = fields
  }

  /** The first message for a field, for showing under that input. */
  field(name: string): string | undefined {
    return this.fields[name]?.[0]
  }
}

function toFieldErrors(error: unknown): FieldErrors {
  if (!error || typeof error !== 'object') return {}
  const fields: FieldErrors = {}
  for (const [key, value] of Object.entries(error)) {
    if (Array.isArray(value)) fields[key] = value.map(String)
    else if (typeof value === 'string') fields[key] = [value]
  }
  return fields
}

function errorMessage(status: number, fields: FieldErrors): string {
  const detail = fields.detail?.[0] ?? fields.non_field_errors?.[0] ?? Object.values(fields)[0]?.[0]
  if (detail) return detail
  if (status === 429) return 'Too many attempts. Wait a minute and try again.'
  if (status >= 500) return 'The server had a problem. Try again in a moment.'
  return 'Something went wrong.'
}

function readRefresh(): string | null {
  try {
    return localStorage.getItem(REFRESH_KEY)
  } catch {
    return null
  }
}

let accessToken: string | null = null
let refreshing: Promise<boolean> | null = null
let unauthorizedHandler: () => void = () => {}

export const session = {
  get hasRefreshToken() {
    return readRefresh() !== null
  },
  get refreshToken() {
    return readRefresh()
  },
  store(access: string, refresh: string) {
    accessToken = access
    try {
      localStorage.setItem(REFRESH_KEY, refresh)
    } catch {
      // Private mode: the session lasts until the tab closes
    }
  },
  clear() {
    accessToken = null
    try {
      localStorage.removeItem(REFRESH_KEY)
    } catch {
      // nothing stored
    }
  },
  onUnauthorized(handler: () => void) {
    unauthorizedHandler = handler
  },
}

/** Exchange the refresh token for a new access token; concurrent callers share one request. */
export function refreshAccessToken(): Promise<boolean> {
  const refresh = readRefresh()
  if (!refresh) return Promise.resolve(false)
  refreshing ??= fetch(`${API_ROOT}/auth/token-refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  })
    .then(async (response) => {
      if (!response.ok) return false
      const body = await response.json()
      accessToken = body.data.access
      if (body.data.refresh) session.store(body.data.access, body.data.refresh)
      return true
    })
    .catch(() => false)
    .finally(() => {
      refreshing = null
    })
  return refreshing
}

type Query = Record<string, string | number | boolean | null | undefined>

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE'
  body?: unknown
  query?: Query
  auth?: boolean
  signal?: AbortSignal
}

export function buildUrl(path: string, query?: Query): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value !== undefined && value !== null && value !== '') params.set(key, String(value))
  }
  const qs = params.toString()
  return `${API_ROOT}${path}${qs ? `?${qs}` : ''}`
}

export async function api<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, query, auth = true, signal } = options

  const send = () =>
    fetch(buildUrl(path, query), {
      method,
      signal,
      headers: {
        Accept: 'application/json',
        ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
        ...(auth && accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })

  let response = await send()
  if (response.status === 401 && auth) {
    if (await refreshAccessToken()) {
      response = await send()
    }
    if (response.status === 401) {
      session.clear()
      unauthorizedHandler()
    }
  }

  if (response.status === 204) return undefined as T

  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    const fields = toFieldErrors(payload?.error ?? payload)
    throw new ApiError(response.status, errorMessage(response.status, fields), fields)
  }
  return (payload?.data ?? payload) as T
}
