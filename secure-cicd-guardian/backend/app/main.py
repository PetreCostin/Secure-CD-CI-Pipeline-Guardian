"""
FastAPI Backend
Main application server
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid

from app.models.scan import ScanRequest, ScanResponse, Scan as ScanModel
from app.core.decision_engine import DecisionEngine

app = FastAPI(
    title="Secure CI/CD Pipeline Guardian API",
    version="1.0.0",
    description="DevSecOps security scanning API"
)

# Enable CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (in production, use database)
scans_db = {}
projects_db = {}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "secure-cicd-guardian"}


@app.post("/api/scan", response_model=ScanResponse)
async def receive_scan(request: ScanRequest):
    """
    Receive scan results and evaluate against security policy

    Returns PASS/FAIL based on severity thresholds
    """

    # Count findings by severity
    findings_list = [f.dict() if hasattr(f, 'dict') else f for f in request.results]

    critical = sum(1 for f in findings_list if f.get("severity") == "CRITICAL")
    high = sum(1 for f in findings_list if f.get("severity") == "HIGH")
    medium = sum(1 for f in findings_list if f.get("severity") == "MEDIUM")
    low = sum(1 for f in findings_list if f.get("severity") == "LOW")

    # Evaluate decision
    decision = DecisionEngine.evaluate(findings_list)

    # Store scan result
    scan_id = str(uuid.uuid4())
    scan_data = {
        "id": scan_id,
        "project_id": request.project,
        "timestamp": datetime.now().isoformat(),
        "commit": request.commit,
        "status": decision["status"],
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "findings": findings_list
    }
    scans_db[scan_id] = scan_data

    return ScanResponse(
        status=decision["status"],
        critical=critical,
        high=high,
        medium=medium,
        low=low,
        message=decision["reason"]
    )


@app.get("/api/projects")
async def list_projects():
    """List all projects"""
    return list(projects_db.values())


@app.get("/api/projects/{project_id}/scans")
async def get_project_scans(project_id: str):
    """Get all scans for a project"""
    project_scans = [s for s in scans_db.values() if s["project_id"] == project_id]
    return sorted(project_scans, key=lambda x: x["timestamp"], reverse=True)


@app.get("/api/scans/{scan_id}")
async def get_scan(scan_id: str):
    """Get specific scan result"""
    if scan_id not in scans_db:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scans_db[scan_id]


@app.get("/api/policy")
async def get_security_policy():
    """Get current security policy"""
    return DecisionEngine.get_policy()


@app.post("/api/policy")
async def update_security_policy(critical_threshold: int = None, high_threshold: int = None):
    """Update security policy"""
    DecisionEngine.set_policy(critical_threshold, high_threshold)
    return DecisionEngine.get_policy()


@app.get("/api/stats")
async def get_statistics():
    """Get overall statistics"""
    total_scans = len(scans_db)
    failed_scans = sum(1 for s in scans_db.values() if s["status"] == "FAIL")
    passed_scans = total_scans - failed_scans

    total_critical = sum(s["critical"] for s in scans_db.values())
    total_high = sum(s["high"] for s in scans_db.values())

    return {
        "total_scans": total_scans,
        "passed_scans": passed_scans,
        "failed_scans": failed_scans,
        "pass_rate": (passed_scans / total_scans * 100) if total_scans > 0 else 0,
        "total_critical_issues": total_critical,
        "total_high_issues": total_high
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
