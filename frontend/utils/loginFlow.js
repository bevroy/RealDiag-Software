// What the sign-in page shows after POST /users/login.
//
// Two-factor authentication is required for every account (backend
// access_policy.REQUIRE_MFA): an enrolled account gets { mfa_required,
// mfa_token } and must enter a code (POST /mfa/login-verify); an account not
// enrolled yet gets { mfa_setup_required, user } and a session that can only
// enroll (POST /mfa/enroll, then /mfa/verify, which replaces the session).
//
// CommonJS so jest can load it without a Babel config (see __tests__).

function loginNextStep(data) {
  if (data && data.mfa_required && data.mfa_token) return 'code'
  if (data && data.mfa_setup_required) return 'setup'
  return 'done'
}

// Body for POST /mfa/login-verify: a 6-digit code, or a backup code.
function mfaVerifyBody(mfaToken, code, useBackupCode) {
  const value = String(code || '').replace(/\s+/g, '')
  return useBackupCode ? { mfa_token: mfaToken, backup_code: value } : { mfa_token: mfaToken, token: value }
}

module.exports = { loginNextStep, mfaVerifyBody }
