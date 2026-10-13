import { describe, expect, it } from 'vitest'

import { displayUrl, formatCount, formatDay, hostOf, percentChange, plural, timeAgo } from './format'

describe('format', () => {
  it('shows exact counts below ten thousand and compact ones above', () => {
    expect(formatCount(1284)).toBe('1,284')
    expect(formatCount(12_940)).toBe('12.9K')
  })

  it('computes change against the previous period', () => {
    expect(percentChange(150, 100)).toBe(50)
    expect(percentChange(50, 100)).toBe(-50)
    expect(percentChange(5, 0)).toBeNull()
  })

  it('formats calendar dates without shifting them across time zones', () => {
    expect(formatDay('2026-10-01')).toBe('Oct 1')
  })

  it('shortens URLs for display', () => {
    expect(displayUrl('https://www.example.com/a/b?x=1')).toBe('example.com/a/b?x=1')
    expect(displayUrl('https://example.com/')).toBe('example.com')
    expect(hostOf('https://www.t.me/channel')).toBe('t.me')
    expect(displayUrl('not a url')).toBe('not a url')
  })

  it('describes relative times', () => {
    const now = Date.parse('2026-10-13T12:00:00Z')
    expect(timeAgo('2026-10-13T11:59:50Z', now)).toBe('just now')
    expect(timeAgo('2026-10-13T11:00:00Z', now)).toBe('1 hour ago')
    expect(timeAgo('2026-10-11T12:00:00Z', now)).toBe('2 days ago')
  })

  it('pluralises', () => {
    expect(plural(1, 'link')).toBe('1 link')
    expect(plural(1200, 'click')).toBe('1,200 clicks')
  })
})
