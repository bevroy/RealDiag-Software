"""
Network diagnostics module
"""

import socket
import psutil
from datetime import datetime
from config import Config


class NetworkDiagnostics:
    """Network-level diagnostic checks"""
    
    def __init__(self):
        self.config = Config()
    
    def check_connectivity(self, host=None):
        """Check network connectivity to a host"""
        if host is None:
            host = self.config.DEFAULT_TEST_HOST
        
        try:
            socket.setdefaulttimeout(self.config.NETWORK_TIMEOUT)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((host, 53))
                return {
                    'host': host,
                    'status': 'Connected',
                    'reachable': True,
                    'timestamp': datetime.now().isoformat()
                }
            finally:
                sock.close()
        except socket.error as e:
            return {
                'host': host,
                'status': 'Disconnected',
                'reachable': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_network_interfaces(self):
        """Get network interface information"""
        interfaces = psutil.net_if_addrs()
        interface_stats = psutil.net_if_stats()
        
        result = {}
        for interface_name, addresses in interfaces.items():
            result[interface_name] = {
                'addresses': [],
                'is_up': interface_stats.get(interface_name, {}).isup if hasattr(interface_stats.get(interface_name, {}), 'isup') else None
            }
            
            for addr in addresses:
                result[interface_name]['addresses'].append({
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                })
        
        return result
    
    def get_network_stats(self):
        """Get network I/O statistics"""
        net_io = psutil.net_io_counters()
        
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errin': net_io.errin,
            'errout': net_io.errout,
            'dropin': net_io.dropin,
            'dropout': net_io.dropout
        }
    
    def run_full_diagnostic(self):
        """Run all network diagnostics"""
        return {
            'connectivity': self.check_connectivity(),
            'interfaces': self.get_network_interfaces(),
            'stats': self.get_network_stats(),
            'timestamp': datetime.now().isoformat()
        }
