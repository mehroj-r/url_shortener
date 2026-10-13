import { useSyncExternalStore } from 'react'

export type ThemePreference = 'system' | 'light' | 'dark'

export const THEME_OPTIONS: { value: ThemePreference; label: string }[] = [
  { value: 'system', label: 'System' },
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
]

// Keep in step with public/theme.js, which applies the theme before the first paint
const KEY = 'spur.theme'
const BAR_COLOR = { light: '#ffffff', dark: '#16181c' }

const media = typeof window.matchMedia === 'function' ? window.matchMedia('(prefers-color-scheme: dark)') : null
const listeners = new Set<() => void>()

function read(): ThemePreference {
  try {
    const stored = localStorage.getItem(KEY)
    return stored === 'light' || stored === 'dark' ? stored : 'system'
  } catch {
    return 'system'
  }
}

let preference = read()

function apply() {
  const theme = preference === 'system' ? (media?.matches ? 'dark' : 'light') : preference
  document.documentElement.dataset.theme = theme
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', BAR_COLOR[theme])
}

function notify() {
  for (const listener of listeners) listener()
}

apply()
media?.addEventListener('change', () => preference === 'system' && apply())
// Another tab changed the preference
window.addEventListener('storage', (event) => {
  if (event.key !== KEY) return
  preference = read()
  apply()
  notify()
})

export function setThemePreference(next: ThemePreference) {
  preference = next
  try {
    if (next === 'system') localStorage.removeItem(KEY)
    else localStorage.setItem(KEY, next)
  } catch {
    // Storage blocked: the choice still applies to this page
  }
  apply()
  notify()
}

export function useThemePreference(): ThemePreference {
  return useSyncExternalStore(
    (listener) => {
      listeners.add(listener)
      return () => listeners.delete(listener)
    },
    () => preference,
  )
}
