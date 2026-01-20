"""
Secret Detection Module
Detects hardcoded secrets using regex patterns and entropy analysis
"""

import re
import math
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class SecretFinding:
    type: str
    severity: str
    file: str
    line: int
    rule: str
    match: str


class SecretDetector:
    """Detects hardcoded secrets in source code"""

    PATTERNS = {
        "AWS_ACCESS_KEY": {
            "pattern": r"AKIA[0-9A-Z]{16}",
            "severity": "CRITICAL"
        },
        "AWS_SECRET_KEY": {
            "pattern": r"aws_secret_access_key\s*=\s*['\"][^'\"]{40}['\"]",
            "severity": "CRITICAL"
        },
        "GITHUB_TOKEN": {
            "pattern": r"ghp_[A-Za-z0-9]{36}",
            "severity": "CRITICAL"
        },
        "GENERIC_PASSWORD": {
            "pattern": r"(password|passwd|pwd)\s*[=:]\s*['\"]([^'\"]{8,})['\"]",
            "severity": "HIGH"
        },
        "API_KEY": {
            "pattern": r"(api_key|apikey|api-key)\s*[=:]\s*['\"]([^'\"]{16,})['\"]",
            "severity": "HIGH"
        },
        "PRIVATE_KEY": {
            "pattern": r"-----BEGIN (RSA |DSA |EC )?PRIVATE KEY",
            "severity": "CRITICAL"
        },
        "DATABASE_URL": {
            "pattern": r"(database|db)_?url\s*[=:]\s*['\"]?(postgres|mysql|mongodb)://[^\s'\"]+",
            "severity": "HIGH"
        },
        "SLACK_TOKEN": {
            "pattern": r"xox[baprs]-[0-9a-zA-Z]{10,48}",
            "severity": "HIGH"
        },
        "STRIPE_KEY": {
            "pattern": r"sk_(live|test)_[0-9a-zA-Z]{24,}",
            "severity": "CRITICAL"
        }
    }

    @staticmethod
    def calculate_entropy(s: str) -> float:
        """Calculate Shannon entropy of a string"""
        if not s:
            return 0
        entropy = 0
        for char in set(s):
            p_x = s.count(char) / len(s)
            entropy -= p_x * math.log2(p_x)
        return entropy

    @staticmethod
    def get_entropy_severity(entropy: float) -> str:
        """Determine severity based on entropy"""
        if entropy > 5.5:
            return "CRITICAL"
        elif entropy > 4.5:
            return "HIGH"
        elif entropy > 3.5:
            return "MEDIUM"
        return "LOW"

    def scan_file(self, file_path: str, content: str) -> List[SecretFinding]:
        """Scan a file for secrets"""
        findings = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Skip comments and empty lines
            if line.strip().startswith("#") or not line.strip():
                continue

            # Check each pattern
            for rule_name, rule_config in self.PATTERNS.items():
                pattern = rule_config["pattern"]
                matches = re.finditer(pattern, line, re.IGNORECASE)

                for match in matches:
                    # Calculate entropy for the matched value
                    matched_value = match.group(0)
                    entropy = self.calculate_entropy(matched_value)
                    entropy_severity = self.get_entropy_severity(entropy)

                    # Use the higher severity
                    severity = rule_config["severity"]
                    if entropy_severity in ["CRITICAL", "HIGH"] and entropy_severity != severity:
                        if entropy_severity == "CRITICAL":
                            severity = "CRITICAL"
                        elif entropy_severity == "HIGH" and severity != "CRITICAL":
                            severity = "HIGH"

                    findings.append(
                        SecretFinding(
                            type="SECRET",
                            severity=severity,
                            file=file_path,
                            line=line_num,
                            rule=rule_name,
                            match=matched_value[:20] + "***" if len(matched_value) > 20 else matched_value
                        )
                    )

        return findings

    def to_dict(self, finding: SecretFinding) -> Dict[str, Any]:
        """Convert finding to dictionary"""
        return {
            "type": finding.type,
            "severity": finding.severity,
            "file": finding.file,
            "line": finding.line,
            "rule": finding.rule,
            "message": f"Potential {finding.rule} detected",
            "match": finding.match
        }
