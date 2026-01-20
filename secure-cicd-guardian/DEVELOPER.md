# Developer Guide

Building and extending **Secure CI/CD Pipeline Guardian**

---

## Project Structure

```
secure-cicd-guardian/
├── cli/                           # Python CLI Scanner
│   ├── scg/
│   │   ├── __init__.py           # Package init
│   │   ├── main.py               # CLI entrypoint (Click)
│   │   ├── scanner.py            # Main orchestrator
│   │   ├── secrets.py            # Secret detection (regex + entropy)
│   │   ├── dependencies.py       # Dependency vulnerability checking
│   │   └── dockerfile.py         # Dockerfile security rules
│   └── setup.py                  # Package configuration
│
├── backend/                       # FastAPI Backend
│   ├── app/
│   │   ├── main.py              # API application + routes
│   │   ├── core/
│   │   │   └── decision_engine.py # PASS/FAIL logic
│   │   └── models/
│   │       └── scan.py           # Pydantic models
│   ├── requirements.txt
│   └── Dockerfile
│
├── dashboard/                     # React Frontend (placeholder)
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── api.ts
│   └── package.json
│
├── .github/workflows/
│   └── security.yml             # GitHub Actions workflow
│
├── docker-compose.yml           # Local development
├── README.md                    # Feature overview
├── INSTALL.md                   # Setup instructions
├── SECURITY.md                  # Security hardening
└── DEVELOPER.md                 # This file
```

---

## Adding New Security Checks

### 1. Secret Pattern Detection

Add to `cli/scg/secrets.py`:

```python
PATTERNS = {
    "YOUR_SERVICE_TOKEN": {
        "pattern": r"your_pattern_here",
        "severity": "CRITICAL"
    }
}
```

Example: Detect Slack tokens

```python
"SLACK_BOT_TOKEN": {
    "pattern": r"xoxb-[0-9]{10,13}-[0-9a-zA-Z]{24,32}",
    "severity": "CRITICAL"
}
```

### 2. Dependency Vulnerability

Add to `cli/scg/dependencies.py`:

```python
CVE_DATABASE = {
    "package_name": {
        "vulnerable_versions": [("1.0.0", "2.5.0")],
        "severity": "HIGH",
        "description": "Description of vulnerability"
    }
}
```

### 3. Docker Security Rule

Add to `cli/scg/dockerfile.py`:

```python
RULES = {
    "YOUR_RULE": {
        "pattern": r"your_regex",
        "severity": "MEDIUM",
        "description": "Rule description",
        "solution": "How to fix"
    }
}
```

Example: Detect `WORKDIR /` (bad practice)

```python
"WORKDIR_ROOT": {
    "pattern": r"WORKDIR\s+/$",
    "severity": "HIGH",
    "description": "Using root directory as WORKDIR",
    "solution": "Use a specific application directory like /app"
}
```

---

## Modifying Decision Logic

Edit `backend/app/core/decision_engine.py`:

```python
FAIL_POLICY = {
    "critical_threshold": 1,    # Adjust here
    "high_threshold": 3,         # Adjust here
    "medium_threshold": 10,      # Add custom thresholds
}
```

Example: Stricter policy

```python
# No CRITICAL allowed, max 2 HIGH
FAIL_POLICY = {
    "critical_threshold": 0,
    "high_threshold": 2,
}
```

---

## Adding API Endpoints

Edit `backend/app/main.py`:

```python
@app.get("/api/your-endpoint")
async def your_endpoint():
    """Endpoint description"""
    return {"data": "value"}
```

Example: Get findings by severity

```python
@app.get("/api/findings/{severity}")
async def get_findings_by_severity(severity: str):
    """Get all findings of a specific severity"""
    findings = [
        f for scan in scans_db.values()
        for f in scan["findings"]
        if f["severity"] == severity.upper()
    ]
    return {"severity": severity, "count": len(findings), "findings": findings}
```

---

## Testing

### Unit Tests

```bash
cd cli
python -m pytest tests/ -v
```

