import { useEffect, useMemo, useRef, useState } from 'react'
import { CheckCircle, X } from '@phosphor-icons/react'
import { CATEGORIES } from './lib.js'

const TYPES = [
  ['black_friday', 'Black Friday alerts (recommended)', 'Sale announced, launch date confirmed, a reminder 24 hours before it goes live, the moment it goes live, and when it ends', true],
  ['discounts', 'Black Friday discount changes', 'The advertised Black Friday discount changes while the sale is on', false],
  ['sales', 'Regular sales too', 'A normal (not Black Friday) sale starts or ends', false],
]

// Sign-up form. Posts to the Google Apps Script backend, which emails a confirmation link (double opt-in).
export default function Alerts({ brands, initial, favs, notifyUrl, onClose }) {
  const ref = useRef(null)
  const [email, setEmail] = useState('')
  const [scope, setScope] = useState(initial.length ? 'pick' : favs.size ? 'favs' : 'all')
  const [picked, setPicked] = useState(() => new Set(initial))
  const [types, setTypes] = useState(() => new Set(TYPES.filter((t) => t[3]).map((t) => t[0])))
  const [state, setState] = useState({ step: 'form', error: null })
  const [q, setQ] = useState('')
  useEffect(() => { ref.current?.showModal() }, [])

  const chosen = scope === 'all' ? ['*'] : scope === 'favs' ? [...favs] : [...picked]
  const grouped = useMemo(() => Object.keys(CATEGORIES).map((c) => [c, brands.filter((b) => b.category === c && b.name.toLowerCase().includes(q.toLowerCase()))]), [brands, q])
  const toggle = (set, setter, id) => { const n = new Set(set); n.has(id) ? n.delete(id) : n.add(id); setter(n) }

  async function submit(e) {
    e.preventDefault()
    const form = new FormData(e.currentTarget)
    if (!chosen.length) return setState({ step: 'form', error: 'Choose at least one brand.' })
    if (!types.size) return setState({ step: 'form', error: 'Choose at least one alert type.' })
    setState({ step: 'sending', error: null })
    try {
      // Apps Script can't answer CORS preflights, so send a "simple" text/plain request; the reply is opaque.
      await fetch(notifyUrl, { method: 'POST', mode: 'no-cors', headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify({ action: 'subscribe', email, brands: chosen, prefs: [...types], website: form.get('website') || '' }) })
      setState({ step: 'sent', error: null })
    } catch {
      setState({ step: 'form', error: 'Could not reach the alerts service. Check your connection and try again.' })
    }
  }

  return (
    <dialog ref={ref} className="modal" onClose={onClose} onClick={(e) => e.target === ref.current && ref.current.close()} aria-labelledby="a-title">
      <form className="modal-inner" onSubmit={submit} noValidate={false}>
        <header className="drawer-head">
          <h2 id="a-title">Email alerts</h2>
          <button type="button" className="icon-btn" onClick={() => ref.current.close()} aria-label="Close"><X size={18} /></button>
        </header>

        {!notifyUrl ? (
          <p className="summary-text">Email alerts aren't switched on for this dashboard yet. The owner needs to connect the email service (see the project README).</p>
        ) : state.step === 'sent' ? (
          <div className="sent">
            <CheckCircle size={28} weight="fill" className="tone-live" />
            <p><strong>Check your inbox.</strong> We sent a confirmation link to {email}. Alerts start once you click it. If it's not there in a few minutes, check spam.</p>
            <button type="button" className="btn" onClick={() => ref.current.close()}>Done</button>
          </div>
        ) : (
          <>
            <div className="field">
              <label htmlFor="a-email">Email address</label>
              <input id="a-email" type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            {/* honeypot: hidden from people, bots fill it in */}
            <input className="hp" name="website" tabIndex={-1} autoComplete="off" aria-hidden="true" />

            <fieldset className="field">
              <legend>Brands</legend>
              <div className="seg">
                {favs.size > 0 && <label><input type="radio" name="scope" checked={scope === 'favs'} onChange={() => setScope('favs')} /> My favourites ({favs.size})</label>}
                <label><input type="radio" name="scope" checked={scope === 'all'} onChange={() => setScope('all')} /> All brands</label>
                <label><input type="radio" name="scope" checked={scope === 'pick'} onChange={() => setScope('pick')} /> Choose ({picked.size})</label>
              </div>
              {scope === 'pick' && (
                <div className="picker">
                  <input type="search" placeholder="Filter brands" aria-label="Filter brands" value={q} onChange={(e) => setQ(e.target.value)} />
                  {grouped.map(([c, list]) => list.length > 0 && (
                    <div key={c}>
                      <div className="picker-cat">{CATEGORIES[c]}</div>
                      <div className="picker-grid">
                        {list.map((b) => (
                          <label key={b.id}><input type="checkbox" checked={picked.has(b.id)} onChange={() => toggle(picked, setPicked, b.id)} /> {b.name}</label>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </fieldset>

            <fieldset className="field">
              <legend>Alert me about</legend>
              {TYPES.map(([id, label, help]) => (
                <label key={id} className="check">
                  <input type="checkbox" checked={types.has(id)} onChange={() => toggle(types, setTypes, id)} />
                  <span><strong>{label}</strong><br /><span className="muted">{help}</span></span>
                </label>
              ))}
            </fieldset>

            {state.error && <p className="tone-warn" role="alert">{state.error}</p>}
            <p className="muted small">We'll email you a link to confirm. Alerts are checked about every 6 hours. Every email has a one-click unsubscribe. Your email is stored privately, not on this public site.</p>
            <button className="btn" type="submit" disabled={state.step === 'sending'}>{state.step === 'sending' ? 'Sending...' : 'Send confirmation email'}</button>
          </>
        )}
      </form>
    </dialog>
  )
}
