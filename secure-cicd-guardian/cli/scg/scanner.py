"""
Main Scanner Orchestrator
Coordinates all security scans
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from .secrets import SecretDetector
from .dependencies import DependencyChecker
from .dockerfile import DockerfileChecker


class SecurityScanner:
    """Main orchestrator for security scanning"""

    def __init__(self, path: str = "."):
        self.path = Path(path)
        self.secret_detector = SecretDetector()
        self.dependency_checker = DependencyChecker()
        self.dockerfile_checker = DockerfileChecker()
        self.findings = []

    def scan(self) -> Dict[str, Any]:
        """Run complete security scan"""
        self.findings = []

        # Scan for secrets in all source files
        self._scan_secrets()

        # Scan dependencies
        self._scan_dependencies()

        # Scan Dockerfile
        self._scan_dockerfile()

        return self._generate_report()

    def _scan_secrets(self):
        """Scan all source files for secrets"""
        source_extensions = {".py", ".js", ".ts", ".java", ".go", ".rb", ".sh", ".yml", ".yaml", ".json", ".env"}

        for file_path in self.path.rglob("*"):
            if file_path.is_file() and file_path.suffix in source_extensions:
                # Skip node_modules and .git
                if "node_modules" in str(file_path) or ".git" in str(file_path):
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    relative_path = file_path.relative_to(self.path)
                    findings = self.secret_detector.scan_file(str(relative_path), content)
                    for finding in findings:
                        self.findings.append(self.secret_detector.to_dict(finding))
                except Exception as e:
                    pass

    def _scan_dependencies(self):
        """Scan for vulnerable dependencies"""
        # Check requirements.txt
        req_file = self.path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, "r") as f:
                    content = f.read()
                findings = self.dependency_checker.check_python_requirements(content)
                for finding in findings:
                    self.findings.append(self.dependency_checker.to_dict(finding))
            except Exception as e:
                pass

        # Check pom.xml
        pom_file = self.path / "pom.xml"
        if pom_file.exists():
            try:
                with open(pom_file, "r") as f:
                    content = f.read()
                findings = self.dependency_checker.check_maven_pom(content)
                for finding in findings:
                    self.findings.append(self.dependency_checker.to_dict(finding))
            except Exception as e:
                pass

    def _scan_dockerfile(self):
        """Scan Dockerfile for security issues"""
        dockerfile = self.path / "Dockerfile"
        if dockerfile.exists():
            try:
                with open(dockerfile, "r") as f:
                    content = f.read()
                findings = self.dockerfile_checker.scan_dockerfile(content)
                for finding in findings:
                    self.findings.append(self.dockerfile_checker.to_dict(finding))
            except Exception as e:
                pass

    def _generate_report(self) -> Dict[str, Any]:
        """Generate security report"""
        critical_count = sum(1 for f in self.findings if f["severity"] == "CRITICAL")
        high_count = sum(1 for f in self.findings if f["severity"] == "HIGH")
        medium_count = sum(1 for f in self.findings if f["severity"] == "MEDIUM")
        low_count = sum(1 for f in self.findings if f["severity"] == "LOW")

        # Determine overall status
        status = "PASS"
        if critical_count >= 1:
            status = "FAIL"
        elif high_count >= 3:
            status = "FAIL"

        return {
            "project": os.path.basename(self.path),
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "statistics": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": low_count,
                "total": len(self.findings)
            },
            "findings": self.findings
        }
