export const LINE_COLORS = ['red', 'blue', 'green', 'violet', 'amber', 'teal'] as const
export type LineColor = (typeof LINE_COLORS)[number]
export type TagColor = LineColor | 'slate'
export const TAG_COLORS: TagColor[] = ['slate', ...LINE_COLORS]

export type CodeStatus = 'active' | 'inactive' | 'expired'

export interface Page<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface Profile {
  id: number
  first_name: string
  last_name: string
  username: string | null
  phone: string | null
  email: string
  created_at: string
  last_login: string | null
}

export interface ShortCode {
  id: number
  short_url: string
  is_active: boolean
  expires_at: string | null
  status: CodeStatus
  clicks: number
  created_at: string
}

export interface Link {
  id: number
  name: string
  url: string
  collection: number | null
  tags: number[]
  short_urls: ShortCode[]
  clicks: number
  last_clicked_at: string | null
  status: CodeStatus
  created_at: string
}

export interface LinkInput {
  name: string
  url: string
  collection?: number | null
  tags?: number[]
  code?: string
  expires_at?: string | null
}

export interface Collection {
  id: number
  name: string
  color: LineColor
  link_count: number
  clicks: number
  created_at: string
}

export interface Tag {
  id: number
  name: string
  color: TagColor
  link_count: number
  created_at: string
}

export interface Invite {
  id: number
  token: string
  note: string
  status: 'pending' | 'used' | 'expired'
  expires_at: string
  used_at: string | null
  used_by_name: string | null
  created_at: string
}

export type Device = 'desktop' | 'mobile' | 'tablet' | 'bot' | 'other'

export interface Click {
  id: number
  short_url: number
  code: string
  link: number
  link_name: string
  ipv4_address: string | null
  ipv6_address: string | null
  user_agent: string | null
  referer: string | null
  referer_domain: string | null
  browser: string
  os: string
  device: Device
  is_bot: boolean
  created_at: string
}

export interface Breakdown {
  name: string | null
  clicks: number
}

export interface Summary {
  range: { days: number; start: string; end: string; timezone: string }
  totals: { clicks: number; previous_clicks: number; visitors: number; bots: number; links: number }
  series: { date: string; clicks: number }[]
  hours: number[]
  top_links: { id: number; name: string; url: string; code: string; clicks: number }[]
  link_clicks: { id: number; clicks: number }[]
  referrers: Breakdown[]
  browsers: Breakdown[]
  os: Breakdown[]
  devices: Breakdown[]
}

export interface SummaryScope {
  days: number
  url?: number
  collection?: number
  tag?: number
}
