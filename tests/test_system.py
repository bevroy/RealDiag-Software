"""
Unit tests for system diagnostics module
"""

import unittest
from diagnostics.system import SystemDiagnostics


class TestSystemDiagnostics(unittest.TestCase):
    """Test cases for SystemDiagnostics class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.diag = SystemDiagnostics()
    
    def test_get_system_info(self):
        """Test getting system information"""
        info = self.diag.get_system_info()
        
        # Check that all expected keys are present
        self.assertIn('platform', info)
        self.assertIn('platform_release', info)
        self.assertIn('architecture', info)
        self.assertIn('hostname', info)
        self.assertIn('processor', info)
        self.assertIn('timestamp', info)
        
        # Check that values are not empty
        self.assertIsNotNone(info['platform'])
        self.assertIsNotNone(info['hostname'])
    
    def test_check_cpu(self):
        """Test CPU diagnostics"""
        cpu = self.diag.check_cpu()
        
        # Check that all expected keys are present
        self.assertIn('cpu_percent', cpu)
        self.assertIn('cpu_count', cpu)
        self.assertIn('status', cpu)
        self.assertIn('threshold', cpu)
        
        # Check value ranges
        self.assertGreaterEqual(cpu['cpu_percent'], 0)
        self.assertLessEqual(cpu['cpu_percent'], 100)
        self.assertGreater(cpu['cpu_count'], 0)
        self.assertIn(cpu['status'], ['OK', 'WARNING'])
    
    def test_check_memory(self):
        """Test memory diagnostics"""
        memory = self.diag.check_memory()
        
        # Check that all expected keys are present
        self.assertIn('total', memory)
        self.assertIn('available', memory)
        self.assertIn('percent', memory)
        self.assertIn('used', memory)
        self.assertIn('status', memory)
        
        # Check value ranges
        self.assertGreater(memory['total'], 0)
        self.assertGreaterEqual(memory['percent'], 0)
        self.assertLessEqual(memory['percent'], 100)
        self.assertIn(memory['status'], ['OK', 'WARNING'])
    
    def test_check_disk(self):
        """Test disk diagnostics"""
        disk = self.diag.check_disk()
        
        # Check that all expected keys are present
        self.assertIn('total', disk)
        self.assertIn('used', disk)
        self.assertIn('free', disk)
        self.assertIn('percent', disk)
        self.assertIn('status', disk)
        
        # Check value ranges
        self.assertGreater(disk['total'], 0)
        self.assertGreaterEqual(disk['percent'], 0)
        self.assertLessEqual(disk['percent'], 100)
        self.assertIn(disk['status'], ['OK', 'WARNING'])
    
    def test_run_full_diagnostic(self):
        """Test running full system diagnostic"""
        results = self.diag.run_full_diagnostic()
        
        # Check that all diagnostic sections are present
        self.assertIn('system_info', results)
        self.assertIn('cpu', results)
        self.assertIn('memory', results)
        self.assertIn('disk', results)
        
        # Verify each section has data
        self.assertIsNotNone(results['system_info'])
        self.assertIsNotNone(results['cpu'])
        self.assertIsNotNone(results['memory'])
        self.assertIsNotNone(results['disk'])


if __name__ == '__main__':
    unittest.main()
