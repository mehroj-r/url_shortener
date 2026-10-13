import type { TagColor } from '../api/types'

/** CSS custom property for a line (collection) or tag colour. */
export function lineColor(color: TagColor | undefined | null): string {
  return `var(--line-${color ?? 'slate'})`
}
