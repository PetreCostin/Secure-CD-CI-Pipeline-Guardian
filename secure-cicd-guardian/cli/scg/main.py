"""
CLI Entry Point
Command-line interface for Secure CI/CD Guardian
"""

import json
import sys
import click
from pathlib import Path
from .scanner import SecurityScanner


@click.group()
def cli():
    """Secure CI/CD Pipeline Guardian - DevSecOps Security Scanner"""
    pass


@cli.command()
@click.option("--path", "-p", default=".", help="Path to scan")
@click.option("--output", "-o", help="Output file for JSON report")
@click.option("--fail-on", type=click.Choice(["critical", "high", "medium", "low"]),
              default="critical", help="Fail build if severity >= level")
def scan(path, output, fail_on):
    """Run security scan on project"""
    click.echo(f"🔍 Scanning: {path}")

    scanner = SecurityScanner(path)
    report = scanner.scan()

    # Print summary
    click.echo(f"\n📊 SCAN RESULTS:")
    click.echo(f"  • Critical: {report['statistics']['critical']}")
    click.echo(f"  • High: {report['statistics']['high']}")
    click.echo(f"  • Medium: {report['statistics']['medium']}")
    click.echo(f"  • Low: {report['statistics']['low']}")

    # Print findings
    if report['findings']:
        click.echo(f"\n🔒 FINDINGS ({len(report['findings'])} issues):\n")
        for finding in report['findings']:
            severity_emoji = {
                "CRITICAL": "🔴",
                "HIGH": "🟠",
                "MEDIUM": "🟡",
                "LOW": "🟢"
            }.get(finding['severity'], "⚪")
            click.echo(f"{severity_emoji} {finding['severity']:8} | {finding['type']:10} | {finding.get('file', 'N/A'):30} | {finding['message']}")

    # Write output file if specified
    if output:
        with open(output, "w") as f:
            json.dump(report, f, indent=2)
        click.echo(f"\n✅ Report saved to {output}")

    # Determine exit code based on fail-on level
    severity_levels = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    fail_level = severity_levels[fail_on]

    critical_in_range = report['statistics']['critical'] > 0
    high_in_range = fail_level >= 1 and report['statistics']['high'] >= 3

    if critical_in_range or high_in_range:
        click.echo(f"\n❌ BUILD FAILED: Security issues detected at {fail_on} level")
        sys.exit(1)
    else:
        click.echo(f"\n✅ BUILD PASSED: No {fail_on} severity issues found")
        sys.exit(0)


@cli.command()
@click.argument("project_id")
def report(project_id):
    """View scan report for project"""
    click.echo(f"📋 Report for project: {project_id}")
    click.echo("(Integration with backend required)")


if __name__ == "__main__":
    cli()
