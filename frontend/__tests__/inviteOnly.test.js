// Accounts are invite-only: no page offers self-registration.
const fs = require('fs')
const path = require('path')

const read = (...p) => fs.readFileSync(path.join(__dirname, '..', ...p), 'utf8')

test('the register page explains invitations and posts nothing', () => {
  const page = read('app', 'register', 'page.jsx')
  expect(page).toContain('Accounts are by invitation')
  expect(page).not.toMatch(/apiFetch|fetch\(/)
})

test('login and account pages do not offer to create an account', () => {
  expect(read('app', 'login', 'page.jsx')).not.toContain('Create one')
  const account = read('pages', 'account.js')
  expect(account).not.toMatch(/authRegister|handleRegister/)
  expect(account).toContain('Accounts are by invitation')
})

test('an invite setup link titles the password page as account setup', () => {
  expect(read('app', 'reset-password', 'page.jsx')).toContain('Set up your RealDiag account')
})
