"""
Security Decision Engine
Evaluates findings and determines build status
"""

from typing import List, Dict, Any


class DecisionEngine:
    """Evaluates security findings and decides PASS/FAIL"""

    # Security policy
    FAIL_POLICY = {
        "critical_threshold": 1,  # Fail if >= 1 CRITICAL
        "high_threshold": 3,      # Fail if >= 3 HIGH
    }

    @staticmethod
    def evaluate(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate findings against security policy
        Returns: {"status": "PASS"/"FAIL", "reason": str}
        """

        critical_count = sum(1 for f in findings if f.get("severity") == "CRITICAL")
        high_count = sum(1 for f in findings if f.get("severity") == "HIGH")

        # Check policy
        if critical_count >= DecisionEngine.FAIL_POLICY["critical_threshold"]:
            return {
                "status": "FAIL",
                "reason": f"Found {critical_count} CRITICAL severity issues",
                "policy_violated": "critical_threshold"
            }

        if high_count >= DecisionEngine.FAIL_POLICY["high_threshold"]:
            return {
                "status": "FAIL",
                "reason": f"Found {high_count} HIGH severity issues (threshold: {DecisionEngine.FAIL_POLICY['high_threshold']})",
                "policy_violated": "high_threshold"
            }

        return {
            "status": "PASS",
            "reason": "All findings within acceptable thresholds",
            "policy_violated": None
        }

    @staticmethod
    def get_policy() -> Dict[str, Any]:
        """Get current security policy"""
        return DecisionEngine.FAIL_POLICY

    @staticmethod
    def set_policy(critical_threshold: int = None, high_threshold: int = None):
        """Update security policy"""
        if critical_threshold is not None:
            DecisionEngine.FAIL_POLICY["critical_threshold"] = critical_threshold
        if high_threshold is not None:
            DecisionEngine.FAIL_POLICY["high_threshold"] = high_threshold
