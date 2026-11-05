// Run: npm test
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { countdown, filterBrands, fmtDay, sortBrands, sydneyMidnight, tzOffsetMinutes } from './lib.js'

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

test('search and live filter', () => {
  assert.deepEqual(filterBrands(B, { q: 'char' }).map((b) => b.id), ['c'])
  assert.deepEqual(filterBrands(B, { view: 'live' }).map((b) => b.id), ['a'])
})

test('sort by discount desc puts nulls last; favourites first', () => {
  assert.deepEqual(sortBrands(B, 'discount', 'desc').map((b) => b.id), ['c', 'a', 'b', 'd'])
  assert.deepEqual(sortBrands(B, 'discount', 'desc', new Set(['d'])).map((b) => b.id), ['d', 'c', 'a', 'b'])
  assert.deepEqual(sortBrands(B, 'brand', 'desc').map((b) => b.id), ['d', 'c', 'b', 'a'])
})