### Security Tests

```bash
# Check for hardcoded secrets
bandit -r .

# Type checking
mypy app/

# Dependency vulnerabilities
safety check
```

### Integration Tests

```bash
# Test scanner on real project
scg scan --path /path/to/test/project --output test_report.json

# Test API
curl http://localhost:8000/api/stats
```

---

## Contributing Code

### Code Style

```bash
# Format code
black .

# Lint
flake8 .

# Type check
mypy app/
```

### Commit Messages

```
feat: add new secret pattern for API keys
fix: correct entropy calculation
docs: update installation guide
test: add unit tests for dockerfile checker
```

### Pull Request Process

1. Fork repository
2. Create feature branch: `git checkout -b feat/new-feature`
3. Make changes
4. Add tests
5. Run security checks
6. Create pull request

---

## Performance Optimization

### Scanner Speed

Current scan speed: ~5-30 seconds per project

Optimization ideas:
- Parallel file processing
- Caching results
- Skip binary files
- Limit file size

### API Performance

- Add database indexes
- Implement caching (Redis)
- Paginate large result sets

---

## Database Schema (Future)

When migrating to PostgreSQL:

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    repo_url VARCHAR(255),
    owner_id VARCHAR(255),
    created_at TIMESTAMP
);

CREATE TABLE scans (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    status VARCHAR(50),
    timestamp TIMESTAMP,
    critical INT, high INT, medium INT, low INT
);

CREATE TABLE findings (
    id UUID PRIMARY KEY,
    scan_id UUID REFERENCES scans(id),
    type VARCHAR(50),
    severity VARCHAR(50),
    file VARCHAR(255),
    line INT,
    rule VARCHAR(255),
    message TEXT
);

CREATE INDEX idx_scan_project ON scans(project_id);
CREATE INDEX idx_finding_severity ON findings(severity);
```

---

## Extending to Other Languages

### JavaScript/TypeScript

```python
# In cli/scg/dependencies.py
def check_npm_packages(package_json_content: str):
    """Check npm package-lock.json for vulnerabilities"""
    import json
    data = json.loads(package_json_content)
    # Check against CVE database
```

### Go

```python
def check_go_modules(go_mod_content: str):
    """Check go.mod for vulnerable dependencies"""
    # Parse and check against database
```

---

## Deployment to Production

### Docker Image

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY cli /app/cli
COPY backend /app/backend
RUN pip install -e cli/
RUN pip install -r backend/requirements.txt
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scg-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: scg-api
  template:
    metadata:
      labels:
        app: scg-api
    spec:
      containers:
      - name: api
        image: scg-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: scg-secrets
              key: db-url
```

---

## Debugging

### Enable Verbose Logging

```python
# In scanner.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### API Debug Mode

```python
# In backend/app/main.py
app = FastAPI(debug=True)
```

### Test Individual Components

```bash
# Test secrets detection only
python -c "
from cli.scg.secrets import SecretDetector
detector = SecretDetector()
findings = detector.scan_file('test.py', 'password=\"secret123\"')
print(findings)
"
```

---

## Resources

- [Click Documentation](https://click.palletsprojects.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Regular Expressions](https://regex101.com/)
- [OWASP Top 10](https://owasp.org/Top10/)

---

## Common Issues & Solutions

### Issue: Scanner finds false positives

**Solution:**
```python
# In secrets.py
SKIP_PATTERNS = [
    "example_password_for_docs",
    "test_key_in_comments"
]
```

### Issue: API is slow

**Solution:**
- Add caching
- Use database indexes
- Profile with `py-spy`

### Issue: GitHub Actions workflow failing

**Solution:**
- Check `pip install -e cli/` works in isolation
- Verify Python version compatibility
- Check path handling in CLI

---

## Feature Requests

Have an idea? Open an issue:
- Title: `[FEATURE] Brief description`
- Description: Why you need it, how it would work
- Example: `[FEATURE] Support for GitLab CI pipelines`

---

**Happy coding! 🚀**
