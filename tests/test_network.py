"""
Unit tests for network diagnostics module
"""

import unittest
from diagnostics.network import NetworkDiagnostics


class TestNetworkDiagnostics(unittest.TestCase):
    """Test cases for NetworkDiagnostics class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.diag = NetworkDiagnostics()
    
    def test_check_connectivity(self):
        """Test network connectivity check"""
        result = self.diag.check_connectivity()
        
        # Check that all expected keys are present
        self.assertIn('host', result)
        self.assertIn('status', result)
        self.assertIn('reachable', result)
        self.assertIn('timestamp', result)
        
        # Check that status is appropriate
        self.assertIsInstance(result['reachable'], bool)
        if result['reachable']:
            self.assertEqual(result['status'], 'Connected')
        else:
            self.assertEqual(result['status'], 'Disconnected')
            self.assertIn('error', result)
    
    def test_get_network_interfaces(self):
        """Test getting network interfaces"""
        interfaces = self.diag.get_network_interfaces()
        
        # Check that we have at least one interface
        self.assertIsInstance(interfaces, dict)
        self.assertGreater(len(interfaces), 0)
        
        # Check structure of interface data
        for interface_name, interface_data in interfaces.items():
            self.assertIn('addresses', interface_data)
            self.assertIsInstance(interface_data['addresses'], list)
    
    def test_get_network_stats(self):
        """Test getting network statistics"""
        stats = self.diag.get_network_stats()
        
        # Check that all expected keys are present
        self.assertIn('bytes_sent', stats)
        self.assertIn('bytes_recv', stats)
        self.assertIn('packets_sent', stats)
        self.assertIn('packets_recv', stats)
        self.assertIn('errin', stats)
        self.assertIn('errout', stats)
        
        # Check that values are non-negative
        self.assertGreaterEqual(stats['bytes_sent'], 0)
        self.assertGreaterEqual(stats['bytes_recv'], 0)
        self.assertGreaterEqual(stats['packets_sent'], 0)
        self.assertGreaterEqual(stats['packets_recv'], 0)
    
    def test_run_full_diagnostic(self):
        """Test running full network diagnostic"""
        results = self.diag.run_full_diagnostic()
        
        # Check that all diagnostic sections are present
        self.assertIn('connectivity', results)
        self.assertIn('interfaces', results)
        self.assertIn('stats', results)
        self.assertIn('timestamp', results)
        
        # Verify each section has data
        self.assertIsNotNone(results['connectivity'])
        self.assertIsNotNone(results['interfaces'])
        self.assertIsNotNone(results['stats'])


if __name__ == '__main__':
    unittest.main()
