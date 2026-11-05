import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { ArrowClockwise, ArrowSquareOut, CaretDown, CaretUp, MagnifyingGlass, Star, Warning, X } from '@phosphor-icons/react'
import { CATEGORIES, STATUS, ago, countdown, discountLabel, filterBrands, fmtDateTime, fmtDay, sortBrands } from './lib.js'

const FAV_KEY = 'saleradar:favs'
const STALE_SITE_HOURS = 12 // scheduler runs every 6h; 12h without a run means something is wrong

const VIEWS = [
  ['all', 'All'], ['live', 'Live now'], ['upcoming', 'Confirmed upcoming'],
  ['free_returns', 'Free returns'], ['free_return_shipping', 'Free return postage'],
  ['favourites', 'Favourites'], ['changed', 'Changed this scan'],
]
const SORTS = [['status', 'Status'], ['discount', 'Discount'], ['start', 'Start date'], ['brand', 'Brand']]

function useFavs() {
  const [favs, setFavs] = useState(() => {
    try { return new Set(JSON.parse(localStorage.getItem(FAV_KEY) || '[]')) } catch { return new Set() }
  })
  const toggle = useCallback((id) => setFavs((prev) => {
    const next = new Set(prev)
    next.has(id) ? next.delete(id) : next.add(id)
    localStorage.setItem(FAV_KEY, JSON.stringify([...next]))
    return next
  }), [])
  return [favs, toggle]
}

function useDashboard() {
  const [state, setState] = useState({ data: null, error: null, loading: true })
  const load = useCallback(async () => {
    setState((s) => ({ ...s, loading: true }))
    try {
      const res = await fetch(`./data/dashboard.json?t=${Date.now()}`, { cache: 'no-store' })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      setState({ data: await res.json(), error: null, loading: false })
    } catch (e) {
      setState((s) => ({ ...s, error: String(e.message || e), loading: false }))
    }
  }, [])
  useEffect(() => { load() }, [load])
  return [state, load]
}

const Tri = ({ v, unverified }) => {
  const map = { YES: ['Yes', 'yes'], NO: ['No', 'no'], CONDITIONAL: ['Conditional', 'cond'], NA: ['N/A', 'unk'] }
  const [label, tone] = map[v] || ['Unknown', 'unk']
  return <span className={`tri tri-${tone}`} title={unverified ? 'From a sourced research pass; not double-checked against the retailer page' : undefined}>{label}{unverified && v && v !== 'UNKNOWN' ? '*' : ''}</span>
}

function StatusPill({ sale, stale }) {
  const s = STATUS[sale.status] || STATUS.NEEDS_CHECKING
  // research-backed values stay trustworthy for a few days even when the site blocks the scanner
  const isStale = sale.basis === 'stale' || (stale && sale.basis !== 'verified')
  const note = sale.basis === 'auto' ? 'auto-detected' : isStale ? 'stale' : null
  return (
    <span className="status-wrap">
      <span className={`pill pill-${s.tone}`}>{s.label}</span>
      {note && <span className={`basis ${note === 'stale' ? 'basis-stale' : ''}`}>{note}</span>}
    </span>
  )
}

function DateCell({ sale, which }) {
  const v = sale[which]
  if (v) return <span className="mono">{fmtDay(v)}</span>
  return <span className="muted" title={sale.expected_note || 'No retailer-confirmed date'}>{sale.expected_note && which === 'start' ? 'Not confirmed' : '-'}</span>
}

function Summary({ data, now }) {
  const m = data.meta
  const cd = countdown(m.black_friday, now)
  const confirmedUpcoming = data.brands.filter((b) => b.sale.status === 'UPCOMING' && b.sale.date_basis === 'confirmed').length
  const live = data.brands.filter((b) => b.sale.status === 'LIVE' || b.sale.status === 'EARLY_ACCESS').length
  const verify = data.brands.filter((b) => b.sale.status === 'NEEDS_CHECKING' || b.sale.basis === 'stale' || (b.scan.stale && b.sale.basis !== 'verified')).length
  const stats = [
    ['Brands monitored', m.brands_total],
    ['Live sales', live, 'live'],
    ['Confirmed upcoming', confirmedUpcoming],
    ['Need verification', verify, verify ? 'warn' : null],
    ['Last successful scan', m.last_successful_scan ? ago(m.last_successful_scan, now) : 'never', null, fmtDateTime(m.last_successful_scan)],
    ['Black Friday', cd ? `${cd.days}d ${cd.hours}h` : 'Today', null, 'Fri 27 Nov 2026, Sydney time'],
  ]
  return (
    <section className="summary" aria-label="Summary">
      {stats.map(([label, value, tone, sub]) => (
        <div key={label} className="stat">
          <div className="stat-label">{label}</div>
          <div className={`stat-value ${tone ? `tone-${tone}` : ''}`}>{value}</div>
          {sub && <div className="stat-sub">{sub}</div>}
        </div>
      ))}
    </section>
  )
}

