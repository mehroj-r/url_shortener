import { Check } from 'lucide-react'
import { Link as RouterLink } from 'react-router'

import type { Tag } from '../api/types'
import styles from './TagPicker.module.css'
import { LineDot } from './ui'

/** Every tag as a toggle; fine for the tens of tags a person keeps. */
export function TagPicker({
  tags,
  selected,
  onChange,
}: {
  tags: Tag[]
  selected: number[]
  onChange: (ids: number[]) => void
}) {
  if (tags.length === 0) {
    return (
      <p className={styles.none}>
        No tags yet. <RouterLink to="/tags">Create tags</RouterLink> to label links across collections.
      </p>
    )
  }
  return (
    <fieldset className={styles.picker}>
      <legend className="visually-hidden">Tags</legend>
      {tags.map((tag) => {
        const on = selected.includes(tag.id)
        return (
          <button
            key={tag.id}
            type="button"
            className={styles.toggle}
            aria-pressed={on}
            onClick={() => onChange(on ? selected.filter((id) => id !== tag.id) : [...selected, tag.id])}
          >
            {on ? <Check size={12} aria-hidden /> : <LineDot color={tag.color} />}
            {tag.name}
          </button>
        )
      })}
    </fieldset>
  )
}
