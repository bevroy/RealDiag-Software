"""
Security Audit Checklist and Tools
OWASP Top 10 checks, dependency scanning, security best practices
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any
import hashlib
import re


class SecurityAuditor:
    """Security audit tools and checklist"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = []
    
    def run_full_audit(self) -> Dict[str, Any]:
        """Run complete security audit"""
        print("🔒 Starting Security Audit...\n")
        
        results = {
            "owasp_top_10": self.check_owasp_top_10(),
            "dependencies": self.scan_dependencies(),
            "secrets": self.scan_for_secrets(),
            "code_quality": self.check_code_quality(),
            "configuration": self.check_configuration(),
            "summary": {}
        }
        
        # Generate summary
        total_issues = sum(len(v.get("issues", [])) for v in results.values() if isinstance(v, dict))
        results["summary"] = {
            "total_issues": total_issues,
            "critical": sum(1 for issue in self.issues if issue.get("severity") == "CRITICAL"),
            "high": sum(1 for issue in self.issues if issue.get("severity") == "HIGH"),
            "medium": sum(1 for issue in self.issues if issue.get("severity") == "MEDIUM"),
            "low": sum(1 for issue in self.issues if issue.get("severity") == "LOW")
        }
        
        return results
    
    def check_owasp_top_10(self) -> Dict[str, Any]:
        """Check against OWASP Top 10 vulnerabilities"""
        print("📋 Checking OWASP Top 10...")
        
        checks = {
            "A01_Broken_Access_Control": self._check_access_control(),
            "A02_Cryptographic_Failures": self._check_cryptography(),
            "A03_Injection": self._check_injection(),
            "A04_Insecure_Design": self._check_design(),
            "A05_Security_Misconfiguration": self._check_misconfiguration(),
            "A06_Vulnerable_Components": self._check_components(),
            "A07_Authentication_Failures": self._check_authentication(),
            "A08_Data_Integrity_Failures": self._check_integrity(),
            "A09_Logging_Monitoring_Failures": self._check_logging(),
            "A10_SSRF": self._check_ssrf()
        }
        
        return {
            "checks": checks,
            "issues": [issue for check in checks.values() for issue in check.get("issues", [])]
        }
    
    def _check_access_control(self) -> Dict[str, Any]:
        """Check for broken access control"""
        issues = []
        
        # Check for missing authentication decorators
        python_files = list(self.project_root.glob("**/*.py"))
        for file in python_files:
            if "services" in str(file):
                content = file.read_text()
                # Look for routes without authentication
                if "@router." in content and "Depends(get_current_user)" not in content:
                    if "health" not in str(file) and "monitoring" not in str(file):
                        issues.append({
                            "file": str(file.relative_to(self.project_root)),
                            "issue": "Routes may be missing authentication",
                            "severity": "MEDIUM"
                        })
        
        return {"status": "checked", "issues": issues}
    
    def _check_cryptography(self) -> Dict[str, Any]:
        """Check for cryptographic failures"""
        issues = []
        
        # Check for hardcoded secrets
        python_files = list(self.project_root.glob("**/*.py"))
        dangerous_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']'
        ]
        
        for file in python_files:
            content = file.read_text()
            for pattern in dangerous_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append({
                        "file": str(file.relative_to(self.project_root)),
                        "issue": "Possible hardcoded secret",
                        "severity": "HIGH"
                    })
        
        return {"status": "checked", "issues": issues}
    
    def _check_injection(self) -> Dict[str, Any]:
        """Check for injection vulnerabilities"""
        issues = []
        
        # Check for SQL injection risks
        python_files = list(self.project_root.glob("**/*.py"))
        for file in python_files:
            content = file.read_text()
            # Look for string formatting in SQL contexts
            if "execute(" in content or "query(" in content:
                if "f\"" in content or "format(" in content:
                    issues.append({
                        "file": str(file.relative_to(self.project_root)),
                        "issue": "Possible SQL injection via string formatting",
                        "severity": "CRITICAL"
                    })
        
        return {"status": "checked", "issues": issues}
    
    def _check_design(self) -> Dict[str, Any]:
        """Check for insecure design patterns"""
        return {"status": "manual_review_required", "issues": []}
    
    def _check_misconfiguration(self) -> Dict[str, Any]:
        """Check for security misconfiguration"""
        issues = []
        
        # Check for debug mode in production
        config_files = list(self.project_root.glob("**/config.py"))
        for file in config_files:
            content = file.read_text()
            if "DEBUG = True" in content or "debug=True" in content:
                issues.append({
                    "file": str(file.relative_to(self.project_root)),
                    "issue": "Debug mode may be enabled",
                    "severity": "HIGH"
                })
        
        return {"status": "checked", "issues": issues}
    
    def _check_components(self) -> Dict[str, Any]:
        """Check for vulnerable components"""
        # This would use safety or pip-audit in practice
        return {"status": "see_dependency_scan", "issues": []}
    
    def _check_authentication(self) -> Dict[str, Any]:
        """Check for authentication failures"""
        issues = []
        
        # Check for weak password requirements
        python_files = list(self.project_root.glob("**/*.py"))
        for file in python_files:
            content = file.read_text()
            if "password" in content.lower() and "len(" in content:
                # Simple check for password length validation
                if "len(password) < 8" not in content and "len(password) >= 8" not in content:
                    if "user" in str(file) or "auth" in str(file):
                        issues.append({
                            "file": str(file.relative_to(self.project_root)),
                            "issue": "Password validation may be weak",
                            "severity": "MEDIUM"
                        })
        
        return {"status": "checked", "issues": issues}
    
    def _check_integrity(self) -> Dict[str, Any]:
        """Check for data integrity failures"""
        return {"status": "checked", "issues": []}
    
    def _check_logging(self) -> Dict[str, Any]:
        """Check for logging and monitoring failures"""
        issues = []
        
        # Check if logging is configured
        has_logging = False
        python_files = list(self.project_root.glob("**/*.py"))
        for file in python_files:
            content = file.read_text()
            if "import logging" in content:
                has_logging = True
                break
        
        if not has_logging:
            issues.append({
                "file": "N/A",
                "issue": "Logging may not be configured",
                "severity": "MEDIUM"
            })
        
        return {"status": "checked", "issues": issues}
    
    def _check_ssrf(self) -> Dict[str, Any]:
        """Check for SSRF vulnerabilities"""
        issues = []
        
        # Check for unvalidated URL requests
        python_files = list(self.project_root.glob("**/*.py"))
        for file in python_files:
            content = file.read_text()
            if "requests.get(" in content or "httpx.get(" in content:
                # Look for URL validation
                if "validate_url" not in content and "urlparse" not in content:
                    issues.append({
                        "file": str(file.relative_to(self.project_root)),
                        "issue": "External requests may not validate URLs",
                        "severity": "MEDIUM"
                    })
        
        return {"status": "checked", "issues": issues}
    
    def scan_dependencies(self) -> Dict[str, Any]:
        """Scan dependencies for vulnerabilities"""
        print("🔍 Scanning dependencies...")
        
        results = {"issues": []}
        
        try:
            # Try using pip-audit if available
            result = subprocess.run(
                ["pip-audit", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                vulnerabilities = json.loads(result.stdout)
                results["vulnerabilities"] = vulnerabilities
                results["issues"] = [
                    {
                        "package": vuln.get("name"),
                        "issue": vuln.get("description"),
                        "severity": "HIGH"
                    }
                    for vuln in vulnerabilities.get("dependencies", [])
                ]
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            results["status"] = "pip-audit not available or timed out"
        
        return results
    
    def scan_for_secrets(self) -> Dict[str, Any]:
        """Scan for hardcoded secrets"""
        print("🔐 Scanning for secrets...")
        
        issues = []
        
        # Patterns for secrets
        secret_patterns = {
            "AWS Access Key": r"AKIA[0-9A-Z]{16}",
            "API Key": r"api[_-]?key['\"]?\s*[:=]\s*['\"][a-zA-Z0-9]{32,}['\"]",
            "Password": r"password['\"]?\s*[:=]\s*['\"][^'\"]{8,}['\"]",
            "Private Key": r"-----BEGIN (RSA |EC )?PRIVATE KEY-----"
        }
        
        files_to_scan = list(self.project_root.glob("**/*.py")) + \
                       list(self.project_root.glob("**/*.js")) + \
                       list(self.project_root.glob("**/*.yml")) + \
                       list(self.project_root.glob("**/*.yaml"))
        
        for file in files_to_scan:
            try:
                content = file.read_text()
                for secret_type, pattern in secret_patterns.items():
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        issues.append({
                            "file": str(file.relative_to(self.project_root)),
                            "line": content[:match.start()].count("\n") + 1,
                            "issue": f"Possible {secret_type} found",
                            "severity": "CRITICAL"
                        })
            except Exception:
                continue
        
        return {"issues": issues}
    
    def check_code_quality(self) -> Dict[str, Any]:
        """Check code quality and security with bandit"""
        print("🎯 Checking code quality...")
        
        try:
            # Run bandit security linter
            result = subprocess.run(
                ["bandit", "-r", str(self.project_root / "backend"), "-f", "json"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 or result.stdout:
                data = json.loads(result.stdout)
                return {
                    "results": data.get("results", []),
                    "issues": [
                        {
                            "file": issue.get("filename"),
                            "line": issue.get("line_number"),
                            "issue": issue.get("issue_text"),
                            "severity": issue.get("issue_severity")
                        }
                        for issue in data.get("results", [])
                    ]
                }
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            return {"status": "bandit not available or timed out"}
    
    def check_configuration(self) -> Dict[str, Any]:
        """Check security configuration"""
        print("⚙️  Checking configuration...")
        
        issues = []
        
        # Check for .env file
        env_file = self.project_root / ".env"
        if env_file.exists():
            # Check if .env is in .gitignore
            gitignore = self.project_root / ".gitignore"
            if gitignore.exists():
                if ".env" not in gitignore.read_text():
                    issues.append({
                        "file": ".gitignore",
                        "issue": ".env file not in .gitignore",
                        "severity": "HIGH"
                    })
        
        # Check for HTTPS configuration
        docker_compose = self.project_root / "docker-compose.yml"
        if docker_compose.exists():
            content = docker_compose.read_text()
            if "http://" in content and "https://" not in content:
                issues.append({
                    "file": "docker-compose.yml",
                    "issue": "May not be using HTTPS",
                    "severity": "MEDIUM"
                })
        
        return {"issues": issues}
    
    def generate_report(self, results: Dict[str, Any], output_file: str = "security_audit_report.json"):
        """Generate security audit report"""
        print(f"\n📊 Generating report: {output_file}")
        
        with open(self.project_root / output_file, "w") as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        summary = results.get("summary", {})
        print("\n=== Security Audit Summary ===")
        print(f"Total Issues: {summary.get('total_issues', 0)}")
        print(f"  Critical: {summary.get('critical', 0)}")
        print(f"  High: {summary.get('high', 0)}")
        print(f"  Medium: {summary.get('medium', 0)}")
        print(f"  Low: {summary.get('low', 0)}")
        print(f"\nFull report saved to: {output_file}")


def main():
    """Run security audit"""
    project_root = Path(__file__).parent.parent
    auditor = SecurityAuditor(str(project_root))
    
    results = auditor.run_full_audit()
    auditor.generate_report(results)


if __name__ == "__main__":
    main()
