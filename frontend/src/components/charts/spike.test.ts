import { describe, expect, it } from 'vitest'

import { findSpikeOnset } from './DailyBars'

const days = (counts: number[]) => counts.map((clicks, i) => ({ date: `2026-10-${String(i + 1).padStart(2, '0')}`, clicks }))

describe('findSpikeOnset', () => {
  it('marks the first day of the latest busy run', () => {
    expect(findSpikeOnset(days([3, 4, 2, 3, 40, 52, 38, 4]))).toBe(4)
  })

  it('ignores quiet series', () => {
    expect(findSpikeOnset(days([1, 2, 1, 3, 2]))).toBeNull()
    expect(findSpikeOnset(days([0, 0, 9]))).toBeNull()
  })
})
