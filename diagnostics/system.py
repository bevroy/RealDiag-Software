"""
System diagnostics module
"""

import platform
import psutil
from datetime import datetime
from config import Config


class SystemDiagnostics:
    """System-level diagnostic checks"""
    
    def __init__(self):
        self.config = Config()
    
    def get_system_info(self):
        """Get basic system information"""
        info = {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'processor': platform.processor(),
            'timestamp': datetime.now().isoformat()
        }
        return info
    
    def check_cpu(self):
        """Check CPU usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        status = "OK"
        if cpu_percent > self.config.CPU_WARNING_THRESHOLD:
            status = "WARNING"
        
        return {
            'cpu_percent': cpu_percent,
            'cpu_count': cpu_count,
            'status': status,
            'threshold': self.config.CPU_WARNING_THRESHOLD
        }
    
    def check_memory(self):
        """Check memory usage"""
        memory = psutil.virtual_memory()
        
        status = "OK"
        if memory.percent > self.config.MEMORY_WARNING_THRESHOLD:
            status = "WARNING"
        
        return {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent,
            'used': memory.used,
            'free': memory.free,
            'status': status,
            'threshold': self.config.MEMORY_WARNING_THRESHOLD
        }
    
    def check_disk(self):
        """Check disk usage"""
        disk = psutil.disk_usage('/')
        
        status = "OK"
        if disk.percent > self.config.DISK_WARNING_THRESHOLD:
            status = "WARNING"
        
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent,
            'status': status,
            'threshold': self.config.DISK_WARNING_THRESHOLD
        }
    
    def run_full_diagnostic(self):
        """Run all system diagnostics"""
        return {
            'system_info': self.get_system_info(),
            'cpu': self.check_cpu(),
            'memory': self.check_memory(),
            'disk': self.check_disk()
        }
