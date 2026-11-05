// Pure helpers: formatting in Sydney time, filtering, sorting. Tested in lib.test.js.
export const TZ = 'Australia/Sydney'

export const STATUS = {
  LIVE: { label: 'Live', tone: 'live', order: 0 },
  EARLY_ACCESS: { label: 'Early access', tone: 'early', order: 1 },
  UPCOMING: { label: 'Upcoming', tone: 'upcoming', order: 2 },
  NEEDS_CHECKING: { label: 'Needs checking', tone: 'warn', order: 3 },
  NOT_ANNOUNCED: { label: 'Not announced', tone: 'muted', order: 4 },
  ENDED: { label: 'Ended', tone: 'muted', order: 5 },
}

export const CATEGORIES = { gymwear: 'Gym & fitness', sportswear: 'Sportswear', fashion: 'Fashion & streetwear', department: 'Department & marketplaces', tech: 'Tech & electronics' }

// Offset (minutes) of a time zone at a given instant, via Intl (handles AEDT/AEST switch).
export function tzOffsetMinutes(date, tz = TZ) {
  const p = Object.fromEntries(
    new Intl.DateTimeFormat('en-US', { timeZone: tz, hourCycle: 'h23', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
      .formatToParts(date).map((x) => [x.type, x.value]),
  )
  const asUtc = Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour, +p.minute, +p.second)
  return Math.round((asUtc - date.getTime()) / 60000)
}

// Midnight at the start of a Sydney calendar day, as a Date.
export function sydneyMidnight(ymd) {
  const [y, m, d] = ymd.split('-').map(Number)
  const guess = new Date(Date.UTC(y, m - 1, d))
  return new Date(guess.getTime() - tzOffsetMinutes(guess) * 60000)
}

export function fmtDateTime(iso) {
  if (!iso) return '-'
  return new Intl.DateTimeFormat('en-AU', { timeZone: TZ, weekday: 'short', day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' }).format(new Date(iso))
}

// A 'YYYY-MM-DD' Sydney calendar date. Formatted in UTC so it never shifts a day.
export function fmtDay(ymd) {
  if (!ymd) return null
  if (ymd.includes('T')) return fmtDateTime(ymd) // exact launch time, e.g. a 4-hour sale
  const [y, m, d] = ymd.split('-').map(Number)
  return new Intl.DateTimeFormat('en-AU', { timeZone: 'UTC', weekday: 'short', day: 'numeric', month: 'short' }).format(new Date(Date.UTC(y, m - 1, d)))
}

export function ago(iso, now = new Date()) {
  if (!iso) return 'never'
  const mins = Math.round((now - new Date(iso)) / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const h = Math.round(mins / 60)
  if (h < 48) return `${h}h ago`
  return `${Math.round(h / 24)}d ago`
}

export function countdown(targetYmd, now = new Date()) {
  const ms = sydneyMidnight(targetYmd) - now
  if (ms <= 0) return null
  const days = Math.floor(ms / 86400000)
  const hours = Math.floor((ms % 86400000) / 3600000)
  return { days, hours }
}

export const isYes = (v) => v === 'YES'

const toDate = (v) => (v.includes('T') ? new Date(v) : sydneyMidnight(v))

// The Black Friday status as of right now. A retailer-confirmed launch time flips to LIVE on the
// client the moment it passes, without waiting for the next 6-hourly scan.
export function effectiveStatus(sale, now = new Date()) {
  if (sale.date_basis !== 'confirmed') return sale.status
  const endMs = sale.end ? (sale.end.includes('T') ? new Date(sale.end) : sydneyMidnight(sale.end)).getTime() + (sale.end.includes('T') ? 0 : 86400000 - 1) : null
  if (endMs != null && now.getTime() > endMs && ['LIVE', 'EARLY_ACCESS', 'UPCOMING'].includes(sale.status)) return 'ENDED'
  if (sale.start && sale.status === 'UPCOMING' && toDate(sale.start) <= now) return 'LIVE'
  return sale.status
}

// When the Black Friday sale goes live, only if the retailer confirmed it.
export function goesLive(sale, now = new Date()) {
  if (sale.date_basis !== 'confirmed' || !sale.start) return null
  const at = toDate(sale.start)
  const ms = at - now
  if (ms <= 0) return { at, live: true }
  const d = Math.floor(ms / 86400000), h = Math.floor((ms % 86400000) / 3600000), m = Math.floor((ms % 3600000) / 60000)
  return { at, live: false, ms, label: d ? `in ${d}d ${h}h` : h ? `in ${h}h ${m}m` : `in ${m}m` }
}

export function filterBrands(brands, { q = '', category = 'all', view = 'all', favs = new Set(), now = new Date() } = {}) {
  const needle = q.trim().toLowerCase()
  return brands.filter((b) => {
    if (needle && !b.name.toLowerCase().includes(needle)) return false
    if (category !== 'all' && b.category !== category) return false
    const r = b.policy?.returns || {}
    const st = effectiveStatus(b.sale, now)
    switch (view) {
      case 'live': return st === 'LIVE' || st === 'EARLY_ACCESS'
      case 'soon': return st === 'UPCOMING' && b.sale.date_basis === 'confirmed'
      case 'announced': return st === 'UPCOMING'
      case 'regular': return !!b.sale.regular_active
      case 'upcoming': return st === 'UPCOMING' && b.sale.date_basis === 'confirmed'
      case 'free_returns': return isYes(r.free_returns)
      case 'free_return_shipping': return isYes(r.free_return_postage)
      case 'favourites': return favs.has(b.id)
      case 'changed': return !!b.changed_this_run
      default: return true
    }
  })
}

const startMs = (v) => (v.includes('T') ? new Date(v) : sydneyMidnight(v)).getTime()
const nullsLast = (a, b, cmp) => (a == null && b == null ? 0 : a == null ? 1 : b == null ? -1 : cmp(a, b))

export function sortBrands(list, key = 'status', dir = 'asc', favs = new Set(), now = new Date()) {
  const sign = dir === 'desc' ? -1 : 1
  const by = {
    brand: (a, b) => sign * a.name.localeCompare(b.name),
    discount: (a, b) => nullsLast(a.sale.discount_max_pct, b.sale.discount_max_pct, (x, y) => sign * (x - y)),
    start: (a, b) => nullsLast(a.sale.start, b.sale.start, (x, y) => sign * (startMs(x) - startMs(y))),
    // Black Friday first: live, then soonest confirmed launch, then announced, then the rest
    status: (a, b) => sign * (STATUS[effectiveStatus(a.sale, now)].order - STATUS[effectiveStatus(b.sale, now)].order)
      || nullsLast(a.sale.date_basis === 'confirmed' ? a.sale.start : null, b.sale.date_basis === 'confirmed' ? b.sale.start : null, (x, y) => startMs(x) - startMs(y))
      || a.priority - b.priority || a.name.localeCompare(b.name),
  }[key]
  // favourites always float to the top, then the chosen sort
  return [...list].sort((a, b) => (favs.has(b.id) - favs.has(a.id)) || by(a, b) || a.name.localeCompare(b.name))
}

export function discountLabel(s) {
  if (!s.discount_text) return null
  const scope = s.scope === 'SITEWIDE' ? 'sitewide' : s.scope === 'SELECTED' ? 'selected items' : null
  // don't repeat the scope if the retailer's wording already says it
  const said = /sitewide|everything|selected|eligible|almost/i.test(s.discount_text)
  return { text: s.discount_text, scope: said ? null : scope }
}
