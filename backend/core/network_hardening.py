"""
Network Hardening & Issue Detection
Handles common networking problems beyond just port conflicts
"""

import socket
import logging
import psutil
from typing import Dict, List, Any, Optional
from datetime import datetime
import platform

logger = logging.getLogger(__name__)


class NetworkHardening:
    """
    Detects and handles common networking issues:
    - IPv4/IPv6 conflicts
    - Firewall blocking
    - Socket reuse (TIME_WAIT)
    - File descriptor limits
    - Network interface failures
    - Connection limits
    - SSL/TLS issues
    - DNS resolution
    """
    
    def __init__(self):
        self.os_type = platform.system()
        self.issues_detected = []
        self.warnings = []
    
    def check_all_networking_issues(self, port: int) -> Dict[str, Any]:
        """
        Comprehensive network check before binding port
        Returns issues and recommendations
        """
        
        logger.info(f"[NETWORK-HARDENING] Running comprehensive checks for port {port}")
        
        checks = {
            'ipv4_available': self._check_ipv4(),
            'ipv6_available': self._check_ipv6(),
            'socket_reuse': self._check_socket_reuse_option(),
            'file_descriptors': self._check_file_descriptor_limits(),
            'network_interfaces': self._check_network_interfaces(),
            'firewall': self._check_firewall_rules(port),
            'time_wait_sockets': self._check_time_wait_sockets(port),
            'connection_limits': self._check_connection_limits(),
            'dns_resolution': self._check_dns_resolution(),
        }
        
        # Count issues
        critical_issues = [k for k, v in checks.items() if isinstance(v, dict) and v.get('status') == 'error']
        warnings = [k for k, v in checks.items() if isinstance(v, dict) and v.get('status') == 'warning']
        
        status = 'healthy'
        if critical_issues:
            status = 'critical'
        elif warnings:
            status = 'warning'
        
        logger.info(f"[NETWORK-HARDENING] Status: {status} ({len(critical_issues)} critical, {len(warnings)} warnings)")
        
        return {
            'status': status,
            'critical_issues': critical_issues,
            'warnings': warnings,
            'checks': checks,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _check_ipv4(self) -> Dict[str, Any]:
        """Check if IPv4 is available"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.close()
            return {'status': 'ok', 'available': True}
        except Exception as e:
            return {'status': 'error', 'available': False, 'error': str(e)}
    
    def _check_ipv6(self) -> Dict[str, Any]:
        """Check if IPv6 is available"""
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.close()
            return {'status': 'ok', 'available': True}
        except Exception as e:
            return {'status': 'warning', 'available': False, 'note': 'IPv6 not available (not critical)'}
    
    def _check_socket_reuse_option(self) -> Dict[str, Any]:
        """Check SO_REUSEADDR and SO_REUSEPORT support"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Check SO_REUSEADDR
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Check SO_REUSEPORT (not available on Windows)
            reuse_port_available = False
            if hasattr(socket, 'SO_REUSEPORT'):
                try:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                    reuse_port_available = True
                except:
                    pass
            
            sock.close()
            
            return {
                'status': 'ok',
                'SO_REUSEADDR': True,
                'SO_REUSEPORT': reuse_port_available,
                'note': 'Socket reuse options available'
            }
        except Exception as e:
            return {'status': 'warning', 'error': str(e)}
    
    def _check_file_descriptor_limits(self) -> Dict[str, Any]:
        """Check file descriptor limits (max connections)"""
        try:
            if self.os_type == 'Windows':
                # Windows doesn't have ulimit, but has handle limits
                process = psutil.Process()
                num_handles = process.num_handles()
                
                return {
                    'status': 'ok',
                    'current_handles': num_handles,
                    'platform': 'Windows',
                    'note': 'Windows handle tracking available'
                }
            else:
                # Unix-like systems
                import resource
                soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
                
                status = 'ok'
                if soft < 1024:
                    status = 'warning'
                
                return {
                    'status': status,
                    'soft_limit': soft,
                    'hard_limit': hard,
                    'platform': self.os_type,
                    'recommendation': 'Increase if < 1024' if soft < 1024 else 'OK'
                }
        except Exception as e:
            return {'status': 'warning', 'error': str(e)}
    
    def _check_network_interfaces(self) -> Dict[str, Any]:
        """Check available network interfaces"""
        try:
            interfaces = psutil.net_if_addrs()
            
            # Check if localhost interface exists
            has_localhost = any('127.0.0.1' in str(addrs) for addrs in interfaces.values() for addr in addrs)
            
            # Check if external interfaces exist
            external_interfaces = []
            for iface_name, addrs in interfaces.items():
                for addr in addrs:
                    if hasattr(addr, 'address') and addr.address not in ['127.0.0.1', '::1']:
                        external_interfaces.append(iface_name)
                        break
            
            status = 'ok' if has_localhost else 'error'
            
            return {
                'status': status,
                'total_interfaces': len(interfaces),
                'has_localhost': has_localhost,
                'external_interfaces': len(set(external_interfaces)),
                'interface_names': list(interfaces.keys())
            }
        except Exception as e:
            return {'status': 'warning', 'error': str(e)}
    
    def _check_firewall_rules(self, port: int) -> Dict[str, Any]:
        """Check if firewall might block the port"""
        try:
            # Try to bind and listen briefly
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                sock.bind(('0.0.0.0', port))
                sock.listen(1)
                sock.close()
                
                return {
                    'status': 'ok',
                    'port': port,
                    'can_bind': True,
                    'note': 'Port can be bound (firewall likely OK)'
                }
            except OSError as e:
                sock.close()
                
                if 'in use' in str(e).lower():
                    return {
                        'status': 'ok',
                        'port': port,
                        'in_use': True,
                        'note': 'Port in use (expected if Grace is running)'
                    }
                else:
                    return {
                        'status': 'warning',
                        'port': port,
                        'can_bind': False,
                        'error': str(e),
                        'recommendation': 'Check firewall rules'
                    }
        except Exception as e:
            return {'status': 'warning', 'error': str(e)}
    
    def _check_time_wait_sockets(self, port: int) -> Dict[str, Any]:
        """Check for sockets in TIME_WAIT state on this port"""
        try:
            connections = psutil.net_connections()
            
            time_wait_count = 0
            for conn in connections:
                if conn.laddr and conn.laddr.port == port:
                    if conn.status == 'TIME_WAIT':
                        time_wait_count += 1
            
            status = 'ok'
            if time_wait_count > 10:
                status = 'warning'
            
            return {
                'status': status,
                'time_wait_count': time_wait_count,
                'note': 'Normal if < 10' if time_wait_count <= 10 else 'High TIME_WAIT count',
                'recommendation': 'Consider SO_REUSEADDR' if time_wait_count > 10 else 'OK'
            }
        except Exception as e:
            return {'status': 'info', 'note': 'Could not check TIME_WAIT sockets'}
    
    def _check_connection_limits(self) -> Dict[str, Any]:
        """Check system connection limits"""
        try:
            # Get current connection count
            connections = psutil.net_connections()
            total_connections = len(connections)
            
            # Count by state
            established = sum(1 for c in connections if c.status == 'ESTABLISHED')
            listen = sum(1 for c in connections if c.status == 'LISTEN')
            
            status = 'ok'
            if total_connections > 10000:
                status = 'warning'
            
            return {
                'status': status,
                'total_connections': total_connections,
                'established': established,
                'listening': listen,
                'recommendation': 'High connection count' if total_connections > 10000 else 'OK'
            }
        except Exception as e:
            return {'status': 'info', 'error': str(e)}
    
    def _check_dns_resolution(self) -> Dict[str, Any]:
        """Check DNS resolution works"""
        try:
            # Try to resolve localhost
            localhost_ip = socket.gethostbyname('localhost')
            
            # Try to resolve hostname
            hostname = socket.gethostname()
            hostname_ip = socket.gethostbyname(hostname)
            
            return {
                'status': 'ok',
                'localhost': localhost_ip,
                'hostname': hostname,
                'hostname_ip': hostname_ip
            }
        except Exception as e:
            return {
                'status': 'warning',
                'error': str(e),
                'recommendation': 'Check /etc/hosts or DNS settings'
            }
    
    def apply_socket_hardening(self, sock: socket.socket) -> Dict[str, Any]:
        """
        Apply hardening options to a socket
        - Enable SO_REUSEADDR (avoid TIME_WAIT issues)
        - Set timeouts
        - Configure buffers
        """
        
        applied = []
        
        try:
            # SO_REUSEADDR - Allows reuse of local addresses
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            applied.append('SO_REUSEADDR')
        except:
            pass
        
        try:
            # SO_KEEPALIVE - Detect dead connections
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            applied.append('SO_KEEPALIVE')
        except:
            pass
        
        try:
            # TCP_NODELAY - Disable Nagle's algorithm for low latency
            if hasattr(socket, 'TCP_NODELAY'):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                applied.append('TCP_NODELAY')
        except:
            pass
        
        try:
            # Set socket timeout (prevent hanging)
            sock.settimeout(30.0)
            applied.append('TIMEOUT=30s')
        except:
            pass
        
        try:
            # Increase send/receive buffer sizes
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
            applied.append('BUFFERS=64KB')
        except:
            pass
        
        logger.info(f"[NETWORK-HARDENING] Applied socket options: {', '.join(applied)}")
        
        return {
            'hardening_applied': applied,
            'count': len(applied)
        }
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get current network statistics"""
        try:
            net_io = psutil.net_io_counters()
            connections = psutil.net_connections()
            
            return {
                'io': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv,
                    'errors_in': net_io.errin,
                    'errors_out': net_io.errout,
                    'dropped_in': net_io.dropin,
                    'dropped_out': net_io.dropout
                },
                'connections': {
                    'total': len(connections),
                    'by_status': self._count_connection_states(connections)
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _count_connection_states(self, connections: List) -> Dict[str, int]:
        """Count connections by state"""
        states = {}
        for conn in connections:
            state = conn.status
            states[state] = states.get(state, 0) + 1
        return states
    
    def detect_port_exhaustion(self) -> Dict[str, Any]:
        """Detect if system is running out of ephemeral ports"""
        try:
            connections = psutil.net_connections()
            
            # Count connections by local port
            port_usage = {}
            for conn in connections:
                if conn.laddr:
                    port = conn.laddr.port
                    port_usage[port] = port_usage.get(port, 0) + 1
            
            # Ephemeral port range (typically 49152-65535)
            ephemeral_ports = [p for p in port_usage.keys() if 49152 <= p <= 65535]
            ephemeral_used = len(ephemeral_ports)
            ephemeral_total = 65535 - 49152 + 1
            usage_percent = (ephemeral_used / ephemeral_total) * 100
            
            status = 'ok'
            if usage_percent > 80:
                status = 'critical'
            elif usage_percent > 60:
                status = 'warning'
            
            return {
                'status': status,
                'ephemeral_ports_used': ephemeral_used,
                'ephemeral_ports_total': ephemeral_total,
                'usage_percent': usage_percent,
                'recommendation': 'Increase TIME_WAIT timeout' if usage_percent > 60 else 'OK'
            }
        except Exception as e:
            return {'status': 'info', 'error': str(e)}
    
    def check_ssl_readiness(self) -> Dict[str, Any]:
        """Check if SSL/TLS is configured properly"""
        try:
            import ssl
            
            # Check SSL library version
            ssl_version = ssl.OPENSSL_VERSION
            
            # Check if certificates exist
            cert_paths = [
                Path('config/ssl/cert.pem'),
                Path('config/ssl/key.pem'),
                Path('/etc/ssl/certs'),
            ]
            
            certs_found = [str(p) for p in cert_paths if p.exists()]
            
            return {
                'status': 'info',
                'ssl_version': ssl_version,
                'certificates_found': len(certs_found),
                'cert_paths': certs_found,
                'note': 'SSL available for HTTPS if needed'
            }
        except Exception as e:
            return {'status': 'info', 'note': 'SSL check not critical'}
    
    def recommend_uvicorn_config(self, port: int) -> Dict[str, Any]:
        """
        Recommend uvicorn configuration based on network checks
        """
        
        checks = self.check_all_networking_issues(port)
        
        config = {
            'host': '0.0.0.0',  # Bind to all interfaces
            'port': port,
            'workers': 1,  # Single worker for development
            'limit_concurrency': 1000,  # Max concurrent connections
            'limit_max_requests': 0,  # No request limit
            'timeout_keep_alive': 5,  # Keep-alive timeout
            'backlog': 2048,  # Connection backlog
        }
        
        recommendations = []
        
        # Adjust based on checks
        if checks['status'] == 'critical':
            recommendations.append('Fix critical issues before starting')
        
        if checks['status'] == 'warning':
            recommendations.append('Monitor warnings, but safe to start')
        
        # Check connection limits
        fd_check = checks['checks'].get('file_descriptors', {})
        if isinstance(fd_check, dict):
            if fd_check.get('soft_limit', 1024) < 1024:
                recommendations.append('Increase file descriptor limit (ulimit -n 4096)')
        
        # Check TIME_WAIT
        time_wait = checks['checks'].get('time_wait_sockets', {})
        if isinstance(time_wait, dict) and time_wait.get('time_wait_count', 0) > 10:
            recommendations.append('High TIME_WAIT count - ensure SO_REUSEADDR is enabled')
            config['backlog'] = 4096  # Increase backlog
        
        return {
            'recommended_config': config,
            'recommendations': recommendations,
            'network_status': checks['status']
        }


# Global instance
network_hardening = NetworkHardening()
