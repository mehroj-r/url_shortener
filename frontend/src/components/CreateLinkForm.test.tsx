import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ToastProvider } from '../lib/toast'
import { CreateLinkForm, nameFromUrl, urlProblem } from './CreateLinkForm'

function json(status: number, body: unknown) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
}

const page = { count: 0, next: null, previous: null, results: [] }

describe('CreateLinkForm', () => {
  const fetchMock = vi.fn<typeof fetch>()

  beforeEach(() => vi.stubGlobal('fetch', fetchMock))
  afterEach(() => {
    fetchMock.mockReset()
    vi.unstubAllGlobals()
  })

  function renderForm() {
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    return render(
      <QueryClientProvider client={client}>
        <ToastProvider>
          <MemoryRouter>
            <CreateLinkForm variant="ticket" />
          </MemoryRouter>
        </ToastProvider>
      </QueryClientProvider>,
    )
  }

  it('derives a readable name', () => {
    expect(nameFromUrl('https://www.docs.google.com/document/d/123')).toBe('docs.google.com/document')
    expect(nameFromUrl('https://example.com')).toBe('example.com')
  })

  it('explains what is wrong with the URL before submitting', () => {
    expect(urlProblem('')).toMatch(/Paste the long URL/)
    expect(urlProblem('not a url')).toMatch(/doesn’t look like a web address/)
    expect(urlProblem('localhost')).toMatch(/doesn’t look like a web address/)
    expect(urlProblem('example.com/page')).toBeNull()
  })

  it('keeps Shorten enabled and says what is missing', async () => {
    fetchMock.mockResolvedValue(json(200, { success: true, data: page }))
    renderForm()

    const shorten = screen.getByRole('button', { name: 'Shorten' })
    expect(shorten).toBeEnabled()
    await userEvent.click(shorten)

    expect(await screen.findByText('Paste the long URL you want to shorten.')).toBeInTheDocument()
    expect(fetchMock.mock.calls.some(([, init]) => init?.method === 'POST')).toBe(false)
  })

  it('creates a link with a derived name and scheme, then shows the code', async () => {
    fetchMock.mockImplementation(async (input, init) => {
      const url = String(input)
      if (init?.method === 'POST') {
        return json(201, {
          success: true,
          data: { id: 7, name: 'example.com/page', url: 'https://example.com/page', short_urls: [{ short_url: 'q3Kx9aB' }] },
        })
      }
      return json(200, { success: true, data: url.includes('tags') || url.includes('collections') ? page : page })
    })
    renderForm()

    await userEvent.type(screen.getByLabelText('Long URL'), 'example.com/page')
    await userEvent.click(screen.getByRole('button', { name: 'Shorten' }))

    expect(await screen.findByText('q3Kx9aB')).toBeInTheDocument()
    const post = fetchMock.mock.calls.find(([, init]) => init?.method === 'POST')!
    expect(JSON.parse(String(post[1]!.body))).toMatchObject({
      url: 'https://example.com/page',
      name: 'example.com/page',
      collection: null,
      tags: [],
      expires_at: null,
    })
  })

  it('shows a taken code under the code field', async () => {
    fetchMock.mockImplementation(async (_input, init) =>
      init?.method === 'POST'
        ? json(400, { success: false, error: { code: ['This short code is already taken.'] } })
        : json(200, { success: true, data: page }),
    )
    renderForm()

    await userEvent.type(screen.getByLabelText('Long URL'), 'https://example.com')
    await userEvent.type(screen.getByLabelText('Short code'), 'taken')
    await userEvent.click(screen.getByRole('button', { name: 'Shorten' }))

    expect(await screen.findByText('This short code is already taken.')).toBeInTheDocument()
    expect(screen.getByLabelText('Short code')).toHaveAttribute('aria-invalid', 'true')
  })
})
