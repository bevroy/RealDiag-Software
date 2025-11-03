"""
Configuration module for RealDiag Software
"""

import os
from pathlib import Path

class Config:
    """Configuration settings for the diagnostic tool"""
    
    # Application info
    APP_NAME = "RealDiag"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Real Time Diagnostic Assistant Software"
    
    # Diagnostic settings
    CHECK_INTERVAL = 5  # seconds
    REPORT_DIR = Path("reports")
    LOG_FILE = Path("realdiag.log")
    
    # System thresholds
    CPU_WARNING_THRESHOLD = 80  # percentage
    MEMORY_WARNING_THRESHOLD = 85  # percentage
    DISK_WARNING_THRESHOLD = 90  # percentage
    
    # Network settings
    DEFAULT_TEST_HOST = "8.8.8.8"
    NETWORK_TIMEOUT = 5  # seconds
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.REPORT_DIR.mkdir(exist_ok=True)
