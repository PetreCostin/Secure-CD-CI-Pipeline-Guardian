# Secure CI/CD Pipeline Guardian

**A DevSecOps tool that introduces automated security gates into CI/CD pipelines, preventing the deployment of vulnerable code.**

## Overview

Secure CI/CD Pipeline Guardian (SCG) is an open-source DevSecOps security scanner designed for CI/CD pipelines. It automatically detects:

- 🔐 **Hardcoded Secrets** - API keys, passwords, private keys using regex + entropy analysis
- 📦 **Vulnerable Dependencies** - Known CVEs in Python (requirements.txt) and Java (pom.xml)
- 🐳 **Docker Security Issues** - Root user, latest tags, exposed ports
- ⚙️ **Configuration Risks** - Exposed environment variables and unsafe configs

SCG **blocks the build** if security violations are detected, ensuring only secure code reaches production.

---

## Key Features

✅ **CLI Scanner** - Runs in CI/CD pipelines (GitHub Actions, GitLab CI, etc.)
✅ **Secret Detection** - Regex patterns + Shannon entropy analysis
✅ **Dependency Scanning** - Python & Java vulnerability checks
✅ **Docker Security** - Dockerfile best practices validation
✅ **Decision Engine** - Configurable FAIL/PASS policy
✅ **REST API** - Send results, store history, query reports
✅ **Web Dashboard** - View projects, scan history, security trends
✅ **GitHub Actions** - Native integration with auto-comments on PRs

---

## Architecture

```
Developer Push → GitHub Actions → SCG CLI Scanner → Backend API → Dashboard
                                    ↓
                             Decision Engine (PASS/FAIL)
                                    ↓
                             Build Status → Feedback to Developer
```

### Components

| Component | Role | Technology |
|-----------|------|-----------|
| **CLI Scanner** | Analyzes code, dependencies, configs | Python |
| **Backend API** | Processes results, makes decisions | FastAPI |
| **Dashboard** | Views projects, scans, findings | React |
| **Database** | Stores scan history, projects | PostgreSQL (optional) |
| **CI/CD** | Runs scanner automatically | GitHub Actions / GitLab CI |

---

## Quick Start

### 1. Install CLI

```bash
# From the cli directory
cd cli
pip install -e .
```

### 2. Run Scanner

```bash
# Scan current directory
scg scan --path .

# Scan with output file
scg scan --path . --output report.json

# Fail build if CRITICAL issues found (default)
scg scan --fail-on critical

# Fail build if 3+ HIGH issues found
scg scan --fail-on high
```

### 3. Start Backend API

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

API available at `http://localhost:8000`

### 4. GitHub Actions Integration

Add to `.github/workflows/security.yml`:

```yaml
- name: Install SCG
  run: pip install -e cli/

- name: Run Security Scan
  run: scg scan --output report.json --fail-on critical
```

---

## Decision Rules

The **Decision Engine** evaluates findings against a security policy:

| Condition | Decision |
|-----------|----------|
| **≥1 CRITICAL** | ❌ **FAIL** - Block build |
| **≥3 HIGH** | ❌ **FAIL** - Block build |
| Otherwise | ✅ **PASS** - Continue build |

### Change Policy

```bash
curl -X POST http://localhost:8000/api/policy \
  -H "Content-Type: application/json" \
  -d '{"critical_threshold": 0, "high_threshold": 2}'
```

---

## Scan Types

### Secret Detection

Detects:
- AWS Access Keys: `AKIA[0-9A-Z]{16}`
- GitHub Tokens: `ghp_[A-Za-z0-9]{36}`
- Generic Secrets: `password|api_key|secret` + entropy > 4.5
- Private Keys, Database URLs, Stripe/Slack tokens

### Dependency Scanning

**Python (requirements.txt)**
- Detects vulnerable package versions
- Mock CVE database (integrates with real ones)

**Java (pom.xml)**
- Scans Maven dependencies
- Flags known vulnerabilities

### Docker Security

- ✅ Using `latest` tag instead of specific version
- ✅ Missing `USER` directive (running as root)
- ✅ Using `sudo` in RUN commands
- ✅ Exposed ports without justification

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/scan` | POST | Submit scan results |
| `/api/projects` | GET | List all projects |
| `/api/projects/{id}/scans` | GET | Get project scans |
| `/api/scans/{id}` | GET | Get specific scan |
| `/api/policy` | GET | Get security policy |
| `/api/policy` | POST | Update security policy |
| `/api/stats` | GET | Get statistics |

### Example: Submit Scan Results

```bash
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "project": "api-service",
    "commit": "a9f3c2e1f",
    "results": [
      {
        "type": "SECRET",
        "severity": "CRITICAL",
        "file": "config.py",
        "line": 14,
        "rule": "AWS_ACCESS_KEY",
        "message": "Potential AWS Access Key detected"
      }
    ]
  }'
