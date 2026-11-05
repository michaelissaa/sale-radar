// Unit tests for the pure functions in Code.gs. Run: node --test notify/apps-script/
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import vm from 'node:vm'

const ctx = {}
vm.createContext(ctx)
vm.runInContext(readFileSync(new URL('./Code.gs', import.meta.url), 'utf8'), ctx)
const { normaliseSubscription, matchAlerts, renderAlertEmail, renderConfirmEmail } = ctx

test('validates email, brands and prefs', () => {
  assert.equal(normaliseSubscription({ email: 'nope', brands: ['x'], prefs: ['sales'] }).ok, false)
  assert.equal(normaliseSubscription({ email: 'a@b.com', brands: [], prefs: ['sales'] }).ok, false)
  assert.equal(normaliseSubscription({ email: 'a@b.com', brands: ['gymshark'], prefs: ['bogus'] }).ok, false)
  assert.equal(normaliseSubscription({ email: 'a@b.com', brands: ['gymshark'], prefs: ['sales'], website: 'spam' }).ok, false, 'honeypot')
  const ok = normaliseSubscription({ email: ' Me@Example.com.au ', brands: ['gymshark', 'BAD ID', '*'], prefs: ['black_friday', 'x'] })
  assert.equal(ok.ok, true)
  assert.equal(ok.email, 'me@example.com.au')
  assert.deepEqual([...ok.brands], ['*'])
  assert.deepEqual([...ok.prefs], ['black_friday'])
})

const alerts = [
  { brand: 'gymshark', brand_name: 'Gymshark', kind: 'bf_dates', title: 'Gymshark: Black Friday dates confirmed', detail: 'Fri 20 Nov', url: 'https://au.gymshark.com/' },
  { brand: 'lskd', brand_name: 'LSKD', kind: 'sale_live', title: 'LSKD: Sale started', detail: '', url: 'javascript:alert(1)' },
  { brand: 'nike', brand_name: 'Nike', kind: 'discount', title: 'Nike: Discount changed', detail: '<b>40%</b>', url: 'https://nike.com/au' },
]

test('matches only chosen brands and alert types', () => {
  assert.deepEqual(matchAlerts({ brands: ['gymshark', 'lskd'], prefs: ['black_friday'] }, alerts).map((a) => a.brand), ['gymshark'])
  assert.deepEqual(matchAlerts({ brands: ['*'], prefs: ['sales', 'discounts'] }, alerts).map((a) => a.brand), ['lskd', 'nike'])
  assert.equal(matchAlerts({ brands: ['asos'], prefs: ['black_friday', 'sales', 'discounts'] }, alerts).length, 0)
})

test('emails escape content, drop unsafe links, include unsubscribe', () => {
  const m = renderAlertEmail(alerts, 'https://site/', 'https://script/unsub?token=abc')
  assert.match(m.subject, /3 updates/)
  assert.ok(!m.html.includes('<b>40%</b>'), 'html escaped')
  assert.ok(!m.html.includes('javascript:'), 'unsafe url removed')
  assert.ok(m.html.includes('https://script/unsub?token=abc') && m.text.includes('Unsubscribe: https://script/unsub?token=abc'))
  assert.equal(renderAlertEmail([alerts[0]], 'https://site/', 'u').subject, 'Gymshark: Black Friday dates confirmed')
  assert.match(renderConfirmEmail('https://c', { brands: ['*'] }).html, /all brands/)
})
