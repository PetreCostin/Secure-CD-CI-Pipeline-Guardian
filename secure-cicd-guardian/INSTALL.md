# Installation & Deployment Guide

**Secure CI/CD Pipeline Guardian** - Complete setup instructions

---

## Prerequisites

- Python 3.8+
- Git
- Docker & Docker Compose (optional, for containerized deployment)
- Node.js 16+ (for dashboard)

---

## Part 1: CLI Installation & Testing

### Step 1: Clone Repository

```bash
cd /path/to/secure-cicd-guardian
```

### Step 2: Install CLI

```bash
cd cli
pip install -e .
```

### Step 3: Verify Installation

```bash
scg --help
```

You should see:

```
Usage: scg [OPTIONS] COMMAND [ARGS]...

  Secure CI/CD Pipeline Guardian - DevSecOps Security Scanner

Commands:
  report  View scan report for project
  scan    Run security scan on project
```

### Step 4: Test Scanner on Example Project

```bash
cd ..
scg scan --path . --output report.json
```

**Expected Output:**
```
🔍 Scanning: .

📊 SCAN RESULTS:
  • Critical: 3
  • High: 4
  • Medium: 1
  • Low: 1

🔒 FINDINGS (9 issues):
...

❌ BUILD FAILED: Security issues detected at critical level
```

---

## Part 2: Backend API Setup

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Run Development Server

```bash
python -m uvicorn app.main:app --reload
```

**Expected Output:**
```
Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Step 3: Test API

Open in browser: `http://localhost:8000/docs`

You'll see the interactive Swagger API documentation.

### Step 4: Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get statistics
curl http://localhost:8000/api/stats

# Submit scan results
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "project": "test-app",
    "commit": "a1b2c3d4e5",
    "results": []
  }'
```

---

## Part 3: GitHub Actions Integration

### Step 1: Add Workflow File

The file `.github/workflows/security.yml` is already created.

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Add security scanning"
git push origin main
```

### Step 3: Verify Workflow

Go to your GitHub repo → Actions tab

You should see the "Security Gate" workflow running on every push.

### Step 4: View Results

- Click on the workflow run
- Check the "Run Security Scan" step
- See findings and PASS/FAIL status

---

## Part 4: Docker Deployment (Optional)

### Step 1: Build Docker Image

```bash
docker build -t scg-api backend/
```

### Step 2: Run with Docker Compose

```bash
docker-compose up -d
```

This starts:
- **API** on port 8000
- **PostgreSQL** on port 5432
- **Dashboard** on port 3000

### Step 3: Verify

```bash
curl http://localhost:8000/health
```

---

## Part 5: Advanced Configuration

### Custom Security Policy

```bash
# Get current policy
curl http://localhost:8000/api/policy

# Update policy (fail if any CRITICAL)
curl -X POST http://localhost:8000/api/policy \
  -H "Content-Type: application/json" \
  -d '{"critical_threshold": 0, "high_threshold": 3}'
```

### Integration with CI/CD Systems

#### GitHub Actions ✅ (Implemented)
```yaml
- run: scg scan --fail-on critical
```

#### GitLab CI
```yaml
security:
  script:
    - pip install -e cli/
    - scg scan --output report.json
  artifacts:
    reports:
      sast: report.json
```

#### Jenkins
```groovy
stage('Security Scan') {
  steps {
    sh 'scg scan --fail-on critical'
  }
}
```

---

## Part 6: Dashboard Setup

Dashboard is a React application that displays:
- Projects and scan history
- Security findings by severity
- Scan trends over time

### Step 1: Build Dashboard

```bash
cd dashboard
npm install
npm start
```

### Step 2: Connect to API

Update `.env`:
```
REACT_APP_API_URL=http://localhost:8000
```

### Step 3: Access Dashboard

Open: `http://localhost:3000`

---

## Troubleshooting

### Issue: `scg: command not found`

**Solution:**
```bash
cd cli
pip install -e .
```

### Issue: API Connection Error

**Solution:**
1. Verify API is running: `curl http://localhost:8000/health`
2. Check firewall rules
3. Verify API_URL in dashboard `.env`

### Issue: CLI Not Finding Files

**Solution:**
```bash
# Verbose output
scg scan --path . -v

# Check permissions
ls -la .
```

### Issue: False Positives

**Solution:** Add exceptions in scanner code:
```python
# In secrets.py, add to SKIP_PATTERNS
SKIP_PATTERNS = [
    "example_key_for_docs",
]
```

---

## Security Checklist

Before deploying to production:

- [ ] All secrets in `.env` (not in code)
- [ ] HTTPS enabled on API
- [ ] Database credentials rotated
- [ ] Firewall rules configured
- [ ] Rate limiting enabled
- [ ] Audit logging active
- [ ] Backup strategy implemented
- [ ] Monitoring/alerting configured
- [ ] Security scanning in CI/CD ✅

---

## Performance Tuning

### Scan Speed Optimization

```bash
# Exclude large directories
scg scan --path . --exclude node_modules --exclude .git

# Parallel scanning (future feature)
scg scan --workers 4
```

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_scan_project ON scans(project_id);
CREATE INDEX idx_finding_severity ON findings(severity);
```

---

## Monitoring & Alerts

### Set up Alerts for:
- Build failures (≥1 CRITICAL)
- Multiple HIGH severity issues
- Failed dependencies
- API downtime

### Example: Email Alert on FAIL

```python
# In decision_engine.py
if result["status"] == "FAIL":
    send_email_alert(result)
```

---

## Upgrade Guide

### Upgrading SCG

```bash
# Pull latest code
git pull origin main

# Reinstall CLI
cd cli && pip install -e . --upgrade

# Restart API
pkill -f "uvicorn"
python -m uvicorn app.main:app &
```

---

## Support

- 📖 [README.md](README.md) - Feature overview
- 🔐 [SECURITY.md](SECURITY.md) - Security hardening
- 🐛 Issues: `github.com/youruser/secure-cicd-guardian/issues`

---

**Next Step:** Run your first scan! 🚀

```bash
scg scan --path .
```
