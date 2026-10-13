import { createContext, use, useMemo, useState, type ReactNode } from 'react'

interface Highlight {
  /** The link pointed at anywhere on the page (a station, a row, a click). */
  linkId: number | null
  setLinkId: (id: number | null) => void
  /** The link just created, which arrives on its line once. */
  arrivingId: number | null
  setArrivingId: (id: number | null) => void
}

const HighlightContext = createContext<Highlight>({
  linkId: null,
  setLinkId: () => {},
  arrivingId: null,
  setArrivingId: () => {},
})

export function HighlightProvider({ children }: { children: ReactNode }) {
  const [linkId, setLinkId] = useState<number | null>(null)
  const [arrivingId, setArrivingId] = useState<number | null>(null)
  const value = useMemo(() => ({ linkId, setLinkId, arrivingId, setArrivingId }), [linkId, arrivingId])
  return <HighlightContext value={value}>{children}</HighlightContext>
}

export function useHighlight() {
  return use(HighlightContext)
}

/** Props that make an element point at a link while hovered or focused. */
export function useHighlightTarget(id: number) {
  const { linkId, setLinkId } = useHighlight()
  return {
    active: linkId === id,
    props: {
      onPointerEnter: () => setLinkId(id),
      onPointerLeave: () => setLinkId(null),
      onFocus: () => setLinkId(id),
      onBlur: () => setLinkId(null),
    },
  }
}
