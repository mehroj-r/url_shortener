import { render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { describe, expect, it } from 'vitest'

import type { Collection, Link } from '../../api/types'
import { HighlightProvider } from './highlight'
import { LineMap } from './LineMap'

const collection = (id: number, name: string, color: Collection['color']): Collection => ({
  id, name, color, link_count: 0, clicks: 0, created_at: '2026-10-01T00:00:00Z',
})

const link = (id: number, code: string, collectionId: number | null): Link => ({
  id,
  name: `Link ${code}`,
  url: `https://example.com/${code}`,
  collection: collectionId,
  tags: [],
  short_urls: [{ id, short_url: code, is_active: true, expires_at: null, status: 'active', clicks: 0, created_at: '2026-10-01T00:00:00Z' }],
  clicks: 0,
  last_clicked_at: null,
  status: 'active',
  created_at: `2026-10-0${id}T00:00:00Z`,
})

function renderMap(links: Link[], clicks: [number, number][]) {
  return render(
    <MemoryRouter>
      <HighlightProvider>
        <LineMap
          collections={[collection(1, 'Portfolio', 'red'), collection(2, 'Job hunt', 'green')]}
          links={links}
          clicksByLink={new Map(clicks)}
          days={30}
        />
      </HighlightProvider>
    </MemoryRouter>,
  )
}

describe('LineMap', () => {
  it('draws one line per collection, busiest first, with stations ordered by clicks', () => {
    renderMap([link(1, 'cv', 1), link(2, 'gh', 1), link(3, 'apply', 2), link(4, 'loose', null)], [[1, 5], [2, 40], [3, 3]])

    const lines = screen.getAllByRole('list', { name: /links$/ })
    expect(lines.map((line) => line.getAttribute('aria-label'))).toEqual([
      'Portfolio links',
      'Job hunt links',
      'No collection links',
    ])
    const stations = within(lines[0]).getAllByRole('link')
    expect(stations.map((station) => station.textContent?.split('Link')[0])).toEqual(['gh', 'cv'])
    expect(stations[0]).toHaveAccessibleName('Link gh, gh: 40 clicks in 30 days')
  })

  it('folds stations that do not fit into a terminus', () => {
    const many = Array.from({ length: 12 }, (_, i) => link(i + 1, `c${i + 1}`, 1))
    renderMap(many, [])

    // 800px of track at 112px per station: six stations and the "+6" terminus
    expect(screen.getByRole('link', { name: '6 more links in Portfolio' })).toHaveTextContent('+6')
  })
})
