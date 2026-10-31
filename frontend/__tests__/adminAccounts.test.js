// The admin page offers the invite-only account tools and the accounts list.
const fs = require('fs')
const path = require('path')

const page = fs.readFileSync(path.join(__dirname, '..', 'pages', 'admin-review.js'), 'utf8')

test('account tools call the invite, create, MFA reset, deactivation and allowlist endpoints', () => {
  for (const p of ['/admin/users/invite', '/admin/users/create', '/admin/users/reset-mfa', '/admin/users/deactivate',
    '/admin/users/reactivate', '/admin/allowlist', '/admin/allowlist/remove']) {
    expect(page).toContain(`'${p}'`)
  }
})

test('the accounts list shows status and last sign-in', () => {
  expect(page).toContain('/admin/users`')
  expect(page).toMatch(/'Last sign-in'/)
  expect(page).toMatch(/u\.last_login \? new Date\(u\.last_login\)\.toLocaleString\(\) : 'never'/)
})
