"""
Backend Models for Secure CI/CD Guardian
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Finding(BaseModel):
    """Security finding"""
    type: str
    severity: str
    file: str
    line: int
    rule: str
    message: str


class ScanRequest(BaseModel):
    """Scan request payload"""
    project: str
    commit: str
    results: List[Finding]


class ScanResponse(BaseModel):
    """Scan response"""
    status: str
    critical: int
    high: int
    medium: int
    low: int
    message: str


class Project(BaseModel):
    """Project model"""
    id: str
    name: str
    repo_url: str
    owner: str
    created_at: datetime = None


class Scan(BaseModel):
    """Scan model"""
    id: str
    project_id: str
    timestamp: datetime
    status: str
    critical: int
    high: int
    medium: int
    low: int
    findings: List[Finding]
