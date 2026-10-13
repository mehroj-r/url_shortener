import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { api } from './client'
import type {
  Click,
  Collection,
  Invite,
  Link,
  LinkInput,
  LineColor,
  Page,
  Profile,
  ShortCode,
  Summary,
  SummaryScope,
  Tag,
  TagColor,
} from './types'

const TIME_ZONE = Intl.DateTimeFormat().resolvedOptions().timeZone

export interface LinkFilters {
  search?: string
  collection?: number | 'none'
  tag?: number
  status?: 'active' | 'expired' | 'inactive'
  ordering?: string
  page?: number
  page_size?: number
}

// ---- Queries

export function useSummary(scope: SummaryScope) {
  return useQuery({
    queryKey: ['summary', scope],
    queryFn: ({ signal }) => api<Summary>('/analytics/summary/', { query: { ...scope, tz: TIME_ZONE }, signal }),
    placeholderData: keepPreviousData,
  })
}

export function useLinks(filters: LinkFilters) {
  return useQuery({
    queryKey: ['links', filters],
    queryFn: ({ signal }) => api<Page<Link>>('/shortener/urls/', { query: { ...filters }, signal }),
    placeholderData: keepPreviousData,
  })
}

export function useLink(id: number) {
  return useQuery({
    queryKey: ['link', id],
    queryFn: ({ signal }) => api<Link>(`/shortener/urls/${id}/`, { signal }),
  })
}

export function useCollections() {
  return useQuery({
    queryKey: ['collections'],
    queryFn: ({ signal }) => api<Page<Collection>>('/shortener/url-collections/', { query: { page_size: 100 }, signal }),
    select: (page) => page.results,
  })
}

export function useTags() {
  return useQuery({
    queryKey: ['tags'],
    queryFn: ({ signal }) => api<Page<Tag>>('/shortener/tags/', { query: { page_size: 100 }, signal }),
    select: (page) => page.results,
  })
}

export function useClicks(query: { url_id?: number; collection?: number; page?: number; page_size?: number }) {
  return useQuery({
    queryKey: ['clicks', query],
    queryFn: ({ signal }) =>
      api<Page<Click>>('/analytics/url-clicks/', { query: { is_bot: false, ...query }, signal }),
    placeholderData: keepPreviousData,
  })
}

export function useInvites() {
  return useQuery({
    queryKey: ['invites'],
    queryFn: ({ signal }) => api<Page<Invite>>('/auth/invites/', { query: { page_size: 100 }, signal }),
    select: (page) => page.results,
  })
}

// ---- Mutations

function useInvalidate() {
  const client = useQueryClient()
  return (...keys: string[]) => Promise.all(keys.map((key) => client.invalidateQueries({ queryKey: [key] })))
}

const LINK_DATA = ['links', 'link', 'summary', 'collections', 'tags', 'clicks']

export function useCreateLink() {
  const invalidate = useInvalidate()
  return useMutation({
    mutationFn: (input: LinkInput) => api<Link>('/shortener/urls/', { method: 'POST', body: input }),
    onSuccess: () => invalidate(...LINK_DATA),
  })
}

export function useUpdateLink(id: number) {
  const invalidate = useInvalidate()
  return useMutation({
    mutationFn: (input: Partial<LinkInput>) => api<Link>(`/shortener/urls/${id}/`, { method: 'PATCH', body: input }),
    onSuccess: () => invalidate(...LINK_DATA),
  })
}

export function useDeleteLink() {
  const invalidate = useInvalidate()
  return useMutation({
    mutationFn: (id: number) => api<void>(`/shortener/urls/${id}/`, { method: 'DELETE' }),
    onSuccess: () => invalidate(...LINK_DATA),
  })
}

export type BulkAction =
  | { action: 'delete' | 'activate' | 'deactivate' }
  | { action: 'move'; collection: number | null }
  | { action: 'add_tag' | 'remove_tag'; tag: number }

