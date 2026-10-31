const fixture = require('./fixtures/offline-search-parity.json')
const { rankOffline } = require('../utils/offlineSearch')

const bundle = {
  search: {
    ...fixture.search,
    rules: fixture.rules.map((r) => ({ ...r, review_status: 'draft', review_status_label: 'Draft - under clinical review.' })),
  },
}

describe('offline ranking gives the server ranking (shared fixture)', () => {
  fixture.queries.forEach((q, i) => {
    test(`${JSON.stringify(q)}`, () => {
      const out = rankOffline(bundle, q.symptoms, {
        age: q.age === undefined ? null : q.age, sex: q.sex || null, family: q.family || null, limit: q.limit,
      })
      expect(out.results.map((r) => [r.rule_id, r.match_score, r.matched_presentations, r.cant_miss]))
        .toEqual(fixture.expected[i].results)
      expect(out.negated_terms).toEqual(fixture.expected[i].negated_terms)
    })
  })
})

test('offline results are labelled and carry review status, never AI', () => {
  const { results } = rankOffline(bundle, ['chest pain'])
  expect(results.every((r) => r.offline && !r.ai_suggested && r.has_tree)).toBe(true)
  expect(results[0].review_status_label).toBe('Draft - under clinical review.')
  expect(results[0].cant_miss_label).toBe("Can't-miss condition")
})
