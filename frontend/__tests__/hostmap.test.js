const { mapPreviewHost } = require('../scripts/test-hostmap')

test('preview host maps -3000 -> -8000', () => {
  expect(mapPreviewHost('silver-space-12345-3000.app.github.dev', 'https:'))
    .toBe('https://silver-space-12345-8000.app.github.dev')
})

test('localhost fallback uses :8000', () => {
  expect(mapPreviewHost('localhost', 'http:')).toBe('http://localhost:8000')
})

test('regular host fallback uses :8000', () => {
  expect(mapPreviewHost('example.com', 'https:')).toBe('https://example.com:8000')
})
