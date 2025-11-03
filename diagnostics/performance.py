"""
Performance monitoring module
"""

import psutil
import time
from datetime import datetime
from config import Config


class PerformanceMonitor:
    """Real-time performance monitoring"""
    
    def __init__(self):
        self.config = Config()
        self.start_time = time.time()
    
    def get_uptime(self):
        """Get system uptime"""
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        
        return {
            'boot_time': datetime.fromtimestamp(boot_time).isoformat(),
            'uptime_seconds': uptime_seconds,
            'uptime_hours': uptime_seconds / 3600,
            'uptime_days': uptime_seconds / 86400
        }
    
    def get_cpu_times(self):
        """Get detailed CPU times"""
        cpu_times = psutil.cpu_times()
        
        return {
            'user': cpu_times.user,
            'system': cpu_times.system,
            'idle': cpu_times.idle
        }
    
    def get_process_count(self):
        """Get count of running processes"""
        return {
            'total_processes': len(psutil.pids()),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_top_processes(self, limit=5):
        """Get top processes by CPU usage"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                processes.append({
                    'pid': proc_info['pid'],
                    'name': proc_info['name'],
                    'cpu_percent': proc_info['cpu_percent'],
                    'memory_percent': proc_info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'] if x['cpu_percent'] else 0, reverse=True)
        
        return processes[:limit]
    
    def get_load_average(self):
        """Get system load average (Unix-like systems)"""
        try:
            load1, load5, load15 = psutil.getloadavg()
            return {
                'load_1min': load1,
                'load_5min': load5,
                'load_15min': load15
            }
        except (AttributeError, OSError):
            # Not available on Windows
            return {
                'load_1min': None,
                'load_5min': None,
                'load_15min': None,
                'note': 'Load average not available on this platform'
            }
    
    def run_full_diagnostic(self):
        """Run all performance diagnostics"""
        return {
            'uptime': self.get_uptime(),
            'cpu_times': self.get_cpu_times(),
            'process_count': self.get_process_count(),
            'top_processes': self.get_top_processes(),
            'load_average': self.get_load_average(),
            'timestamp': datetime.now().isoformat()
        }
