const fs = require('fs')
const path = require('path')
const { loginNextStep, mfaVerifyBody } = require('../utils/loginFlow')

test('sign-in goes to the code step, the setup step, or straight in', () => {
  expect(loginNextStep({ mfa_required: true, mfa_token: 't' })).toBe('code')
  expect(loginNextStep({ mfa_setup_required: true, user: { email: 'a' } })).toBe('setup')
  expect(loginNextStep({ user: { email: 'a' } })).toBe('done')
})

test('the code step sends a TOTP code or a backup code', () => {
  expect(mfaVerifyBody('t', '123 456', false)).toEqual({ mfa_token: 't', token: '123456' })
  expect(mfaVerifyBody('t', 'abcd-efgh', true)).toEqual({ mfa_token: 't', backup_code: 'abcd-efgh' })
})

test('the login page handles both MFA steps and only stores the user after MFA', () => {
  const page = fs.readFileSync(path.join(__dirname, '..', 'app', 'login', 'page.jsx'), 'utf8')
  expect(page).toMatch(/\/mfa\/login-verify/)
  expect(page).toMatch(/<MFASetup/)
  expect(page).toMatch(/loginNextStep\(data\)/)
})
