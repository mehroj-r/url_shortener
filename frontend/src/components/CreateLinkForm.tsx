import { ArrowRight, Check, ChevronDown } from 'lucide-react'
import { useState, type CSSProperties, type FormEvent } from 'react'
import { Link as RouterLink } from 'react-router'

import { ApiError } from '../api/client'
import { useCollections, useCreateLink, useTags } from '../api/queries'
import type { Link } from '../api/types'
import { SHORT_HOST } from '../lib/format'
import styles from './CreateLinkForm.module.css'
import { Button, Code, CopyCodeButton, Dialog, Field, FormError, Select, TextInput } from './ui'
import { TagPicker } from './TagPicker'

/** A readable default name from the destination: "docs.google.com/document". */
export function nameFromUrl(url: string): string {
  try {
    const parsed = new URL(url)
    const firstSegment = parsed.pathname.split('/').find(Boolean)
    return `${parsed.hostname.replace(/^www\./, '')}${firstSegment ? `/${firstSegment}` : ''}`.slice(0, 255)
  } catch {
    return url.slice(0, 255)
  }
}

function withScheme(url: string): string {
  const trimmed = url.trim()
  return /^https?:\/\//i.test(trimmed) || !trimmed ? trimmed : `https://${trimmed}`
}

/** The problem with what was typed, in words, or null when it is a usable web address. */
export function urlProblem(url: string): string | null {
  if (!url.trim()) return 'Paste the long URL you want to shorten.'
  try {
    const parsed = new URL(withScheme(url))
    if (!parsed.hostname.includes('.')) throw new Error('no domain')
    return null
  } catch {
    return 'That doesn’t look like a web address. Paste a link like https://example.com/page.'
  }
}

interface Props {
  variant: 'ticket' | 'full'
  defaultCollection?: number | null
  onCreated?: (link: Link) => void
}

export function CreateLinkForm({ variant, defaultCollection = null, onCreated }: Props) {
  const create = useCreateLink()
  const collections = useCollections()
  const tags = useTags()
  const [url, setUrl] = useState('')
  const [code, setCode] = useState('')
  const [name, setName] = useState('')
  const [collection, setCollection] = useState<number | null>(defaultCollection)
  const [tagIds, setTagIds] = useState<number[]>([])
  const [expiresAt, setExpiresAt] = useState('')
  const [moreOpen, setMoreOpen] = useState(variant === 'full')
  const [created, setCreated] = useState<Link | null>(null)
  const [urlError, setUrlError] = useState<string | null>(null)

  const error = create.error instanceof ApiError ? create.error : null
  const fieldError = (field: string) => error?.field(field)
  const generalError =
    error && !['url', 'code', 'name', 'collection', 'tags', 'expires_at'].some((field) => error.field(field))
      ? error.message
      : create.error && !error
        ? 'Could not reach the server. Check your connection.'
        : undefined

  async function submit(event: FormEvent) {
    event.preventDefault()
    const problem = urlProblem(url)
    setUrlError(problem)
    if (problem) return
    const destination = withScheme(url)
    const link = await create
      .mutateAsync({
        url: destination,
        name: name.trim() || nameFromUrl(destination),
        code: code.trim() || undefined,
        collection,
        tags: tagIds,
        expires_at: expiresAt ? new Date(expiresAt).toISOString() : null,
      })
      .catch(() => null)
    if (!link) return
    setCreated(link)
    setUrl('')
    setCode('')
    setName('')
    setExpiresAt('')
    onCreated?.(link)
  }

  const newCode = created?.short_urls[0]?.short_url

  return (
    <form className={styles.form} data-variant={variant} onSubmit={submit} noValidate>
      <div className={styles.primaryRow}>
        <Field label="Long URL" error={urlError ?? fieldError('url')} className={styles.urlField}>
          {(props) => (
            <TextInput
              {...props}
              type="url"
              inputMode="url"
              autoComplete="off"
              required
              placeholder="Paste a long URL"
              value={url}
              onChange={(event) => {
                setUrl(event.target.value)
                setUrlError(null)
              }}
              data-ticket-url={variant === 'ticket' || undefined}
              data-autofocus={variant === 'full' || undefined}
            />
          )}
        </Field>
        <Field label="Short code" error={fieldError('code')} className={styles.codeField}>
          {(props) => (
            <div className={styles.codeInput} style={{ '--prefix': `${SHORT_HOST.length + 1}ch` } as CSSProperties}>
              <span aria-hidden>{SHORT_HOST}/</span>
              <TextInput
                {...props}
                autoComplete="off"
                spellCheck={false}
                placeholder="auto"
                maxLength={64}
                value={code}
                onChange={(event) => setCode(event.target.value)}
              />
            </div>
          )}
        </Field>
        <div className={styles.submitCell}>
          {/* Same height as the field labels, so the button lines up with the inputs */}
          <span className={styles.labelSpacer} aria-hidden>
            &nbsp;
          </span>
          <Button
            type="submit"
            variant="primary"
            size={variant === 'ticket' ? 'lg' : 'md'}
            className={styles.submit}
            loading={create.isPending}
          >
            Shorten
          </Button>
        </div>
      </div>

      {variant === 'ticket' && (
        <button
          type="button"
          className={styles.moreToggle}
          aria-expanded={moreOpen}
          onClick={() => setMoreOpen((open) => !open)}
        >
          <ChevronDown size={14} aria-hidden data-open={moreOpen} />
          Name, collection, tags and expiry
        </button>
      )}

      {moreOpen && (
        <div className={styles.more}>
          <Field label="Name" hint="Defaults to the site and first path segment." error={fieldError('name')}>
            {(props) => (
              <TextInput
                {...props}
                maxLength={255}
                placeholder={url ? nameFromUrl(withScheme(url)) : 'e.g. Portfolio'}
                value={name}
                onChange={(event) => setName(event.target.value)}
              />
            )}
          </Field>
          <Field label="Collection" error={fieldError('collection')}>
            {(props) => (
              <Select
                {...props}
                value={collection ?? ''}
                onChange={(event) => setCollection(event.target.value ? Number(event.target.value) : null)}
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
          <Field label="Expires" hint="Optional. After this, the link stops redirecting." error={fieldError('expires_at')}>
            {(props) => (
              <TextInput
                {...props}
                type="datetime-local"
                value={expiresAt}
                onChange={(event) => setExpiresAt(event.target.value)}
              />
            )}
          </Field>
          <div className={styles.tagsField}>
            <span className={styles.tagsLabel}>Tags</span>
            <TagPicker tags={tags.data ?? []} selected={tagIds} onChange={setTagIds} />
          </div>
        </div>
      )}

      <FormError message={generalError} />

      {created && newCode && (
        <div className={styles.issued} role="status">
          <Check size={16} aria-hidden className={styles.issuedIcon} />
          <Code code={newCode} host />
          <CopyCodeButton code={newCode} />
          <span className={styles.issuedName}>{created.name}</span>
          <RouterLink to={`/links/${created.id}`} className={styles.issuedLink}>
            Open link <ArrowRight size={14} aria-hidden />
          </RouterLink>
        </div>
      )}
    </form>
  )
}

export function CreateLinkDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <Dialog open={open} onClose={onClose} title="New short link" width={640}>
      <CreateLinkForm variant="full" />
    </Dialog>
  )
}
