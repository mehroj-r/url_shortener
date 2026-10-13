import { Pencil, Trash2 } from 'lucide-react'
import { useState, type CSSProperties, type FormEvent } from 'react'
import { Link as RouterLink } from 'react-router'

import { ApiError } from '../api/client'
import { useCollections, useDeleteCollection, useSaveCollection } from '../api/queries'
import { LINE_COLORS, type Collection, type LineColor } from '../api/types'
import { ColorPicker } from '../components/ColorPicker'
import { Button, Dialog, EmptyState, Field, IconButton, Panel, Skeleton, TextInput, ui } from '../components/ui'
import { lineColor } from '../lib/colors'
import { formatNumber, plural } from '../lib/format'
import { useToast } from '../lib/toast'
import styles from './ManagePage.module.css'

function nextColor(collections: Collection[]): LineColor {
  return LINE_COLORS[collections.length % LINE_COLORS.length]
}

function CreateCollection({ collections }: { collections: Collection[] }) {
  const save = useSaveCollection()
  const [name, setName] = useState('')
  const [color, setColor] = useState<LineColor | null>(null)
  const [nameError, setNameError] = useState<string | null>(null)
  const error = save.error instanceof ApiError ? save.error : null

  async function submit(event: FormEvent) {
    event.preventDefault()
    if (!name.trim()) {
      setNameError('Give the collection a name.')
      return
    }
    const ok = await save.mutateAsync({ name: name.trim(), color: color ?? nextColor(collections) }).then(
      () => true,
      () => false,
    )
    if (ok) {
      setName('')
      setColor(null)
    }
  }

  return (
    <Panel title="New collection">
      <form className={styles.createRow} onSubmit={submit} noValidate>
        <Field label="Name" error={nameError ?? error?.field('name')}>
          {(props) => (
            <TextInput
              {...props}
              maxLength={255}
              placeholder="e.g. Job hunt"
              value={name}
              onChange={(e) => {
                setName(e.target.value)
                setNameError(null)
              }}
            />
          )}
        </Field>
        <div className={styles.colorField}>
          <span className={ui.label}>Line colour</span>
          <ColorPicker label="Line colour" colors={LINE_COLORS} value={color ?? nextColor(collections)} onChange={setColor} />
        </div>
        <Button type="submit" variant="primary" loading={save.isPending}>
          Create
        </Button>
      </form>
    </Panel>
  )
}

function CollectionItem({ collection, onDelete }: { collection: Collection; onDelete: () => void }) {
  const save = useSaveCollection()
  const [editing, setEditing] = useState(false)
  const [name, setName] = useState(collection.name)
  const [color, setColor] = useState(collection.color)
  const error = save.error instanceof ApiError ? save.error : null

  return (
    <li className={styles.item} style={{ '--line': lineColor(collection.color) } as CSSProperties}>
      <span className={styles.lineSample} aria-hidden />
      <span className={styles.itemName}>
        <RouterLink to={`/links?collection=${collection.id}`}>{collection.name}</RouterLink>
        <span>{plural(collection.link_count, 'link')}</span>
      </span>
      <span className={`${styles.itemStats} num`}>{formatNumber(collection.clicks)} clicks</span>
      <span className={styles.itemActions}>
        <IconButton label={`Edit ${collection.name}`} onClick={() => setEditing((open) => !open)} aria-expanded={editing}>
          <Pencil size={15} aria-hidden />
        </IconButton>
        <IconButton label={`Delete ${collection.name}`} onClick={onDelete}>
          <Trash2 size={15} aria-hidden />
        </IconButton>
      </span>
      {editing && (
        <form
          className={styles.editRow}
          onSubmit={async (event) => {
            event.preventDefault()
            const ok = await save.mutateAsync({ id: collection.id, name: name.trim(), color }).then(() => true, () => false)
            if (ok) setEditing(false)
          }}
        >
          <Field label="Name" error={error?.field('name')}>
            {(props) => <TextInput {...props} required value={name} onChange={(e) => setName(e.target.value)} />}
          </Field>
          <ColorPicker label="Line colour" colors={LINE_COLORS} value={color} onChange={setColor} />
          <Button onClick={() => setEditing(false)}>Cancel</Button>
          <Button type="submit" variant="primary" loading={save.isPending}>
            Save
          </Button>
        </form>
      )}
    </li>
  )
}

export default function CollectionsPage() {
  const collections = useCollections()
  const remove = useDeleteCollection()
  const toast = useToast()
  const [deleting, setDeleting] = useState<Collection | null>(null)
  const [deleteLinks, setDeleteLinks] = useState(false)

  return (
    <div className={styles.page}>
      <div className={styles.heading}>
        <h1>Collections</h1>
        <p>Group links by project, campaign or topic. Each collection is a line on the dashboard, in its own colour.</p>
      </div>

      <CreateCollection collections={collections.data ?? []} />

      <Panel title="Your collections">
        {collections.isPending ? (
          <Skeleton height={80} />
        ) : collections.data?.length ? (
          <ul className={styles.list}>
            {collections.data.map((collection) => (
              <CollectionItem
                key={collection.id}
                collection={collection}
                onDelete={() => {
                  setDeleteLinks(false)
                  setDeleting(collection)
                }}
              />
            ))}
          </ul>
        ) : (
          <EmptyState title="No collections yet">
            Create one above, then add links to it from the link form or with bulk actions on the Links page.
          </EmptyState>
        )}
      </Panel>

      <Dialog
        open={deleting !== null}
        onClose={() => setDeleting(null)}
        title={`Delete ${deleting?.name}?`}
        footer={
          <>
            <Button onClick={() => setDeleting(null)}>Cancel</Button>
            <Button
              variant="danger"
              loading={remove.isPending}
              onClick={async () => {
                if (!deleting) return
                await remove
                  .mutateAsync({ id: deleting.id, deleteLinks })
                  .then(() => toast(`Deleted ${deleting.name}`), () => toast('Could not delete the collection.', 'error'))
                setDeleting(null)
              }}
            >
              Delete collection
            </Button>
          </>
        }
      >
        <fieldset className={styles.choice} style={{ border: 0, padding: 0, margin: 0 }}>
          <legend className="visually-hidden">What happens to its links</legend>
          <label>
            <input type="radio" name="links" checked={!deleteLinks} onChange={() => setDeleteLinks(false)} />
            <span>
              Keep its {plural(deleting?.link_count ?? 0, 'link')}
              <small>They stay active and move to No collection.</small>
            </span>
          </label>
          <label>
            <input type="radio" name="links" checked={deleteLinks} onChange={() => setDeleteLinks(true)} />
            <span>
              Delete the links too
              <small>Their codes stop redirecting and stay reserved.</small>
            </span>
          </label>
        </fieldset>
      </Dialog>
    </div>
  )
}
