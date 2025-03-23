from app.config import api_key_storing, base_config, config, config_manager, db_config, python-dotenv, scanning_profiles
from app.utils.decorators import error_handler  # Import the error_handler decorator
from typing import Dict, Any, List
from app.database import DatabaseManager  # Import DatabaseManager
from app.models import ScanResult, ScanStatus, Finding, SeverityLevel  # Import ScanResult, ScanStatus, Finding, and SeverityLevel
import asyncio  # Import asyncio
import logging  # Import logging
import aiohttp  # Import aiohttp
from datetime import datetime, timezone
import socket  # Import socket
import ssl  # Import ssl
from urllib.parse import urlparse  # Import urlparse

# Initialize logger
logger = logging.getLogger(__name__)

def __init__(self):
    """
    Initializes the ScanService with configuration settings.

    Attributes:
        max_concurrent_scans (int): The maximum number of scans that can run concurrently.
        scan_timeout (int): The timeout for each scan in seconds.
        active_scans (int): The current number of active scans.
    """
    self.max_concurrent_scans = config.get("MAX_CONCURRENT_SCANS")
    self.scan_timeout = config.get("SCAN_TIMEOUT_MINUTES") * 60
    self.active_scans = 0

@error_handler
async def start_scan(self, target_url: str, user_id: int) -> Dict[str, Any]:
    """Start a new vulnerability scan"""
    # Validate URL
    if not self._validate_url(target_url):
        return {"success": False, "message": "Invalid target URL"}

    # Check concurrent scan limit
    if self.active_scans >= self.max_concurrent_scans:
        return {
            "success": False,
            "message": "Maximum concurrent scan limit reached",
        }

    try:
        # Create scan record
        scan_id = self._generate_scan_id()
        with DatabaseManager.get_session() as session:
            scan = ScanResult(
                scan_id=scan_id,
                target_url=target_url,
                status=ScanStatus.PENDING,
                created_by=user_id,
            )
            session.add(scan)

        # Start async scan
        asyncio.create_task(self._run_scan(scan_id, target_url))

        logger.info(f"Scan started - ID: {scan_id}, Target: {target_url}")
        return {
            "success": True,
            "message": "Scan started successfully",
            "scan_id": scan_id,
        }

    except Exception as e:
        logger.error(f"Failed to start scan: {str(e)}", exc_info=True)
        return {"success": False, "message": f"Failed to start scan: {str(e)}"}

