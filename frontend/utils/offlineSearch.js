// Offline symptom search: the tree-library ranking of POST /search/by-symptoms,
// run in the browser on the downloaded offline bundle (GET /offline/bundle).
//
// A line-by-line port of backend/services/symptom_search.py (normalize_text,
// expand_synonyms, calculate_match_score_optimized, apply_filters,
// rank_diagnoses without AI) and complaint_matching.py (split_negated,
// match_terms). Synonyms, negation cues and exceptions come from the bundle,
// so they stay the server's. Parity with the server is tested against one
// shared fixture (__tests__/fixtures/offline-search-parity.json) by both
// backend/tests/test_offline_bundle.py and __tests__/offlineSearch.test.js.
//
// Offline search uses typed symptoms, age, sex and family only: no AI
// suggestions, no vital-sign terms and no chart history.
//
// CommonJS so jest can load it without a Babel config (see __tests__).

const escape = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

// symptom_search.normalize_text
function normalizeText(text) {
  return String(text).toLowerCase().replace(/[^\p{L}\p{N}_\s]/gu, ' ').replace(/\s+/g, ' ').trim()
}

// complaint_matching.normalize
function normalizeComplaint(text) {
  return String(text || '').toLowerCase()
    .replace(/[-/]/g, ' ')
    .replace(/\b(radiates|radiation|radiating|radiate)\b/g, 'radiating')
    .replace(/\bon exertion\b/g, 'with exertion')
    .replace(/\b(the|a|an|left|right)\b/g, ' ')
    .replace(/[^a-z0-9 ]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

const CLAUSE_BREAK = /[.;!?\n]|\bbut\b|\bhowever\b|\balthough\b|\bexcept\b/i

function negationFinder(search) {
  const cues = new RegExp(`\\b(${search.negation_cues.map(escape).join('|')})\\b`, 'g')
  const exceptions = new RegExp(`\\b(${search.negation_exceptions.map(escape).join('|')})\\b`, 'g')
  // First cue that does not start a symptom phrase such as "no appetite".
  return (text) => {
    const starts = new Set([...text.matchAll(exceptions)].map((m) => m.index))
    return [...text.matchAll(cues)].find((m) => !starts.has(m.index)) || null
  }
}

const STRIP = ' ,;:-\t'
function strip(s) {
  let a = 0
  let b = s.length
  while (a < b && STRIP.includes(s[a])) a += 1
  while (b > a && STRIP.includes(s[b - 1])) b -= 1
  return s.slice(a, b)
}

// complaint_matching.split_negated -> [affirmed text, negated terms]
function splitNegated(text, findNegation) {
  const kept = []
  const dropped = []
  for (const clause of String(text || '').split(CLAUSE_BREAK)) {
    const cue = findNegation(clause.toLowerCase())
    const head = strip(cue ? clause.slice(0, cue.index) : clause)
    if (head) kept.push(head)
    const term = cue ? strip(clause.slice(cue.index + cue[0].length)) : ''
    if (term) dropped.push(term)
  }
  return [kept.join('; '), dropped]
}

// complaint_matching.match_terms (matched terms only)
function matchTerms(complaint, terms, findNegation) {
  if (!complaint || !terms || !terms.length) return []
  const clauses = complaint.split(CLAUSE_BREAK).map(normalizeComplaint)
  const matched = []
  for (const term of terms) {
    const pattern = new RegExp(`(?<![a-z0-9])${escape(normalizeComplaint(term))}(?![a-z0-9])`, 'g')
    let found = false
    for (const clause of clauses) {
      for (const m of clause.matchAll(pattern)) {
        if (!findNegation(clause.slice(0, m.index))) found = true
      }
    }
    if (found) matched.push(term)
  }
  return matched
}

// symptom_search.expand_synonyms
function expandSynonyms(symptoms, synonyms) {
  const expanded = [...symptoms]
  const seen = new Set(symptoms.map((s) => s.toLowerCase()))
  for (const symptom of symptoms) {
    const text = ` ${normalizeText(symptom)} `
    for (const [phrase, list] of Object.entries(synonyms || {})) {
      if (text.includes(` ${phrase} `)) {
        for (const synonym of list) {
          if (!seen.has(synonym)) {
            expanded.push(synonym)
            seen.add(synonym)
          }
        }
      }
    }
  }
  return expanded
}

const words = (s) => s.split(/\s+/).filter(Boolean)

// symptom_search.calculate_match_score_optimized -> [score, matched presentations]
function matchScore(normalizedSymptoms, presentations, rule) {
  let score = 0
  const matched = []
  presentations.forEach((original) => {
    const presentation = normalizeText(original)
    const presentationWords = words(presentation)
    const presentationSet = new Set(presentationWords)
    let presentationMatched = false
    for (const symptom of normalizedSymptoms) {
      if (presentation.includes(symptom)) {
        score += 5
        presentationMatched = true
        continue
      }
      const symptomWords = words(symptom)
      const overlap = [...new Set(symptomWords)].filter((w) => presentationSet.has(w)).length
      if (symptomWords.length > 1) {
        const first = symptomWords[0]
        if (presentationSet.has(first) || presentationWords.some((pw) => pw.includes(first))) {
          if (overlap >= 2) {
            score += overlap
            presentationMatched = true
          }
        }
      } else if (overlap) {
        score += overlap
        presentationMatched = true
      }
    }
    if (presentationMatched) matched.push(original)
  })
  if (rule && rule.sensitivity !== null && rule.sensitivity !== undefined) {
    const sensitivity = parseFloat(rule.sensitivity)
    if (!Number.isNaN(sensitivity)) score *= 1 + (sensitivity - 0.5) * 0.2
  }
  return [score, matched]
}

const PEDIATRIC = ['PEDS-', 'PEDIATRIC', 'CROUP', 'BRONCHIOLITIS', 'DEVELOPMENTAL DELAY', 'AUTISM', 'WELL-CHILD',
  'FEBRILE SEIZURE', 'HAND FOOT MOUTH']
const GERIATRIC = ['GER-', 'GERIATRIC', 'SARCOPENIA', 'FRAILTY', 'DELIRIUM', 'POLYPHARMACY', 'FALLS RISK',
  'PRESSURE ULCER']
const MALE_ONLY = ['PROSTAT', 'TESTIC', 'PENILE', 'ERECTILE', 'EPIDIDYM', 'ORCHITIS', 'SPERMAT']
const FEMALE_ONLY = ['PREGNAN', 'OVARIAN', 'MENSTRUAL', 'CERVIC', 'UTERIN', 'VAGINAL', 'ENDOMETRIO', 'MENOPAUSE',
  'DYSMENORRHEA', 'AMENORRHEA', 'MENORRHAGIA', 'ECTOPIC', 'PLACENTA', 'OVARY', 'VULVO', 'PCOS', 'POLYCYSTIC OVARY']

// symptom_search.apply_filters
function applyFilters(rules, age, sex) {
  let normalizedSex = null
  if (sex) {
    const s = String(sex).toUpperCase()
    if (s === 'M' || s === 'MALE') normalizedSex = 'male'
    else if (s === 'F' || s === 'FEMALE') normalizedSex = 'female'
  }
  return rules.filter((rule) => {
    const id = String(rule.id || '').toUpperCase()
    const label = String(rule.label || '').toUpperCase()
    const family = String(rule.family || '').toUpperCase()
    const has = (list) => list.some((k) => id.includes(k) || label.includes(k))
    if (age !== null && age !== undefined) {
      if (rule.age_min !== null && rule.age_min !== undefined && age < rule.age_min) return false
      if (rule.age_max !== null && rule.age_max !== undefined && age > rule.age_max) return false
      if (age >= 18 && (family === 'PEDIATRICS' || has(PEDIATRIC))) return false
      if (age < 65 && (family === 'GERIATRICS' || has(GERIATRIC))) return false
    }
    if (rule.applies_to && normalizedSex && String(rule.applies_to).toLowerCase() !== normalizedSex) return false
    if (normalizedSex === 'female' && has(MALE_ONLY)) return false
    if (normalizedSex === 'male' && (family === 'OBSTETRICS GYNECOLOGY' || family === 'OBGYN' || has(FEMALE_ONLY))) {
      return false
    }
    return true
  })
}

const round2 = (x) => Number(x.toFixed(2))

// symptom_search.rank_diagnoses (allow_ai=False) on the bundle.
// -> { results, negated_terms, total_matches }
function rankOffline(bundle, symptoms, { age = null, sex = null, family = null, limit } = {}) {
  const search = bundle.search
  const findNegation = negationFinder(search)
  const max = limit === undefined ? search.result_limit : limit
  const complaintText = symptoms.join('; ')
  const affirmed = []
  const negatedTerms = []
  for (const symptom of symptoms) {
    const [kept, dropped] = splitNegated(symptom, findNegation)
    if (kept) affirmed.push(kept)
    negatedTerms.push(...dropped)
  }
  const normalizedInput = expandSynonyms(affirmed, search.synonyms).map(normalizeText)
  const rules = family ? search.rules.filter((r) => r.family === family) : search.rules

  const results = []
  for (const rule of applyFilters(rules, age, sex)) {
    const presentations = (rule.presentations || []).filter((p) => typeof p === 'string')
    const emergent = String(rule.urgency || '').toLowerCase() === 'emergent'
    const matchedTerms = emergent ? matchTerms(complaintText, rule.complaint_terms || [], findNegation) : []
    if (!presentations.length && !matchedTerms.length) continue
    const [score, matched] = presentations.length ? matchScore(normalizedInput, presentations, rule) : [0, []]
    const cantMiss = emergent && (score > 0 || matchedTerms.length > 0)
    for (const term of matchedTerms) if (!matched.includes(term)) matched.push(term)
    if (score > 0 || cantMiss) {
      results.push({
        rule_id: rule.id, label: rule.label, family: rule.family, match_score: round2(score),
        matched_presentations: matched, all_presentations: presentations, icd10: rule.icd10 || [], snomed: [],
        sensitivity: rule.sensitivity, specificity: null, clinical_pearls: null, management: null, tests: null,
        referrals: null, has_tree: true, ai_suggested: false, cant_miss: cantMiss,
        cant_miss_label: cantMiss ? "Can't-miss condition" : null, urgency: rule.urgency || null,
        review_status: rule.review_status, review_status_label: rule.review_status_label, offline: true,
      })
    }
  }
  results.sort((a, b) => b.match_score - a.match_score) // stable, like Python's sort
  const top = max ? results.slice(0, max) : results
  const rest = max ? results.slice(max).filter((r) => r.cant_miss) : []
  return { results: top.concat(rest), negated_terms: negatedTerms, total_matches: results.length }
}

module.exports = {
  rankOffline, normalizeText, normalizeComplaint, splitNegated, matchTerms, expandSynonyms, matchScore, applyFilters,
  negationFinder,
}
