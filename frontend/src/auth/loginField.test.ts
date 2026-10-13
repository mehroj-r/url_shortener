import { describe, expect, it } from 'vitest'

import { loginField } from './AuthProvider'

describe('loginField', () => {
  it('tells email, phone and username apart', () => {
    expect(loginField('me@example.com')).toBe('email')
    expect(loginField('+998 90 123 45 67')).toBe('phone')
    expect(loginField('mekhroj')).toBe('username')
  })
})
