# Security Implementation Guide

This document outlines the security hardening measures implemented in Secure CI/CD Pipeline Guardian.

## 1. Secret Management

### ✅ Environment Variables Only
- **Never** store secrets in code
- Use `.env` file (not committed to git)
- Example: `.env.example` shows required variables

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost/scg
JWT_SECRET=your-secret-key-here
GITHUB_CLIENT_ID=xxx
GITHUB_CLIENT_SECRET=xxx
```

### ✅ Secrets Detection
The CLI itself detects hardcoded secrets:
- AWS Access Keys
- GitHub Tokens
- Database URLs
- API Keys with high entropy

---

## 2. Authentication & Authorization

### ✅ OAuth2 GitHub Integration
```python
# OAuth flow
GET /login → GitHub OAuth → Token Exchange → Redirect
```

### ✅ JWT Tokens
- **Expiration**: 15 minutes
- **Refresh Token**: 7 days (stored securely)
- **Algorithm**: HS256
- **Claims**: user_id, permissions, exp

### ✅ RBAC (Role-Based Access Control)
```python
ROLES = {
    "owner": ["read", "write", "admin"],
    "viewer": ["read"],
    "editor": ["read", "write"]
}
```

---

## 3. Rate Limiting

### ✅ API Rate Limits
```python
# Per IP address
/api/scan: 100 requests/hour
/api/projects: 1000 requests/hour
/auth/login: 5 failed attempts = 15min lockout
```

### ✅ Implementation
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/scan")
@limiter.limit("100/hour")
async def receive_scan(request: ScanRequest):
    ...
```

---

## 4. Data Protection

### ✅ Encryption at Rest
- Database: TLS for PostgreSQL connections
- Secrets: Encrypted with Fernet
- Reports: JSON with sensitive data redacted

### ✅ Encryption in Transit
- **HTTPS Only** - All API endpoints
- **TLS 1.2+** - Minimum version
- **HSTS** - Strict-Transport-Security header

### ✅ Data Sensitivity Levels
```
Level 1: Public findings
Level 2: Detailed code context (restricted to owner)
Level 3: Raw tokens/secrets (never stored, logged only as hashes)
```

---

## 5. Audit Logging

### ✅ Events Logged
```json
{
  "timestamp": "2024-01-14T10:30:00Z",
  "event": "scan_received",
  "actor": "user:123",
  "resource": "project:api-service",
  "status": "FAIL",
  "details": {
    "critical_count": 1,
    "triggered_by": "push to main"
  }
}
```

### ✅ Log Retention
- 90 days: Detailed logs
- 1 year: Aggregated statistics
- Never: Raw secret values

---

## 6. Input Validation

### ✅ Request Validation
```python
class ScanRequest(BaseModel):
    project: str = Field(..., min_length=1, max_length=100)
    commit: str = Field(..., regex=r"^[a-f0-9]{40}$")
    results: List[Finding] = Field(..., max_items=1000)
```

### ✅ File Path Validation
```python
# Prevent path traversal
safe_path = Path(user_input).resolve()
if not str(safe_path).startswith(allowed_dir):
    raise ValueError("Path traversal attempt")
```

---

## 7. Dependency Security

### ✅ Third-Party Libraries
- **Minimal dependencies** - Only FastAPI, Pydantic, Click
- **Regular updates** - Dependabot alerts
- **License compliance** - All MIT/Apache 2.0

### ✅ Supply Chain Protection
```bash
# Verify package integrity
pip install --require-hashes -r requirements.txt
```

---

## 8. Code Security

### ✅ Static Analysis
- **Type hints** - Mypy checking
- **Linting** - Pylint, Flake8
- **Security scanning** - Bandit for dangerous patterns

### ✅ No Dangerous Patterns
- ❌ eval() / exec()
- ❌ Pickle untrusted data
- ❌ SQL injection vulnerable queries
- ❌ CORS allow-all

---

## 9. Container Security

### ✅ Docker Best Practices
```dockerfile
FROM python:3.10-slim

# Non-root user
RUN groupadd -r scg && useradd -r -g scg scg

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

USER scg

CMD ["python", "-m", "uvicorn", "app.main:app"]
```

---

## 10. GDPR Compliance

### ✅ Data Handling
- **Consent**: Users consent to scanning
- **Retention**: Auto-delete after 90 days (configurable)
- **Export**: Users can export all personal data
- **Deletion**: Right to be forgotten implemented

---

## Security Testing

### ✅ Unit Tests
```bash
pytest tests/ -v
```

### ✅ Security Tests
```bash
# Check for hardcoded secrets
bandit -r .

# Type checking
mypy app/

# Dependency check
safety check
```

### ✅ Penetration Testing Scope
- SQL injection
- XSS attacks
- CSRF protection
- Rate limiting bypass
- Authentication bypass

---

## Incident Response

### ✅ If Secret is Leaked
1. Immediately revoke the secret
2. Rotate all credentials
3. Notify users
4. Review audit logs for unauthorized access
5. Patch the code

### ✅ If Vulnerability Found
1. Assess severity
2. Create security patch
3. Release immediately
4. Publish security advisory

---

## Security Headers

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## Checklist: Before Production

- [ ] All secrets in environment variables
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Audit logging enabled
- [ ] Database encrypted
- [ ] Input validation on all endpoints
- [ ] Authentication/Authorization working
- [ ] Dependencies up to date
- [ ] Security tests passing
- [ ] Monitoring/alerting configured

---

## References

- [OWASP Top 10](https://owasp.org/Top10/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework/)
- [GDPR Compliance](https://gdpr-info.eu/)

---

**For security questions, contact: security@example.com**
