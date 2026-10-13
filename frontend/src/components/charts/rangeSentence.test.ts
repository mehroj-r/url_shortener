import { describe, expect, it } from 'vitest'

import { rangeSentence } from './ClicksOverview'

const sentence = (clicks: number, previous: number) =>
  rangeSentence({
    totals: { clicks, previous_clicks: previous, visitors: 40, bots: 0, links: 3 },
    range: { days: 30, start: '2026-09-14', end: '2026-10-13', timezone: 'Asia/Tashkent' },
  })

describe('rangeSentence', () => {
  it('says how the range compares with the one before', () => {
    expect(sentence(654, 280)).toBe('654 clicks from 40 visitors in the last 30 days, 2.3× the previous 30.')
    expect(sentence(200, 100)).toBe('200 clicks from 40 visitors in the last 30 days, 2× the previous 30.')
    expect(sentence(50, 812)).toBe('50 clicks from 40 visitors in the last 30 days, down from 812 the previous 30.')
    expect(sentence(100, 98)).toBe('100 clicks from 40 visitors in the last 30 days, about the same as the previous 30.')
    expect(sentence(5, 0)).toBe('5 clicks from 40 visitors in the last 30 days.')
  })
})
