import { Pencil, Trash2 } from 'lucide-react'
import { useState, type FormEvent } from 'react'
import { Link as RouterLink } from 'react-router'

import { ApiError } from '../api/client'
import { useDeleteTag, useSaveTag, useTags } from '../api/queries'
import { TAG_COLORS, type Tag, type TagColor } from '../api/types'
import { ColorPicker } from '../components/ColorPicker'
import { Button, Dialog, EmptyState, Field, IconButton, LineDot, Panel, Skeleton, TextInput, ui } from '../components/ui'
import { plural } from '../lib/format'
import { useToast } from '../lib/toast'
import styles from './ManagePage.module.css'

function TagItem({ tag, onDelete }: { tag: Tag; onDelete: () => void }) {
  const save = useSaveTag()
  const [editing, setEditing] = useState(false)
  const [name, setName] = useState(tag.name)
  const [color, setColor] = useState(tag.color)
  const error = save.error instanceof ApiError ? save.error : null

  return (
    <li className={styles.item}>
      <span className={styles.tagSwatch}>
        <LineDot color={tag.color} />
      </span>
      <span className={styles.itemName}>
        <RouterLink to={`/links?tag=${tag.id}`}>{tag.name}</RouterLink>
        <span>{plural(tag.link_count, 'link')}</span>
      </span>
      <span />
      <span className={styles.itemActions}>
        <IconButton label={`Edit ${tag.name}`} onClick={() => setEditing((open) => !open)} aria-expanded={editing}>
          <Pencil size={15} aria-hidden />
        </IconButton>
        <IconButton label={`Delete ${tag.name}`} onClick={onDelete}>
          <Trash2 size={15} aria-hidden />
        </IconButton>
      </span>
      {editing && (
        <form
          className={styles.editRow}
          onSubmit={async (event) => {
            event.preventDefault()
            const ok = await save.mutateAsync({ id: tag.id, name: name.trim(), color }).then(() => true, () => false)
            if (ok) setEditing(false)
          }}
        >
          <Field label="Name" error={error?.field('name')}>
            {(props) => <TextInput {...props} required maxLength={50} value={name} onChange={(e) => setName(e.target.value)} />}
          </Field>
          <ColorPicker label="Tag colour" colors={TAG_COLORS} value={color} onChange={setColor} />
          <Button onClick={() => setEditing(false)}>Cancel</Button>
          <Button type="submit" variant="primary" loading={save.isPending}>
            Save
          </Button>
        </form>
      )}
    </li>
  )
}

export default function TagsPage() {
  const tags = useTags()
  const save = useSaveTag()
  const remove = useDeleteTag()
  const toast = useToast()
  const [name, setName] = useState('')
  const [color, setColor] = useState<TagColor>('slate')
  const [deleting, setDeleting] = useState<Tag | null>(null)
  const [nameError, setNameError] = useState<string | null>(null)
  const error = save.error instanceof ApiError ? save.error : null

  async function submit(event: FormEvent) {
    event.preventDefault()
    if (!name.trim()) {
      setNameError('Give the tag a name.')
      return
    }
    const ok = await save.mutateAsync({ name: name.trim(), color }).then(() => true, () => false)
    if (ok) setName('')
  }

  return (
    <div className={styles.page}>
      <div className={styles.heading}>
        <h1>Tags</h1>
        <p>Labels that cut across collections, like “campaign” or “print”. A link can carry any number of them.</p>
      </div>

      <Panel title="New tag">
        <form className={styles.createRow} onSubmit={submit} noValidate>
          <Field label="Name" error={nameError ?? error?.field('name')}>
            {(props) => (
              <TextInput
                {...props}
                maxLength={50}
                placeholder="e.g. Conference"
                value={name}
                onChange={(e) => {
                  setName(e.target.value)
                  setNameError(null)
                }}
              />
            )}
          </Field>
          <div className={styles.colorField}>
            <span className={ui.label}>Colour</span>
            <ColorPicker label="Tag colour" colors={TAG_COLORS} value={color} onChange={setColor} />
          </div>
          <Button type="submit" variant="primary" loading={save.isPending}>
            Create
          </Button>
        </form>
      </Panel>

      <Panel title="Your tags">
        {tags.isPending ? (
          <Skeleton height={80} />
        ) : tags.data?.length ? (
          <ul className={styles.list}>
            {tags.data.map((tag) => (
              <TagItem key={tag.id} tag={tag} onDelete={() => setDeleting(tag)} />
            ))}
          </ul>
        ) : (
          <EmptyState title="No tags yet">Create one above, then tag links when you create or edit them.</EmptyState>
        )}
      </Panel>

      <Dialog
        open={deleting !== null}
        onClose={() => setDeleting(null)}
        title={`Delete the ${deleting?.name} tag?`}
        footer={
          <>
            <Button onClick={() => setDeleting(null)}>Cancel</Button>
            <Button
              variant="danger"
              loading={remove.isPending}
              onClick={async () => {
                if (!deleting) return
                await remove.mutateAsync(deleting.id).then(
                  () => toast(`Deleted ${deleting.name}`),
                  () => toast('Could not delete the tag.', 'error'),
                )
                setDeleting(null)
              }}
            >
              Delete tag
            </Button>
          </>
        }
      >
        <p>It comes off {plural(deleting?.link_count ?? 0, 'link')}. The links themselves stay.</p>
      </Dialog>
    </div>
  )
}
