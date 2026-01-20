#!/usr/bin/env python
"""Setup script for Secure CI/CD Guardian CLI"""

from setuptools import setup, find_packages

setup(
    name="secure-cicd-guardian",
    version="1.0.0",
    description="DevSecOps tool for automated security scanning in CI/CD pipelines",
    author="Security Team",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "scg=scg.main:cli",
        ]
    },
    install_requires=[
        "click>=8.0.0",
    ],
    python_requires=">=3.8",
)