```

---

## Output Format

```json
{
  "project": "my-app",
  "timestamp": "2024-01-14T10:30:00",
  "status": "FAIL",
  "statistics": {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 5,
    "total": 11
  },
  "findings": [
    {
      "type": "SECRET",
      "severity": "CRITICAL",
      "file": "src/config.py",
      "line": 14,
      "rule": "AWS_ACCESS_KEY",
      "message": "Potential AWS Access Key detected"
    }
  ]
}
```

---

## Security by Design

- **No Secret Storage** - Only environment variables for sensitive data
- **OAuth2 Ready** - GitHub authentication support (extensible)
- **RBAC** - Role-based access control (Owner/Viewer)
- **Rate Limiting** - Built-in protection against abuse
- **Audit Logs** - All scans and decisions logged
- **Short-lived Tokens** - JWT with 15-minute expiration

---

## Project Structure

```
secure-cicd-guardian/
├── cli/                          # CLI Scanner
│   ├── scg/
│   │   ├── __init__.py
│   │   ├── main.py              # CLI entry point
│   │   ├── scanner.py           # Orchestrator
│   │   ├── secrets.py           # Secret detection
│   │   ├── dependencies.py      # Dependency checker
│   │   └── dockerfile.py        # Docker security
│   └── setup.py
│
├── backend/                       # FastAPI Backend
│   ├── app/
│   │   ├── main.py              # API application
│   │   ├── core/
│   │   │   └── decision_engine.py
│   │   └── models/
│   │       └── scan.py
│   └── requirements.txt
│
├── dashboard/                     # React Frontend
│   └── src/
│       ├── pages/
│       └── components/
│
├── .github/workflows/
│   └── security.yml             # GitHub Actions workflow
│
├── docker-compose.yml           # Local development
├── README.md                    # This file
└── SECURITY.md                  # Security hardening guide
```

---

## Use Cases

### 1. Block Secrets Before Deploy

```yaml
- run: scg scan --fail-on critical
```

If a developer accidentally commits an API key, the build fails immediately.

### 2. Enforce Dependency Updates

Scan dependencies on every push, alert on known CVEs.

### 3. Docker Security Gate

Prevent Docker images with `latest` tags or root users from reaching production.

### 4. Compliance Audit

Export all scan reports for compliance documentation (SOC 2, GDPR, etc.).

---

## Development Roadmap

**Phase 1** - Core CLI (Done ✅)
- Secret detection
- Dependency checking
- Dockerfile validation

**Phase 2** - Backend & API (In Progress 🚀)
- FastAPI setup
- Decision engine
- Report storage

**Phase 3** - Dashboard & Auth
- React UI
- GitHub OAuth
- Scan history visualization

**Phase 4** - Advanced Features
- SBOM (Software Bill of Materials)
- Custom policies as code
- GitLab CI integration
- SARIF format export

---

## Contributing

Contributions welcome! Areas to improve:

- Real CVE database integration (NVD, Snyk)
- More secret patterns
- Custom rule engine
- Performance optimization
- Kubernetes scanning

---

## FAQ

**Q: Will it slow down my CI/CD pipeline?**
A: Scans typically complete in 5-30 seconds depending on project size.

**Q: Can I customize the rules?**
A: Yes! Modify `PATTERNS` dictionaries in `secrets.py`, `dependencies.py`, etc.

**Q: What if I have a false positive?**
A: Add exceptions in the code, or adjust entropy thresholds.

**Q: Does it work with private GitHub repos?**
A: Yes! Provide GitHub token via environment variables.

**Q: Can I integrate with other CI/CD systems?**
A: The CLI is platform-agnostic. Add support for GitLab, Jenkins, etc.

---

## License

MIT License - See LICENSE file

---

## Support

- 📖 Documentation: [View Wiki](https://github.com/yourusername/secure-cicd-guardian/wiki)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/secure-cicd-guardian/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/secure-cicd-guardian/discussions)

---

## Authors

Built with ❤️ by the Secure CI/CD Guardian team

---

**Secure CI/CD Pipeline Guardian** - *Making DevSecOps accessible and automatic.*
