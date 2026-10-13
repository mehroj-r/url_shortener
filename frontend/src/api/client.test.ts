import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { api, ApiError, session } from './client'

function json(status: number, body: unknown) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
}

describe('api client', () => {
  const fetchMock = vi.fn<typeof fetch>()

  beforeEach(() => {
    vi.stubGlobal('fetch', fetchMock)
    session.clear()
  })

  afterEach(() => {
    fetchMock.mockReset()
    vi.unstubAllGlobals()
  })

  it('unwraps the response envelope', async () => {
    fetchMock.mockResolvedValueOnce(json(200, { success: true, message: 'OK', data: { id: 1 } }))

    await expect(api('/shortener/urls/1/')).resolves.toEqual({ id: 1 })
  })

  it('refreshes an expired access token once and retries', async () => {
    session.store('old-access', 'refresh-token')
    fetchMock
      .mockResolvedValueOnce(json(401, { success: false, error: { detail: 'expired' } }))
      .mockResolvedValueOnce(json(200, { success: true, data: { access: 'new-access' } }))
      .mockResolvedValueOnce(json(200, { success: true, data: { ok: true } }))

    await expect(api('/auth/me/')).resolves.toEqual({ ok: true })

    const [, retryInit] = fetchMock.mock.calls[2]
    expect(new Headers(retryInit!.headers).get('Authorization')).toBe('Bearer new-access')
  })

  it('signs out when the refresh token is rejected', async () => {
    const onUnauthorized = vi.fn()
    session.onUnauthorized(onUnauthorized)
    session.store('old-access', 'refresh-token')
    fetchMock
      .mockResolvedValueOnce(json(401, { error: { detail: 'expired' } }))
      .mockResolvedValueOnce(json(401, { error: { detail: 'bad refresh' } }))

    await expect(api('/auth/me/')).rejects.toBeInstanceOf(ApiError)
    expect(onUnauthorized).toHaveBeenCalledOnce()
    expect(session.hasRefreshToken).toBe(false)
  })

  it('exposes field errors', async () => {
    fetchMock.mockResolvedValueOnce(
      json(400, { success: false, message: 'NOT OK', error: { code: ['This short code is already taken.'] } }),
    )

    const error = await api('/shortener/urls/', { method: 'POST', body: {} }).catch((caught: ApiError) => caught)

    expect(error).toBeInstanceOf(ApiError)
    if (!(error instanceof ApiError)) return
    expect(error.field('code')).toBe('This short code is already taken.')
    expect(error.message).toBe('This short code is already taken.')
  })
})