export function useBulkLinks() {
  const invalidate = useInvalidate()
  return useMutation({
    mutationFn: ({ ids, ...action }: BulkAction & { ids: number[] }) =>
      api<{ count: number }>('/shortener/urls/bulk/', { method: 'POST', body: { ids, ...action } }),
    onSuccess: () => invalidate(...LINK_DATA),
  })
}

export function useCreateCode(linkId: number) {
  const invalidate = useInvalidate()
  return useMutation({
    mutationFn: (input: { short_url?: string; expires_at?: string | null }) =>
      api<ShortCode>(`/shortener/urls/${linkId}/short-urls/`, { method: 'POST', body: input }),
    onSuccess: () => invalidate(...LINK_DATA),
  })
}

export function useUpdateCode() {
  const invalidate = useInvalidate()
  return useMutation({
    mutationFn: ({ id, ...input }: { id: number; is_active?: boolean; expires_at?: string | null }) =>
      api<ShortCode>(`/shortener/short-urls/${id}/`, { method: 'PATCH', body: input }),
    onSuccess: () => invalidate(...LINK_DATA),
  })
}

export function useDeleteCode() {
  const invalidate = useInvalidate()
  return useMutation({
    mutationFn: (id: number) => api<void>(`/shortener/short-urls/${id}/`, { method: 'DELETE' }),
    onSuccess: () => invalidate(...LINK_DATA),
  })
}

export function useSaveCollection() {
  const invalidate = useInvalidate()
  return useMutation({
    mutationFn: ({ id, ...input }: { id?: number; name: string; color?: LineColor }) =>
      id
        ? api<Collection>(`/shortener/url-collections/${id}/`, { method: 'PATCH', body: input })
        : api<Collection>('/shortener/url-collections/', { method: 'POST', body: input }),
    onSuccess: () => invalidate(...LINK_DATA),
  })
}

export function useDeleteCollection() {
  const invalidate = useInvalidate()
  return useMutation({
    mutationFn: ({ id, deleteLinks }: { id: number; deleteLinks: boolean }) =>
      api<void>(`/shortener/url-collections/${id}/`, {
        method: 'DELETE',
        query: { delete_links: deleteLinks ? 1 : undefined },
      }),
    onSuccess: () => invalidate(...LINK_DATA),
  })
}

export function useSaveTag() {
  const invalidate = useInvalidate()
  return useMutation({
    mutationFn: ({ id, ...input }: { id?: number; name: string; color?: TagColor }) =>
      id
        ? api<Tag>(`/shortener/tags/${id}/`, { method: 'PATCH', body: input })
        : api<Tag>('/shortener/tags/', { method: 'POST', body: input }),
    onSuccess: () => invalidate(...LINK_DATA),
  })
}

export function useDeleteTag() {
  const invalidate = useInvalidate()
  return useMutation({
    mutationFn: (id: number) => api<void>(`/shortener/tags/${id}/`, { method: 'DELETE' }),
    onSuccess: () => invalidate(...LINK_DATA),
  })
}

export function useCreateInvite() {
  const invalidate = useInvalidate()
  return useMutation({
    mutationFn: (input: { note: string; expires_in_days: number }) =>
      api<Invite>('/auth/invites/', { method: 'POST', body: input }),
    onSuccess: () => invalidate('invites'),
  })
}

export function useRevokeInvite() {
  const invalidate = useInvalidate()
  return useMutation({
    mutationFn: (id: number) => api<void>(`/auth/invites/${id}/`, { method: 'DELETE' }),
    onSuccess: () => invalidate('invites'),
  })
}

export function useUpdateProfile() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (input: Partial<Profile>) => api<Profile>('/auth/me/', { method: 'PATCH', body: input }),
    onSuccess: (profile) => client.setQueryData(['me'], profile),
  })
}

export function useChangePassword() {
  return useMutation({
    mutationFn: (input: { current_password: string; new_password: string }) =>
      api<{ detail: string }>('/auth/change-password/', { method: 'POST', body: input }),
  })
}