function SortHeader({ id, label, sort, setSort }) {
  const active = sort.key === id
  return (
    <th aria-sort={active ? (sort.dir === 'asc' ? 'ascending' : 'descending') : 'none'}>
      <button className="th-btn" onClick={() => setSort({ key: id, dir: active && sort.dir === 'asc' ? 'desc' : id === 'discount' && !active ? 'desc' : 'asc' })}>
        {label}{active && (sort.dir === 'asc' ? <CaretUp size={12} weight="bold" /> : <CaretDown size={12} weight="bold" />)}
      </button>
    </th>
  )
}

function Row({ b, fav, onFav, onOpen, now }) {
  const r = b.policy.returns || {}
  const sh = b.policy.shipping || {}
  const unverified = b.policy.verification !== 'verified'
  const d = discountLabel(b.sale)
  const threshold = sh.free_shipping === 'YES' && !sh.free_threshold_aud ? 'Always free' : sh.free_threshold_aud != null ? `$${sh.free_threshold_aud}` : sh.free_shipping === 'NO' ? 'No free shipping' : '-'
  return (
    <tr className={b.changed_this_run ? 'changed' : undefined}>
      <td className="c-fav">
        <button className={`fav ${fav ? 'on' : ''}`} onClick={() => onFav(b.id)} aria-pressed={fav} aria-label={`${fav ? 'Remove' : 'Add'} ${b.name} ${fav ? 'from' : 'to'} favourites`}>
          <Star size={16} weight={fav ? 'fill' : 'regular'} />
        </button>
      </td>
      <td className="c-brand">
        <button className="brand-btn" onClick={() => onOpen(b.id)}>{b.name}</button>
        {b.changed_this_run && <span className="new-tag">Changed</span>}
        <div className="brand-sub">{b.storefront}</div>
      </td>
      <td data-label="Category" className="c-cat">{CATEGORIES[b.category]}</td>
      <td data-label="Status"><StatusPill sale={b.sale} stale={b.scan.stale} /></td>
      <td data-label="Discount" className="c-disc">{d ? <><span className="disc">{d.text}</span>{d.scope && <div className="brand-sub">{d.scope}</div>}</> : <span className="muted">{b.sale.status === 'LIVE' || b.sale.status === 'EARLY_ACCESS' ? 'Not stated' : '-'}</span>}</td>
      <td data-label="Starts"><DateCell sale={b.sale} which="start" /></td>
      <td data-label="Ends"><DateCell sale={b.sale} which="end" /></td>
      <td data-label="Free returns"><Tri v={r.free_returns} unverified={unverified} /></td>
      <td data-label="Free return postage"><Tri v={r.free_return_postage} unverified={unverified} /></td>
      <td data-label="Return window" className="mono" title={r.window_note}>{r.window_days ? `${r.window_days} days` : r.window_note || <span className="muted">-</span>}</td>
      <td data-label="Free shipping over" className="mono">{threshold}</td>
      <td data-label="Last checked">
        <span className={b.scan.ok ? 'nowrap' : 'tone-warn nowrap'} title={fmtDateTime(b.scan.last_attempt)}>{b.scan.ok ? ago(b.scan.last_success, now) : 'Scan blocked'}</span>
        {!b.scan.ok && <div className="brand-sub">{b.scan.last_success ? `last ok ${ago(b.scan.last_success, now)}` : b.sale.verified_at ? `researched ${ago(b.sale.verified_at, now)}` : 'never reached'}</div>}
      </td>
      <td className="c-act">
        {b.links.sale || b.links.home ? <a className="btn-ghost" href={b.links.sale || b.links.home} target="_blank" rel="noreferrer">Shop <ArrowSquareOut size={13} /></a> : null}
        <button className="btn-ghost" onClick={() => onOpen(b.id)}>Details</button>
      </td>
    </tr>
  )
}

const FIELD_FMT = (v) => (v === null || v === undefined || v === '' ? 'none' : typeof v === 'boolean' ? (v ? 'OK' : 'failed') : String(v).replaceAll('_', ' ').toLowerCase())

