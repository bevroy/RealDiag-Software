#!/usr/bin/env python3
"""
Setup script for RealDiag-Software
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read the VERSION file
version_file = Path(__file__).parent / "VERSION"
version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "1.0.0"

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="realdiag-software",
    version=version,
    description="Real Time Diagnostic Assistant Software - System health monitoring and diagnostics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="RealDiag-Software Contributors",
    author_email="",
    url="https://github.com/bevroy/RealDiag-Software",
    project_urls={
        "Bug Reports": "https://github.com/bevroy/RealDiag-Software/issues",
        "Source": "https://github.com/bevroy/RealDiag-Software",
        "Documentation": "https://github.com/bevroy/RealDiag-Software#readme",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "realdiag=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
    ],
    keywords="diagnostics monitoring system health performance network",
    license="MIT",
)
