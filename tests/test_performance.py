"""
Unit tests for performance monitoring module
"""

import unittest
from diagnostics.performance import PerformanceMonitor


class TestPerformanceMonitor(unittest.TestCase):
    """Test cases for PerformanceMonitor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = PerformanceMonitor()
    
    def test_get_uptime(self):
        """Test getting system uptime"""
        uptime = self.monitor.get_uptime()
        
        # Check that all expected keys are present
        self.assertIn('boot_time', uptime)
        self.assertIn('uptime_seconds', uptime)
        self.assertIn('uptime_hours', uptime)
        self.assertIn('uptime_days', uptime)
        
        # Check that values are reasonable
        self.assertGreater(uptime['uptime_seconds'], 0)
        self.assertGreater(uptime['uptime_hours'], 0)
        self.assertGreaterEqual(uptime['uptime_days'], 0)
    
    def test_get_cpu_times(self):
        """Test getting CPU times"""
        cpu_times = self.monitor.get_cpu_times()
        
        # Check that all expected keys are present
        self.assertIn('user', cpu_times)
        self.assertIn('system', cpu_times)
        self.assertIn('idle', cpu_times)
        
        # Check that values are non-negative
        self.assertGreaterEqual(cpu_times['user'], 0)
        self.assertGreaterEqual(cpu_times['system'], 0)
        self.assertGreaterEqual(cpu_times['idle'], 0)
    
    def test_get_process_count(self):
        """Test getting process count"""
        proc_count = self.monitor.get_process_count()
        
        # Check that all expected keys are present
        self.assertIn('total_processes', proc_count)
        self.assertIn('timestamp', proc_count)
        
        # Check that we have at least some processes
        self.assertGreater(proc_count['total_processes'], 0)
    
    def test_get_top_processes(self):
        """Test getting top processes"""
        top_procs = self.monitor.get_top_processes(limit=5)
        
        # Check that we got a list
        self.assertIsInstance(top_procs, list)
        
        # Check that we got at most 5 processes
        self.assertLessEqual(len(top_procs), 5)
        
        # If we have processes, check their structure
        if len(top_procs) > 0:
            proc = top_procs[0]
            self.assertIn('pid', proc)
            self.assertIn('name', proc)
            self.assertIn('cpu_percent', proc)
            self.assertIn('memory_percent', proc)
    
    def test_get_load_average(self):
        """Test getting load average"""
        load = self.monitor.get_load_average()
        
        # Check that all expected keys are present
        self.assertIn('load_1min', load)
        self.assertIn('load_5min', load)
        self.assertIn('load_15min', load)
        
        # Values might be None on Windows, but should be present on Unix
        # Just check that the keys exist
    
    def test_run_full_diagnostic(self):
        """Test running full performance diagnostic"""
        results = self.monitor.run_full_diagnostic()
        
        # Check that all diagnostic sections are present
        self.assertIn('uptime', results)
        self.assertIn('cpu_times', results)
        self.assertIn('process_count', results)
        self.assertIn('top_processes', results)
        self.assertIn('load_average', results)
        self.assertIn('timestamp', results)
        
        # Verify each section has data
        self.assertIsNotNone(results['uptime'])
        self.assertIsNotNone(results['cpu_times'])
        self.assertIsNotNone(results['process_count'])
        self.assertIsNotNone(results['top_processes'])
        self.assertIsNotNone(results['load_average'])


if __name__ == '__main__':
    unittest.main()
