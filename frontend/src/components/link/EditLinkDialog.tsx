import { useState, type FormEvent } from 'react'

import { ApiError } from '../../api/client'
import { useCollections, useTags, useUpdateLink } from '../../api/queries'
import type { Link } from '../../api/types'
import { TagPicker } from '../TagPicker'
import { Button, Dialog, Field, FormError, Select, TextInput, ui } from '../ui'

export function EditLinkDialog({ link, open, onClose }: { link: Link; open: boolean; onClose: () => void }) {
  const update = useUpdateLink(link.id)
  const collections = useCollections()
  const tags = useTags()
  const [name, setName] = useState(link.name)
  const [url, setUrl] = useState(link.url)
  const [collection, setCollection] = useState<number | null>(link.collection)
  const [tagIds, setTagIds] = useState<number[]>(link.tags)
  const error = update.error instanceof ApiError ? update.error : null

  async function submit(event: FormEvent) {
    event.preventDefault()
    const ok = await update
      .mutateAsync({ name: name.trim(), url: url.trim(), collection, tags: tagIds })
      .then(() => true, () => false)
    if (ok) onClose()
  }

  return (
    <Dialog open={open} onClose={onClose} title="Edit link" width={560}>
      <form className={ui.formGrid} onSubmit={submit}>
        <Field label="Name" error={error?.field('name')}>
          {(props) => <TextInput {...props} required maxLength={255} value={name} onChange={(e) => setName(e.target.value)} />}
        </Field>
        <Field
          label="Destination"
          hint="Every code of this link redirects here."
          error={error?.field('url')}
        >
          {(props) => <TextInput {...props} type="url" required value={url} onChange={(e) => setUrl(e.target.value)} />}
        </Field>
        <Field label="Collection" error={error?.field('collection')}>
          {(props) => (
            <Select
              {...props}
              value={collection ?? ''}
              onChange={(e) => setCollection(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">No collection</option>
              {collections.data?.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </Select>
          )}
        </Field>
        <div className={ui.field}>
          <span className={ui.label}>Tags</span>
          <TagPicker tags={tags.data ?? []} selected={tagIds} onChange={setTagIds} />
        </div>
        <FormError message={error && !['name', 'url', 'collection'].some((f) => error.field(f)) ? error.message : undefined} />
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="primary" loading={update.isPending}>
            Save changes
          </Button>
        </div>
      </form>
    </Dialog>
  )
}