function Detail({ b, onClose, now }) {
  const ref = useRef(null)
  useEffect(() => { if (b) ref.current?.showModal(); else ref.current?.close() }, [b])
  if (!b) return <dialog ref={ref} className="drawer" />
  const s = b.sale, p = b.policy, r = p.returns || {}, sh = p.shipping || {}
  const unverified = p.verification !== 'verified'
  const rows = (pairs) => pairs.filter(([, v]) => v !== undefined).map(([k, v]) => <div className="kv" key={k}><dt>{k}</dt><dd>{v}</dd></div>)
  return (
    <dialog ref={ref} className="drawer" onClose={onClose} onClick={(e) => e.target === ref.current && onClose()} aria-labelledby="d-title">
      <div className="drawer-inner">
        <header className="drawer-head">
          <div>
            <h2 id="d-title">{b.name}</h2>
            <div className="brand-sub">{CATEGORIES[b.category]} · {b.storefront}</div>
          </div>
          <button className="icon-btn" onClick={onClose} aria-label="Close"><X size={18} /></button>
        </header>

        <section>
          <h3>Current promotion</h3>
          <StatusPill sale={s} stale={b.scan.stale} />
          <dl>{rows([
            ['Offer', s.discount_text ? `${s.discount_text}${s.scope !== 'UNKNOWN' ? ` (${s.scope.toLowerCase()})` : ''}` : 'None verified'],
            ['Sale name', s.name || undefined],
            ['Starts', s.start ? `${fmtDay(s.start)} (confirmed by retailer)` : 'No confirmed date'],
            ['Ends', s.end ? `${fmtDay(s.end)} (confirmed by retailer)` : 'No confirmed date'],
            ['Previous pattern', s.expected_note ? `${s.expected_note} (historical, not an announcement)` : undefined],
            ['Code required', s.code_required === 'YES' ? 'Yes' : s.code_required === 'NO' ? 'No' : 'Unknown'],
            ['Verified code', s.code || undefined],
            ['Early access / members', s.early_access || undefined],
            ['Conditions', s.conditions || undefined],
            ['How we know', s.basis === 'verified' ? (s.verification === 'verified' ? 'Checked directly against the retailer page' : 'From a sourced research pass (quote and link below), not double-checked') : s.basis === 'auto' ? `Detected automatically on the retailer page (confidence ${s.confidence})` : s.basis === 'stale' ? 'Last known value. The latest scan could not reach the site.' : 'No sale information found'],
            ['Sale verified', s.verified_at ? fmtDateTime(s.verified_at) : undefined],
          ])}</dl>
          {s.evidence && <blockquote className="evidence">"{s.evidence}"</blockquote>}
          {s.source_url && <a className="src" href={s.source_url} target="_blank" rel="noreferrer">Sale source <ArrowSquareOut size={13} /></a>}
        </section>

        <section>
          <h3>Returns {unverified && <span className="basis">{p.verification === 'sourced' ? 'sourced, not double-checked' : 'not yet researched'}</span>}</h3>
          {p.summary && <p className="summary-text">{p.summary}</p>}
          <dl>{rows([
            ['Change-of-mind returns', <Tri v={r.change_of_mind} />],
            ['Free returns', <Tri v={r.free_returns} />],
            ['Free return postage', <Tri v={r.free_return_postage} />],
            ['Return postage cost', r.postage_cost || undefined],
            ['Free in-store returns', <Tri v={r.free_instore_returns} />],
            ['Prepaid label', <Tri v={r.prepaid_label} />],
            ['Window', r.window_note || (r.window_days ? `${r.window_days} days` : 'Unknown')],
            ['Sale items excluded', <Tri v={r.sale_items_excluded} />],
            ['Refund type', r.refund_type || 'Unknown'],
            ['Conditions', r.conditions || undefined],
          ])}</dl>
          {r.evidence && <blockquote className="evidence">"{r.evidence}"</blockquote>}
          {r.source_url && <a className="src" href={r.source_url} target="_blank" rel="noreferrer">Returns policy <ArrowSquareOut size={13} /></a>}
        </section>

        <section>
          <h3>Shipping to Australia</h3>
          <dl>{rows([
            ['Free delivery', <Tri v={sh.free_shipping} />],
            ['Free over', sh.free_shipping === 'YES' && sh.free_threshold_aud == null ? 'Always free' : sh.free_threshold_aud != null ? `$${sh.free_threshold_aud} AUD` : 'Unknown'],
            ['Standard delivery', sh.standard_aud != null ? `$${sh.standard_aud} AUD` : 'Unknown'],
            ['Ships to Australia', <Tri v={sh.ships_to_au} />],
            ['Restrictions', sh.restrictions || undefined],
          ])}</dl>
          {sh.evidence && <blockquote className="evidence">"{sh.evidence}"</blockquote>}
          {sh.source_url && <a className="src" href={sh.source_url} target="_blank" rel="noreferrer">Delivery policy <ArrowSquareOut size={13} /></a>}
          {p.page_changed_since_verified?.length > 0 && <p className="tone-warn"><Warning size={14} /> The {p.page_changed_since_verified.join(' and ')} page text changed since it was verified. Re-check before relying on it.</p>}
        </section>

        <section>
          <h3>Checks</h3>
          <dl>{rows([
            ['Policy verified', p.verified_at ? fmtDateTime(p.verified_at) : 'Never'],
            ['Policy page checked', p.page_checked_at ? `${fmtDateTime(p.page_checked_at)} (${p.page_ok ? 'reachable' : 'unreachable'})` : 'Never'],
            ['Last sale scan', `${fmtDateTime(b.scan.last_attempt)} (${b.scan.ok ? 'OK' : 'failed'})`],
            ['Last successful scan', fmtDateTime(b.scan.last_success)],
            ['Pages read', `${b.scan.pages_ok ?? 0} of ${b.scan.pages_tried ?? 0}`],
          ])}</dl>
          {b.scan.errors?.length > 0 && <ul className="errs">{b.scan.errors.map((e) => <li key={e.url}><span className="mono">{e.error}</span> {e.url}</li>)}</ul>}
          {b.scan.discovered?.length > 0 && <p className="brand-sub">Campaign pages found: {b.scan.discovered.map((u) => <a key={u} href={u} target="_blank" rel="noreferrer">{new URL(u).pathname}</a>).reduce((a, x) => [a, ', ', x])}</p>}
        </section>

        <section>
          <h3>Official links</h3>
          <div className="links">
            {[['Store', b.links.home], ['Sale page', b.links.sale], ['Returns', b.links.returns], ['Delivery', b.links.shipping]].filter(([, u]) => u).map(([k, u]) => (
              <a key={k} className="btn-ghost" href={u} target="_blank" rel="noreferrer">{k} <ArrowSquareOut size={13} /></a>
            ))}
          </div>
        </section>

        <section>
          <h3>Recent changes</h3>
          {b.recent_changes?.length ? (
            <ul className="changes">{b.recent_changes.map((e) => (
              <li key={e.id}><span className="mono muted">{ago(e.at, now)}</span> {e.label}: {e.field === 'brand' ? 'added to tracker' : <>{FIELD_FMT(e.old)} → <strong>{FIELD_FMT(e.new)}</strong></>}</li>
            ))}</ul>
          ) : <p className="muted">No changes recorded yet.</p>}
        </section>
      </div>
    </dialog>
  )
}