async def _run_scan(self, scan_id: str, target_url: str) -> None:
    """
    Run the actual scan operations.
    This method performs a series of security checks on the given target URL in parallel,
    collects the findings, and updates the scan status and results in the database.
    Args:
        scan_id (str): The unique identifier for the scan.
        target_url (str): The URL of the target to be scanned.
    Raises:
        Exception: If any error occurs during the scan process, it is logged and the scan status is set to FAILED.
    Returns:
        None
    """
    """Run the actual scan operations"""
    self.active_scans += 1
    try:
        with DatabaseManager.get_session() as session:
            scan = session.query(ScanResult).filter_by(scan_id=scan_id).first()
            scan.status = ScanStatus.RUNNING
        findings = []

        # Run security checks in parallel
        tasks = [
            self._check_security_headers(target_url),
            self._check_ssl_tls(target_url),
            self._check_common_vulnerabilities(target_url),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Scan error: {str(result)}", exc_info=True)
            else:
                findings.extend(result)

        # Save findings
        with DatabaseManager.get_session() as session:
            scan = session.query(ScanResult).filter_by(scan_id=scan_id).first()

            for finding_data in findings:
                finding = Finding(
                    scan_id=scan.id,
                    type=finding_data["type"],
                    severity=SeverityLevel(finding_data["severity"]),
                    description=finding_data["description"],
                    details=finding_data.get("details"),
                )
                session.add(finding)

            scan.status = ScanStatus.COMPLETED
            scan.total_findings = len(findings)
            scan.updated_at = datetime.now(timezone.utc)

        logger.info(f"Scan completed - ID: {scan_id}, Findings: {len(findings)}")

    except Exception as e:
        logger.error(f"Scan failed - ID: {scan_id}: {str(e)}", exc_info=True)
        with DatabaseManager.get_session() as session:
            scan = session.query(ScanResult).filter_by(scan_id=scan_id).first()
            scan.status = ScanStatus.FAILED

    finally:
        self.active_scans -= 1

headers_to_check = {
    "Content-Security-Policy": {
        "severity": "high",
        "description": "Content Security Policy (CSP) header is missing",
    },
    "Strict-Transport-Security": {
        "severity": "high",
        "description": "Strict Transport Security (HSTS) header is missing",
    },
    "X-Content-Type-Options": {
        "severity": "medium",
        "description": "X-Content-Type-Options header is missing",
    },
    "X-Frame-Options": {
        "severity": "medium",
        "description": "X-Frame-Options header is missing",
    },
    "X-XSS-Protection": {
        "severity": "medium",
        "description": "X-XSS-Protection header is missing",
    },
}

async def _check_security_headers(self, url: str) -> List[Dict[str, Any]]:
    findings = []
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response_headers = response.headers

            findings.extend(
                {
                    "type": "missing_security_header",
                    "severity": config["severity"],
                    "description": config["description"],
                    "details": f"The {header} header is missing from the response",
                }
                for header, config in headers_to_check.items()
                if header not in response_headers
            )
        except Exception as e:
            logger.error(f"Error checking security headers: {str(e)}", exc_info=True)
            findings.append(
                {
                    "type": "error",
                    "severity": "high",
                    "description": "Failed to check security headers",
                    "details": str(e),
                }
            )

        return findings
async def _check_ssl_tls(self, url: str) -> List[Dict[str, Any]]:
    findings = []
    try:
        hostname = urlparse(url).netloc
        context = ssl.create_default_context()

        with context.wrap_socket(socket.socket(), server_hostname=hostname) as sock:
            sock.connect((hostname, 443))
            cert = sock.getpeercert()

            # Check certificate expiration
            not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
            if not_after < datetime.now():
                findings.append(
                    {
                        "type": "ssl_certificate",
                        "severity": "critical",
                        "description": "SSL certificate has expired",
                        "details": f"Certificate expired on {not_after}",
                    }
                )

            # Check protocol version
            version = sock.version()
            if version < ssl.TLSVersion.TLSv1_2:
                findings.append(
                    {
                        "type": "ssl_protocol",
                        "severity": "high",
                        "description": "Outdated SSL/TLS protocol version",
                        "details": f"Using {version} - TLS 1.2 or higher recommended",
                    }
                )

    except Exception as e:
        logger.error(f"Error checking SSL/TLS: {str(e)}", exc_info=True)
        findings.append(
            {
                "type": "ssl_error",
                "severity": "high",
                "description": "Failed to check SSL/TLS configuration",
                "details": str(e),
            }
        )

    return findings

async def _check_common_vulnerabilities(self, url: str) -> List[Dict[str, Any]]:
    # Add actual vulnerability checks here
    # This is a placeholder for demonstration
    checks = [
        {
            "type": "sql_injection",
            "severity": "critical",
            "description": "Potential SQL Injection vulnerability",
            "details": "Input parameter vulnerable to SQL injection",
        },
        {
            "type": "xss",
            "severity": "high",
            "description": "Cross-Site Scripting (XSS) vulnerability",
            "details": "Reflected XSS vulnerability in search parameter",
        },
    ]
    return list(checks)

@staticmethod
def _validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

@staticmethod
@staticmethod
@error_handler
def get_scan_status(scan_id: str) -> Dict[str, Any]:
    """Get the status of a scan"""
    with DatabaseManager.get_session() as session:
        if (
            scan := session.query(ScanResult)
            .filter_by(scan_id=scan_id)
            .first()
        ):
            return {
                "success": True,
                "status": scan.status.value,
                "total_findings": scan.total_findings,
                "timestamp": scan.timestamp.isoformat(),
            }
        else:
            return {"success": False, "message": "Scan not found"}

@staticmethod
@error_handler
def get_scan_results(scan_id: str) -> Dict[str, Any]:
    """Get the results of a completed scan"""
    with DatabaseManager.get_session() as session:
        scan = session.query(ScanResult).filter_by(scan_id=scan_id).first()

        if not scan:
            return {"success": False, "message": "Scan not found"}

        if scan.status != ScanStatus.COMPLETED:
            return {"success": False, "message": f"Scan is {scan.status.value}"}

        findings = [finding.to_dict() for finding in scan.findings]

        return {"success": True, "scan": scan.to_dict(), "findings": findings}
