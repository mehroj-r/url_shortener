import { Check } from 'lucide-react'
import { useId, type CSSProperties } from 'react'

import type { TagColor } from '../api/types'
import { lineColor } from '../lib/colors'
import styles from './ColorPicker.module.css'

const NAMES: Record<TagColor, string> = {
  red: 'Red',
  blue: 'Blue',
  green: 'Green',
  violet: 'Violet',
  amber: 'Amber',
  teal: 'Teal',
  slate: 'Slate',
}

/** Native radios drawn as swatches; each is labelled so colour is never the only cue. */
export function ColorPicker<T extends TagColor>({
  colors,
  value,
  onChange,
  label,
}: {
  colors: readonly T[]
  value: T
  onChange: (color: T) => void
  label: string
}) {
  const name = useId()
  return (
    <fieldset className={styles.picker}>
      <legend className="visually-hidden">{label}</legend>
      {colors.map((color) => (
        <label key={color} className={styles.swatch} style={{ '--swatch': lineColor(color) } as CSSProperties} title={NAMES[color]}>
          <input
            type="radio"
            name={name}
            className="visually-hidden"
            checked={value === color}
            onChange={() => onChange(color)}
          />
          <span className="visually-hidden">{NAMES[color]}</span>
          {value === color && <Check size={14} aria-hidden />}
        </label>
      ))}
    </fieldset>
  )
}
