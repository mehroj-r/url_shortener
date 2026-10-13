import { LogOut, Menu, Plus, Search, Settings } from 'lucide-react'
import { createContext, use, useCallback, useEffect, useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router'

import { useAuth } from '../auth/AuthProvider'
import styles from './AppShell.module.css'
import { CreateLinkDialog } from './CreateLinkForm'
import { Button, IconButton } from './ui'

const NAV = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/links', label: 'Links' },
  { to: '/collections', label: 'Collections' },
  { to: '/tags', label: 'Tags' },
  { to: '/invites', label: 'Invites' },
]

const OpenCreateContext = createContext<() => void>(() => {})

/** Opens the "New short link" dialog from anywhere inside the app shell. */
export function useOpenCreate() {
  return use(OpenCreateContext)
}

function isTyping(target: EventTarget | null) {
  return target instanceof HTMLElement && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))
}

export function AppShell() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [creating, setCreating] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const [query, setQuery] = useState('')

  // Where the page already has a ticket window, go there instead of opening a dialog over it
  const openCreate = useCallback(() => {
    const ticket = document.querySelector<HTMLInputElement>('[data-ticket-url]')
    if (ticket) {
      ticket.scrollIntoView({ block: 'center' })
      ticket.focus()
    } else {
      setCreating(true)
    }
  }, [])

  // "N" opens the create dialog from anywhere, "/" jumps to search
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.metaKey || event.ctrlKey || event.altKey || isTyping(event.target)) return
      if (event.key === 'n') {
        event.preventDefault()
        openCreate()
      } else if (event.key === '/') {
        const search = document.getElementById('global-search')
        if (search && search.offsetParent !== null) {
          event.preventDefault()
          search.focus()
        }
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [openCreate])

  const initials = user ? `${user.first_name[0] ?? ''}${user.last_name[0] ?? ''}`.toUpperCase() : ''

  return (
    <>
      <header className={styles.topBar}>
        <div className={styles.barInner}>
          <NavLink to="/" className={styles.wordmark} aria-label="Bekat, dashboard">
            <span className={styles.mark} aria-hidden />
            Bekat
          </NavLink>
          <nav className={styles.nav} aria-label="Main">
            {NAV.map((item) => (
              <NavLink key={item.to} to={item.to} end={item.end} className={styles.navLink}>
                {item.label}
              </NavLink>
            ))}
          </nav>
          <form
            className={styles.search}
            role="search"
            onSubmit={(event) => {
              event.preventDefault()
              navigate(`/links?search=${encodeURIComponent(query.trim())}`)
            }}
          >
            <Search size={15} aria-hidden />
            <input
              id="global-search"
              type="search"
              placeholder="Search links"
              aria-label="Search links"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </form>
          <Button size="sm" className={styles.shorten} onClick={openCreate} aria-keyshortcuts="n">
            <Plus size={15} aria-hidden />
            <span className={styles.shortenLabel}>Shorten</span>
          </Button>
          <IconButton
            label={menuOpen ? 'Close menu' : 'Open menu'}
            className={styles.menuButton}
            aria-expanded={menuOpen}
            aria-controls="mobile-nav"
            onClick={() => setMenuOpen((open) => !open)}
          >
            <Menu size={18} aria-hidden />
          </IconButton>
          <button type="button" className={styles.userButton} popoverTarget="user-menu" aria-label="Account menu">
            {initials || '·'}
          </button>
          <div id="user-menu" popover="auto" className={styles.menu}>
            {user && (
              <div className={styles.menuHead}>
                <strong>
                  {user.first_name} {user.last_name}
                </strong>
                <span>{user.email}</span>
              </div>
            )}
            <NavLink
              to="/settings"
              className={styles.menuItem}
              onClick={() => document.getElementById('user-menu')?.hidePopover()}
            >
              <Settings size={15} aria-hidden /> Settings
            </NavLink>
            <button type="button" className={styles.menuItem} onClick={() => logout()}>
              <LogOut size={15} aria-hidden /> Sign out
            </button>
          </div>
        </div>
        <nav id="mobile-nav" className={styles.mobileNav} data-open={menuOpen} aria-label="Main">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={styles.navLink}
              onClick={() => setMenuOpen(false)}
            >
              {item.label}
            </NavLink>
          ))}
          <NavLink to="/settings" className={styles.navLink} onClick={() => setMenuOpen(false)}>
            Settings
          </NavLink>
        </nav>
      </header>
      <div className={styles.ceramic} aria-hidden />
      <main className={styles.main}>
        <OpenCreateContext value={openCreate}>
          <Outlet />
        </OpenCreateContext>
      </main>
      <CreateLinkDialog open={creating} onClose={() => setCreating(false)} />
    </>
  )
}
