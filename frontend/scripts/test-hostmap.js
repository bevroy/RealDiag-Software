// Simple test harness for the preview hostname -> API host mapping heuristic.
// Run with: node frontend/scripts/test-hostmap.js

function mapPreviewHost(hostname, protocol = 'https:'){
  const previewMatch = hostname.match(/^(.+)-3000(\..+)$/)
  if (previewMatch){
    const apiHost = `${previewMatch[1]}-8000${previewMatch[2]}`
    return `${protocol}//${apiHost}`
  }
  return `${protocol}//${hostname}:8000`
}

function expectEqual(a,b,msg){
  if (a !== b){
    console.error(`FAIL: ${msg}\n  expected: ${b}\n  got:      ${a}`)
    process.exitCode = 1
    return
  }
  console.log(`ok: ${msg}`)
}

// Test cases
expectEqual(
  mapPreviewHost('silver-space-12345-3000.app.github.dev','https:'),
  'https://silver-space-12345-8000.app.github.dev',
  'preview host with -3000 should map to -8000'
)

expectEqual(
  mapPreviewHost('localhost','http:'),
  'http://localhost:8000',
  'localhost fallback'
)

expectEqual(
  mapPreviewHost('example.com','https:'),
  'https://example.com:8000',
  'normal host fallback'
)

if (process.exitCode === 0) console.log('ALL TESTS PASSED')

module.exports = { mapPreviewHost }
