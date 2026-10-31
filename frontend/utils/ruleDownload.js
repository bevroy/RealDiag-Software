// "Download All Rules" for offline use: one request to GET /rules/all, then
// each rule is saved locally. The result says what actually happened, so the
// page can report success only when every rule was saved.
//
// CommonJS so jest can load it without a Babel config (see __tests__).

async function downloadRules({ fetchRules, saveRule, onProgress }) {
  let response
  try {
    response = await fetchRules()
  } catch (error) {
    return { success: false, downloaded: 0, total: 0, error: `Rule download failed: ${error.message}` }
  }
  if (!response || !response.ok) {
    const status = response ? response.status : 'no response'
    return { success: false, downloaded: 0, total: 0, error: `Rule download failed (HTTP ${status}).` }
  }
  const body = await response.json()
  const rules = Array.isArray(body && body.rules) ? body.rules : []
  const total = rules.length
  if (total === 0) {
    return { success: false, downloaded: 0, total: 0, error: 'The server returned no rules.' }
  }
  let downloaded = 0
  const failed = []
  for (const rule of rules) {
    try {
      await saveRule(rule)
      downloaded += 1
    } catch (error) {
      failed.push(rule.id)
    }
    if (onProgress) {
      onProgress({ downloaded, total, current: rule.id, percentage: Math.round(((downloaded + failed.length) / total) * 100) })
    }
  }
  const success = downloaded === total
  return {
    success,
    downloaded,
    total,
    version: body.version || null,
    error: success ? null : `${failed.length} of ${total} rules could not be saved on this device.`,
  }
}

function downloadMessage(result) {
  if (result.success) {
    return `Downloaded ${result.downloaded} rules${result.version ? ` (library version ${result.version})` : ''}.`
  }
  return result.error || 'Rule download failed.'
}

module.exports = { downloadRules, downloadMessage }
