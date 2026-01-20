"""
Dockerfile Security Checker
Checks Docker configurations for security issues
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class DockerFinding:
    type: str
    severity: str
    file: str
    line: int
    rule: str
    message: str


class DockerfileChecker:
    """Checks Dockerfile for security issues"""

    RULES = {
        "RUN_AS_ROOT": {
            "pattern": r"^FROM\s+(\S+(?::\S+)?)\s*$",
            "severity": "HIGH",
            "description": "Missing USER directive - container runs as root",
            "solution": "Add 'USER nonroot' at the end of Dockerfile"
        },
        "LATEST_IMAGE": {
            "pattern": r"FROM\s+(\S+):latest",
            "severity": "MEDIUM",
            "description": "Using 'latest' tag - unpredictable builds",
            "solution": "Pin to specific image version, e.g. 'ubuntu:22.04'"
        },
        "EXPOSED_PORTS": {
            "pattern": r"EXPOSE\s+(\d+)",
            "severity": "LOW",
            "description": "Port exposed - verify it's intentional",
            "solution": "Review exposed ports for necessity"
        },
        "NO_HEALTHCHECK": {
            "pattern": r"^(?!.*HEALTHCHECK).*$",
            "severity": "LOW",
            "description": "No HEALTHCHECK defined",
            "solution": "Add HEALTHCHECK instruction for container monitoring"
        },
        "RUN_SUDO": {
            "pattern": r"RUN.*sudo",
            "severity": "MEDIUM",
            "description": "Using sudo in Dockerfile",
            "solution": "Use package managers directly without sudo"
        }
    }

    def scan_dockerfile(self, content: str) -> List[DockerFinding]:
        """Scan Dockerfile for security issues"""
        findings = []
        lines = content.split("\n")
        has_user = False

        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Check for USER directive
            if line_stripped.startswith("USER"):
                if "root" not in line_stripped:
                    has_user = True
                continue

            # Skip comments and empty lines
            if line_stripped.startswith("#") or not line_stripped:
                continue

            # Check if using latest tag
            if re.match(self.RULES["LATEST_IMAGE"]["pattern"], line_stripped):
                findings.append(
                    DockerFinding(
                        type="DOCKER",
                        severity=self.RULES["LATEST_IMAGE"]["severity"],
                        file="Dockerfile",
                        line=line_num,
                        rule="LATEST_IMAGE",
                        message=self.RULES["LATEST_IMAGE"]["description"]
                    )
                )

            # Check for sudo
            if re.search(self.RULES["RUN_SUDO"]["pattern"], line_stripped, re.IGNORECASE):
                findings.append(
                    DockerFinding(
                        type="DOCKER",
                        severity=self.RULES["RUN_SUDO"]["severity"],
                        file="Dockerfile",
                        line=line_num,
                        rule="RUN_SUDO",
                        message=self.RULES["RUN_SUDO"]["description"]
                    )
                )

            # Check for exposed ports
            if re.match(self.RULES["EXPOSED_PORTS"]["pattern"], line_stripped):
                findings.append(
                    DockerFinding(
                        type="DOCKER",
                        severity=self.RULES["EXPOSED_PORTS"]["severity"],
                        file="Dockerfile",
                        line=line_num,
                        rule="EXPOSED_PORTS",
                        message=self.RULES["EXPOSED_PORTS"]["description"]
                    )
                )

        # Check if no USER directive defined
        if not has_user and lines:
            findings.append(
                DockerFinding(
                    type="DOCKER",
                    severity=self.RULES["RUN_AS_ROOT"]["severity"],
                    file="Dockerfile",
                    line=len(lines),
                    rule="RUN_AS_ROOT",
                    message=self.RULES["RUN_AS_ROOT"]["description"]
                )
            )

        return findings

    def to_dict(self, finding: DockerFinding) -> Dict[str, Any]:
        """Convert finding to dictionary"""
        return {
            "type": finding.type,
            "severity": finding.severity,
            "file": finding.file,
            "line": finding.line,
            "rule": finding.rule,
            "message": finding.message
        }
