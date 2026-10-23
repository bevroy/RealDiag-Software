const fs = require('fs')
const path = require('path')
const { apiFetch, apiUrl, getApiBase, DEFAULT_API_BASE } = require('../utils/apiClient')

describe('apiClient', () => {
  let calls

  beforeEach(() => {
    calls = []
    global.fetch = jest.fn((url, init) => {
      calls.push({ url, init })
      return Promise.resolve({ ok: true })
    })
    delete process.env.NEXT_PUBLIC_API_BASE
    global.window = undefined
    global.document = undefined
  })

  afterEach(() => {
    delete global.fetch
    delete global.window
    delete global.document
  })

  test('defaults to the production API base', () => {
    expect(getApiBase()).toBe(DEFAULT_API_BASE)
    expect(apiUrl('/diagnostic/trees')).toBe('https://api.realdiag.com/diagnostic/trees')
  })

  test('runtime config wins over the build-time env var', () => {
    process.env.NEXT_PUBLIC_API_BASE = 'https://env.example'
    expect(getApiBase()).toBe('https://env.example')
    global.window = { __RUNTIME_CONFIG: { NEXT_PUBLIC_API_BASE: 'https://runtime.example/' } }
    expect(apiUrl('diagnostic/trees')).toBe('https://runtime.example/diagnostic/trees')
  })

  test('absolute URLs are passed through unchanged', () => {
    expect(apiUrl('https://other.example/x')).toBe('https://other.example/x')
  })

  test('every request sends the login cookie, even if the caller asks otherwise', async () => {
    await apiFetch('/diagnostic/trees')
    await apiFetch('/diagnostic/trees', { credentials: 'omit' })
    expect(calls.map((c) => c.init.credentials)).toEqual(['include', 'include'])
    expect(calls[0].init.method).toBe('GET')
  })

  test('JSON bodies get a content type; CSRF token is added to writes only', async () => {
    global.document = { cookie: 'a=b; csrf_token=tok123' }
    await apiFetch('/diagnostic/evaluate/X', { method: 'post', body: JSON.stringify({ age: 40 }) })
    await apiFetch('/diagnostic/trees')
    expect(calls[0].init.method).toBe('POST')
    expect(calls[0].init.headers).toEqual({ 'Content-Type': 'application/json', 'X-CSRF-Token': 'tok123' })
    expect(calls[1].init.headers).toEqual({})
  })

  test('a caller-supplied content type is kept', async () => {
    await apiFetch('/x', { method: 'POST', body: 'a=1', headers: { 'content-type': 'text/plain' } })
    expect(calls[0].init.headers).toEqual({ 'content-type': 'text/plain' })
  })
})

// Guard: a raw fetch() to the RealDiag API without credentials is what broke
// /diagnose, the tree counts and Patient History. Every API call must go through
// apiFetch/authenticatedFetch, or pass credentials: 'include' (SMART pages) or an
// Authorization header (admin review) itself.
describe('no page calls the API without credentials', () => {
  const ROOT = path.join(__dirname, '..')
  const DIRS = ['pages', 'app', 'components', 'utils']
  const API_REF = /apiBase|API_BASE|getApiBase\(\)|api\.realdiag\.com|onrender\.com/

  function sourceFiles(dir) {
    return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
      const full = path.join(dir, entry.name)
      if (entry.isDirectory()) return sourceFiles(full)
      return /\.(js|jsx|ts|tsx)$/.test(entry.name) ? [full] : []
    })
  }

  // Code samples rendered for readers ({`...`} blocks on the Integration page)
  // are text, not calls.
  function stripCodeSamples(src) {
    return src.replace(/\{`[\s\S]*?`\}/g, '')
  }

  test('raw fetch calls to the API send credentials', () => {
    const offenders = []
    for (const dir of DIRS) {
      for (const file of sourceFiles(path.join(ROOT, dir))) {
        if (file.endsWith(path.join('utils', 'apiClient.js'))) continue
        const src = stripCodeSamples(fs.readFileSync(file, 'utf8'))
        const re = /(^|[^A-Za-z.])fetch\(/g
        let m
        while ((m = re.exec(src))) {
          const call = src.slice(m.index, m.index + 400)
          const target = call.slice(0, call.indexOf(',') === -1 ? 120 : call.indexOf(','))
          if (!API_REF.test(target)) continue
          if (/credentials:\s*'include'|Authorization/.test(call)) continue
          const line = src.slice(0, m.index).split('\n').length
          offenders.push(`${path.relative(ROOT, file)}:${line}`)
        }
      }
    }
    expect(offenders).toEqual([])
  })

  test('the guard catches the pattern that broke /diagnose', () => {
    const broken = "const r = await fetch(`${apiBase}/diagnostic/trees`)"
    const call = broken.slice(broken.indexOf('fetch('))
    expect(API_REF.test(call)).toBe(true)
    expect(/credentials:\s*'include'|Authorization/.test(call)).toBe(false)
  })
})