export default function App() {
  const [{ data, error, loading }, reload] = useDashboard()
  const [favs, toggleFav] = useFavs()
  const [q, setQ] = useState('')
  const [category, setCategory] = useState('all')
  const [view, setView] = useState('all')
  const [sort, setSort] = useState({ key: 'status', dir: 'asc' })
  const [openId, setOpenId] = useState(null)
  const [now, setNow] = useState(() => new Date())
  useEffect(() => { const t = setInterval(() => setNow(new Date()), 60000); return () => clearInterval(t) }, [])

  const rows = useMemo(() => data ? sortBrands(filterBrands(data.brands, { q, category, view, favs }), sort.key, sort.dir, favs) : [], [data, q, category, view, favs, sort])
  const open = data?.brands.find((b) => b.id === openId) || null
  const siteStale = data && (now - new Date(data.meta.generated_at)) / 3600000 > STALE_SITE_HOURS
  const failing = data?.brands.filter((b) => !b.scan.ok) || []

  return (
    <div className="app">
      <header className="top">
        <h1>Sale Radar</h1>
        <div className="top-right">
          {data && <span className="muted" title="Sydney time">Data from {fmtDateTime(data.meta.generated_at)}</span>}
          <button className="btn" onClick={() => { reload(); setNow(new Date()) }} disabled={loading} title="Reloads the latest published data. Retailer scans run automatically every 6 hours.">
            <ArrowClockwise size={15} className={loading ? 'spin' : ''} /> Reload data
          </button>
        </div>
      </header>

      {error && <div className="banner banner-warn" role="alert"><Warning size={16} /> Could not load data ({error}). {data ? 'Showing the last loaded copy.' : ''}</div>}
      {siteStale && <div className="banner banner-warn" role="alert"><Warning size={16} /> No scan has published in {Math.round((now - new Date(data.meta.generated_at)) / 3600000)} hours. The scheduler may be failing; check GitHub Actions.</div>}

      {!data && loading && <div className="skeleton" aria-busy="true"><div /><div /><div /></div>}

      {data && <>
        <Summary data={data} now={now} />

        <section className="controls" aria-label="Filters">
          <label className="search">
            <MagnifyingGlass size={16} aria-hidden />
            <span className="sr-only">Search brands</span>
            <input type="search" placeholder="Search brands" value={q} onChange={(e) => setQ(e.target.value)} />
          </label>
          <label className="select">
            <span className="sr-only">Category</span>
            <select value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="all">All categories</option>
              {Object.entries(CATEGORIES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </label>
          <label className="select mobile-only">
            <span className="sr-only">Sort by</span>
            <select value={`${sort.key}:${sort.dir}`} onChange={(e) => { const [key, dir] = e.target.value.split(':'); setSort({ key, dir }) }}>
              {SORTS.flatMap(([k, l]) => [[`${k}:asc`, `${l} ↑`], [`${k}:desc`, `${l} ↓`]]).map(([v, l]) => <option key={v} value={v}>Sort: {l}</option>)}
            </select>
          </label>
          <div className="views" role="group" aria-label="Quick filters">
            {VIEWS.map(([k, l]) => <button key={k} className={`chip ${view === k ? 'on' : ''}`} aria-pressed={view === k} onClick={() => setView(k)}>{l}</button>)}
          </div>
        </section>

        <div className="table-wrap">
          <table className="grid">
            <thead>
              <tr>
                <th className="c-fav"><span className="sr-only">Favourite</span></th>
                <SortHeader id="brand" label="Brand" sort={sort} setSort={setSort} />
                <th>Category</th>
                <SortHeader id="status" label="Status" sort={sort} setSort={setSort} />
                <SortHeader id="discount" label="Discount" sort={sort} setSort={setSort} />
                <SortHeader id="start" label="Starts" sort={sort} setSort={setSort} />
                <th>Ends</th>
                <th title="Change-of-mind return with no fee via at least one method (mail or store)">Free returns</th>
                <th title="Retailer pays postage for mailed returns">Free return postage</th>
                <th>Return window</th>
                <th>Free shipping over</th>
                <th>Last checked</th>
                <th><span className="sr-only">Actions</span></th>
              </tr>
            </thead>
            <tbody>
              {rows.map((b) => <Row key={b.id} b={b} fav={favs.has(b.id)} onFav={toggleFav} onOpen={setOpenId} now={now} />)}
            </tbody>
          </table>
          {rows.length === 0 && <div className="empty">No brands match these filters. <button className="link" onClick={() => { setQ(''); setCategory('all'); setView('all') }}>Clear filters</button></div>}
        </div>

        <footer className="foot">
          <div>
            <h4>Reading the table</h4>
            <p><strong>Free returns</strong> means a change-of-mind return costs nothing by at least one method (often in store). <strong>Free return postage</strong> means the retailer pays for mailed returns. These are voluntary store policies, separate from your Australian Consumer Law rights for faulty items.</p>
            <p><strong>Dates</strong> appear only when the retailer has published them. "Not confirmed" means we know a past pattern but nothing is announced. <strong>auto-detected</strong> means the scanner found sale wording on the retailer page but no person has checked it. <strong>*</strong> marks policy values not yet verified against the retailer page.</p>
          </div>
          <div>
            <h4>Scan health</h4>
            <p>{data.meta.scan_ok} of {data.meta.brands_total} retailer sites were readable in the latest scan. Sites that block automated access keep their last known values, marked stale.</p>
            {failing.length > 0 && <p className="muted">Not readable: {failing.map((b) => b.name).join(', ')}.</p>}
            <p className="muted">Retailer scans run automatically about every 6 hours. Always confirm the price at checkout.</p>
          </div>
        </footer>
      </>}

      <Detail b={open} onClose={() => setOpenId(null)} now={now} />
    </div>
  )
}
