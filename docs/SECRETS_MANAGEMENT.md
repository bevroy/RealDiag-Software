# Secrets Management Strategy for RealDiag-Software

## Overview
This document outlines the strategy for managing sensitive credentials and secrets in production.

## Secret Storage Solutions

### Recommended: Cloud Provider Secret Management

#### AWS Secrets Manager
```bash
# Store secret
aws secretsmanager create-secret \
  --name realdiag/prod/jwt-secret \
  --secret-string "your-jwt-secret-here"

# Retrieve in application
aws secretsmanager get-secret-value \
  --secret-id realdiag/prod/jwt-secret \
  --query SecretString \
  --output text
```

#### Azure Key Vault
```bash
# Store secret
az keyvault secret set \
  --vault-name realdiag-prod-vault \
  --name jwt-secret \
  --value "your-jwt-secret-here"

# Retrieve in application
az keyvault secret show \
  --vault-name realdiag-prod-vault \
  --name jwt-secret \
  --query value \
  --output tsv
```

#### Google Cloud Secret Manager
```bash
# Store secret
echo -n "your-jwt-secret-here" | \
  gcloud secrets create jwt-secret \
  --data-file=-

# Retrieve in application
gcloud secrets versions access latest \
  --secret="jwt-secret"
```

### Kubernetes Secrets

```bash
# Create secret from literal
kubectl create secret generic realdiag-secrets \
  --from-literal=JWT_SECRET_KEY="your-jwt-secret" \
  --from-literal=DATABASE_PASSWORD="your-db-password" \
  --namespace=production

# Create secret from .env file
kubectl create secret generic realdiag-env \
  --from-env-file=.env.production \
  --namespace=production
```

## Environment-Specific Configuration

### Development (.env.local)
- Use `.env.local` for local development
- Generate test secrets locally
- Never commit to git

### Staging (.env.staging)
- Separate secrets from production
- Use staging-specific database
- Stored in CI/CD pipeline secrets

### Production (.env.production)
- **NEVER** commit to git
- Store in secure vault
- Injected at runtime via:
  - Kubernetes secrets
  - Cloud provider secret manager
  - CI/CD pipeline variables

## Secret Rotation Schedule

| Secret Type | Rotation Frequency | Method |
|------------|-------------------|---------|
| JWT Secret Key | Every 90 days | Generate new, update vault, rolling restart |
| Database Password | Every 90 days | Update in database + vault, restart apps |
| API Keys | Every 90 days | Regenerate with provider |
| TLS Certificates | Every 90 days | Automated via Let's Encrypt |
| Backup Encryption Key | Every 180 days | Generate new, re-encrypt backups |

## Accessing Secrets in Code

### Backend (Python/FastAPI)

```python
import os
from typing import Optional

class Config:
    """Application configuration loaded from environment variables."""
    
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD")
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    
    def __init__(self):
        # Validate required secrets are present
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY environment variable required")
        if not self.DATABASE_PASSWORD:
            raise ValueError("DATABASE_PASSWORD environment variable required")

config = Config()
```

### Frontend (Next.js)

```javascript
// Only expose non-sensitive config to frontend
// Secrets should NEVER be in frontend code

// runtime-config.js (injected at build time)
window.__RUNTIME_CONFIG = {
  NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE,
  NEXT_PUBLIC_SENTRY_DSN: process.env.NEXT_PUBLIC_SENTRY_DSN,
  // Never expose: JWT_SECRET_KEY, DATABASE_PASSWORD, etc.
};
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Set environment variables
  env:
    JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}
    DATABASE_PASSWORD: ${{ secrets.DATABASE_PASSWORD }}
  run: |
    echo "JWT_SECRET_KEY=${JWT_SECRET_KEY}" >> .env.production
    echo "DATABASE_PASSWORD=${DATABASE_PASSWORD}" >> .env.production
```

### GitLab CI
```yaml
variables:
  JWT_SECRET_KEY: ${CI_JWT_SECRET_KEY}
  DATABASE_PASSWORD: ${CI_DATABASE_PASSWORD}
```

## Security Best Practices

### ✅ DO
- Use strong, randomly generated secrets (min 32 characters)
- Store secrets in encrypted vault
- Use different secrets for each environment
- Rotate secrets regularly (90 days)
- Audit secret access logs
- Use principle of least privilege
- Encrypt secrets at rest and in transit

### ❌ DON'T
- Commit secrets to git (even private repos)
- Share secrets via email/chat
- Hardcode secrets in code
- Use weak or predictable secrets
- Reuse secrets across environments
- Log sensitive values
- Store secrets in frontend code

## Emergency Secret Rotation

If a secret is compromised:

1. **Immediate Actions**
   ```bash
   # Generate new secret
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Update in vault
   kubectl create secret generic realdiag-secrets \
     --from-literal=JWT_SECRET_KEY="NEW_SECRET" \
     --dry-run=client -o yaml | kubectl apply -f -
   
   # Rolling restart to pickup new secret
   kubectl rollout restart deployment/realdiag-backend
   ```

2. **Revoke Compromised Secret**
   - Invalidate all sessions using old secret
   - Force re-authentication of users
   - Review access logs for unauthorized usage

3. **Post-Incident**
   - Document incident
   - Review how secret was compromised
   - Improve security controls
   - Notify affected users if necessary

## Validation Checklist

Before production deployment:

- [ ] All secrets generated with cryptographically secure methods
- [ ] `.env` files added to `.gitignore`
- [ ] No secrets committed to git history
- [ ] Secrets stored in secure vault
- [ ] Different secrets for prod/staging/dev
- [ ] Secret rotation schedule documented
- [ ] Emergency rotation procedure tested
- [ ] Team trained on secret management
- [ ] Access to secrets audited and logged
- [ ] Monitoring alerts for failed secret access

## Tools

- **Secret Scanning**: 
  - git-secrets
  - truffleHog
  - GitHub secret scanning

- **Vault Management**:
  - HashiCorp Vault
  - AWS Secrets Manager
  - Azure Key Vault
  - Google Secret Manager

- **Encryption**:
  - SOPS (Secrets OPerationS)
  - Mozilla SOPS
  - git-crypt

## Support

For questions about secrets management:
- Security Team: security@realdiag.com
- DevOps Team: devops@realdiag.com
- On-call: Use PagerDuty for emergencies
