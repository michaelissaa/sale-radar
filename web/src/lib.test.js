// Run: npm test
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { countdown, effectiveStatus, filterBrands, fmtDay, goesLive, sortBrands, sydneyMidnight, tzOffsetMinutes } from './lib.js'

test('Sydney is UTC+11 in November (AEDT) and +10 in June', () => {
  assert.equal(tzOffsetMinutes(new Date('2026-11-27T00:00:00Z')), 660)
  assert.equal(tzOffsetMinutes(new Date('2026-06-15T00:00:00Z')), 600)
})

test('Black Friday starts 13:00 UTC on 26 Nov', () => {
  assert.equal(sydneyMidnight('2026-11-27').toISOString(), '2026-11-26T13:00:00.000Z')
})

test('fmtDay never shifts the calendar day', () => {
  assert.equal(fmtDay('2026-11-27'), 'Fri, 27 Nov')
  assert.equal(fmtDay('2026-11-30'), 'Mon, 30 Nov')
  assert.match(fmtDay('2026-11-10T09:00:00+11:00'), /Tue, 10 Nov.*9:00/)
})

test('countdown from 5 Nov Sydney evening', () => {
  const c = countdown('2026-11-27', new Date('2026-11-05T08:00:00Z')) // 7pm Sydney
  assert.deepEqual(c, { days: 21, hours: 5 })
  assert.equal(countdown('2026-11-27', new Date('2026-11-26T13:00:01Z')), null)
})

const mk = (id, name, status, pct, extra = {}) => ({
  id, name, category: 'gymwear', priority: 2,
  sale: { status, discount_max_pct: pct, start: null, date_basis: 'unknown', ...extra.sale },
  policy: { returns: extra.returns || {} },
})
const B = [
  mk('a', 'Alpha', 'LIVE', 30, { returns: { free_returns: 'YES', free_return_postage: 'NO' } }),
  mk('b', 'Bravo', 'UPCOMING', null, { sale: { date_basis: 'unknown' } }),
  mk('c', 'Charlie', 'UPCOMING', 50, { sale: { date_basis: 'confirmed', start: '2026-11-20' }, returns: { free_returns: 'YES', free_return_postage: 'YES' } }),
  mk('d', 'Delta', 'NOT_ANNOUNCED', null),
]

test('filters keep free returns and free return postage separate', () => {
  assert.deepEqual(filterBrands(B, { view: 'free_returns' }).map((b) => b.id), ['a', 'c'])
  assert.deepEqual(filterBrands(B, { view: 'free_return_shipping' }).map((b) => b.id), ['c'])
})

test('confirmed-upcoming filter excludes unconfirmed dates', () => {
  assert.deepEqual(filterBrands(B, { view: 'upcoming' }).map((b) => b.id), ['c'])
})

test('regular sales are separate from Black Friday', () => {
  const L = [mk('x', 'X', 'NOT_ANNOUNCED', null, { sale: { regular_active: true } }), mk('y', 'Y', 'UPCOMING', null), mk('z', 'Z', 'NOT_ANNOUNCED', null)]
  assert.deepEqual(filterBrands(L, { view: 'regular' }).map((b) => b.id), ['x'])
  assert.deepEqual(filterBrands(L, { view: 'live' }).map((b) => b.id), [])
  assert.deepEqual(filterBrands(L, { view: 'announced' }).map((b) => b.id), ['y'])
})

test('confirmed launch flips to live at the exact Sydney time', () => {
  const sale = { status: 'UPCOMING', start: '2026-11-10T09:00:00+11:00', end: '2026-11-10T13:00:00+11:00', date_basis: 'confirmed' }
  assert.equal(effectiveStatus(sale, new Date('2026-11-09T21:59:00Z')), 'UPCOMING') // 8:59am Sydney
  assert.equal(effectiveStatus(sale, new Date('2026-11-09T22:00:00Z')), 'LIVE')
  assert.equal(effectiveStatus(sale, new Date('2026-11-10T02:01:00Z')), 'ENDED')
  assert.equal(effectiveStatus({ ...sale, date_basis: 'unknown' }, new Date('2026-11-10T00:00:00Z')), 'UPCOMING', 'unconfirmed never auto-flips')
  assert.equal(goesLive(sale, new Date('2026-11-05T09:00:00Z')).label, 'in 4d 13h')
  assert.equal(goesLive({ ...sale, date_basis: 'unknown' }), null)
  const nb = { status: 'UPCOMING', start: '2026-11-13', end: '2026-11-29', date_basis: 'confirmed' }
  assert.equal(effectiveStatus(nb, new Date('2026-11-29T12:00:00Z')), 'LIVE', 'end date is inclusive (Sydney)')
  assert.equal(effectiveStatus(nb, new Date('2026-11-29T13:00:01Z')), 'ENDED')
})

test('status sort puts soonest confirmed launch first', () => {
  const L = [mk('late', 'Late', 'UPCOMING', null, { sale: { start: '2026-11-20', date_basis: 'confirmed' } }),
    mk('tbc', 'Tbc', 'UPCOMING', null), mk('soon', 'Soon', 'UPCOMING', null, { sale: { start: '2026-11-10', date_basis: 'confirmed' } }), mk('live', 'Live', 'LIVE', 30)]
  assert.deepEqual(sortBrands(L, 'status', 'asc', new Set(), new Date('2026-11-05T00:00:00Z')).map((b) => b.id), ['live', 'soon', 'late', 'tbc'])
})

test('search and live filter', () => {
  assert.deepEqual(filterBrands(B, { q: 'char' }).map((b) => b.id), ['c'])
  assert.deepEqual(filterBrands(B, { view: 'live' }).map((b) => b.id), ['a'])
})

test('sort by discount desc puts nulls last; favourites first', () => {
  assert.deepEqual(sortBrands(B, 'discount', 'desc').map((b) => b.id), ['c', 'a', 'b', 'd'])
  assert.deepEqual(sortBrands(B, 'discount', 'desc', new Set(['d'])).map((b) => b.id), ['d', 'c', 'a', 'b'])
  assert.deepEqual(sortBrands(B, 'brand', 'desc').map((b) => b.id), ['d', 'c', 'b', 'a'])
})
