"""
Dependency Vulnerability Checker
Scans requirements.txt and pom.xml for known vulnerabilities
"""

import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class DependencyFinding:
    type: str
    severity: str
    package: str
    current_version: str
    safe_version: str
    rule: str


class DependencyChecker:
    """Checks dependencies for known vulnerabilities"""

    # Mock CVE database (in production, use real CVE databases)
    CVE_DATABASE = {
        "log4j": {
            "vulnerable_versions": [("0", "2.16.0")],
            "severity": "CRITICAL",
            "description": "Log4Shell - Remote Code Execution"
        },
        "spring-core": {
            "vulnerable_versions": [("0", "5.3.0")],
            "severity": "HIGH",
            "description": "Spring Core vulnerability"
        },
        "requests": {
            "vulnerable_versions": [("0", "2.27.0")],
            "severity": "MEDIUM",
            "description": "Requests library vulnerability"
        },
        "django": {
            "vulnerable_versions": [("0", "3.2.0")],
            "severity": "HIGH",
            "description": "Django security vulnerability"
        },
        "pyyaml": {
            "vulnerable_versions": [("0", "5.4.0")],
            "severity": "HIGH",
            "description": "PyYAML unsafe load vulnerability"
        },
        "cryptography": {
            "vulnerable_versions": [("0", "3.4.8")],
            "severity": "MEDIUM",
            "description": "Cryptography library vulnerability"
        }
    }

    @staticmethod
    def parse_version(version: str) -> Tuple[int, int, int]:
        """Parse version string to tuple"""
        try:
            parts = version.split(".")
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            return (major, minor, patch)
        except (ValueError, IndexError):
            return (0, 0, 0)

    @staticmethod
    def version_in_range(version: str, min_v: str, max_v: str) -> bool:
        """Check if version is in vulnerable range"""
        v = DependencyChecker.parse_version(version)
        min_version = DependencyChecker.parse_version(min_v)
        max_version = DependencyChecker.parse_version(max_v)
        return min_version <= v <= max_version

    def check_python_requirements(self, content: str) -> List[DependencyFinding]:
        """Check Python requirements.txt for vulnerabilities"""
        findings = []
        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Parse package==version
            match = re.match(r"([a-zA-Z0-9\-_.]+)(?:==|>=|<=|>|<)?(.+)?", line)
            if not match:
                continue

            package_name = match.group(1).lower()
            version = match.group(2) or "0.0.0"

            # Check against CVE database
            if package_name in self.CVE_DATABASE:
                cve = self.CVE_DATABASE[package_name]
                for min_v, max_v in cve["vulnerable_versions"]:
                    if self.version_in_range(version, min_v, max_v):
                        findings.append(
                            DependencyFinding(
                                type="DEPENDENCY",
                                severity=cve["severity"],
                                package=package_name,
                                current_version=version,
                                safe_version=max_v,
                                rule=cve["description"]
                            )
                        )
                        break

        return findings

    def check_maven_pom(self, content: str) -> List[DependencyFinding]:
        """Check pom.xml for Java vulnerabilities"""
        findings = []
        try:
            root = ET.fromstring(content)
            # Simple namespace handling
            namespace = {'m': 'http://maven.apache.org/POM/4.0.0'}

            for dep in root.findall('.//m:dependency', namespace):
                artifact = dep.find('m:artifactId', namespace)
                version = dep.find('m:version', namespace)

                if artifact is None or version is None:
                    continue

                package_name = artifact.text.lower()
                version_text = version.text

                if package_name in self.CVE_DATABASE:
                    cve = self.CVE_DATABASE[package_name]
                    for min_v, max_v in cve["vulnerable_versions"]:
                        if self.version_in_range(version_text, min_v, max_v):
                            findings.append(
                                DependencyFinding(
                                    type="DEPENDENCY",
                                    severity=cve["severity"],
                                    package=package_name,
                                    current_version=version_text,
                                    safe_version=max_v,
                                    rule=cve["description"]
                                )
                            )
                            break
        except ET.ParseError:
            pass

        return findings

    def to_dict(self, finding: DependencyFinding) -> Dict[str, Any]:
        """Convert finding to dictionary"""
        return {
            "type": finding.type,
            "severity": finding.severity,
            "package": finding.package,
            "current_version": finding.current_version,
            "safe_version": finding.safe_version,
            "rule": finding.rule,
            "message": f"Vulnerable {finding.package}@{finding.current_version}: {finding.rule}"
        }
