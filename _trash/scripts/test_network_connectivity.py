"""
Network Connectivity Diagnostic Tool
Tests various endpoints to diagnose network/firewall issues
"""

import sys
import socket
import ssl
import time
import io
from pathlib import Path

# Force UTF-8 encoding for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_dns(host):
    """Test DNS resolution"""
    try:
        ip = socket.gethostbyname(host)
        return True, ip
    except socket.gaierror as e:
        return False, str(e)

def test_tcp_connection(host, port, timeout=5):
    """Test TCP connection"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0, result
    except Exception as e:
        return False, str(e)

def test_ssl_connection(host, port, timeout=5):
    """Test SSL/TLS connection"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                return True, ssock.version()
    except socket.timeout:
        return False, "Connection timeout"
    except ssl.SSLError as e:
        return False, f"SSL Error: {e}"
    except Exception as e:
        return False, str(e)

def test_http_request(url, timeout=5):
    """Test HTTP/HTTPS request"""
    try:
        import requests
        response = requests.get(url, timeout=timeout)
        return True, response.status_code
    except requests.exceptions.Timeout:
        return False, "Request timeout"
    except requests.exceptions.ConnectionError as e:
        return False, f"Connection error: {e}"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("GRACE Network Connectivity Diagnostic")
    print("=" * 70)
    print()
    
    # Test endpoints
    endpoints = [
        {
            'name': 'DuckDuckGo (HTML endpoint)',
            'dns': 'html.duckduckgo.com',
            'tcp_host': 'html.duckduckgo.com',
            'tcp_port': 443,
            'ssl_host': 'html.duckduckgo.com',
            'ssl_port': 443,
            'http_url': 'https://html.duckduckgo.com',
        },
        {
            'name': 'DuckDuckGo (Main site)',
            'dns': 'duckduckgo.com',
            'tcp_host': 'duckduckgo.com',
            'tcp_port': 443,
            'ssl_host': 'duckduckgo.com',
            'ssl_port': 443,
            'http_url': 'https://duckduckgo.com',
        },
        {
            'name': 'Google Search API',
            'dns': 'www.googleapis.com',
            'tcp_host': 'www.googleapis.com',
            'tcp_port': 443,
            'ssl_host': 'www.googleapis.com',
            'ssl_port': 443,
            'http_url': 'https://www.googleapis.com/customsearch/v1',
        },
        {
            'name': 'Google (Main)',
            'dns': 'www.google.com',
            'tcp_host': 'www.google.com',
            'tcp_port': 443,
            'ssl_host': 'www.google.com',
            'ssl_port': 443,
            'http_url': 'https://www.google.com',
        },
        {
            'name': 'Cloudflare DNS',
            'dns': '1.1.1.1',
            'tcp_host': '1.1.1.1',
            'tcp_port': 443,
            'ssl_host': None,
            'http_url': None,
        },
    ]
    
    results = {}
    
    for endpoint in endpoints:
        print(f"Testing: {endpoint['name']}")
        print("-" * 70)
        
        result = {
            'dns': None,
            'tcp': None,
            'ssl': None,
            'http': None,
        }
        
        # DNS Test
        if endpoint['dns']:
            print(f"  [1/4] DNS resolution ({endpoint['dns']})...", end=" ")
            success, info = test_dns(endpoint['dns'])
            result['dns'] = (success, info)
            if success:
                print(f"✓ OK ({info})")
            else:
                print(f"✗ FAILED ({info})")
        
        # TCP Test
        if endpoint['tcp_host'] and endpoint['tcp_port']:
            print(f"  [2/4] TCP connection ({endpoint['tcp_host']}:{endpoint['tcp_port']})...", end=" ")
            success, info = test_tcp_connection(endpoint['tcp_host'], endpoint['tcp_port'])
            result['tcp'] = (success, info)
            if success:
                print(f"✓ OK")
            else:
                print(f"✗ FAILED (code: {info})")
        
        # SSL Test
        if endpoint['ssl_host'] and endpoint['ssl_port']:
            print(f"  [3/4] SSL/TLS handshake ({endpoint['ssl_host']}:{endpoint['ssl_port']})...", end=" ")
            success, info = test_ssl_connection(endpoint['ssl_host'], endpoint['ssl_port'])
            result['ssl'] = (success, info)
            if success:
                print(f"✓ OK ({info})")
            else:
                print(f"✗ FAILED ({info})")
        
        # HTTP Test
        if endpoint['http_url']:
            print(f"  [4/4] HTTP request ({endpoint['http_url']})...", end=" ")
            success, info = test_http_request(endpoint['http_url'])
            result['http'] = (success, info)
            if success:
                print(f"✓ OK (status: {info})")
            else:
                print(f"✗ FAILED ({info})")
        
        print()
        results[endpoint['name']] = result
    
    # Summary
    print("=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)
    print()
    
    # Check DuckDuckGo
    ddg_html = results.get('DuckDuckGo (HTML endpoint)', {})
    ddg_main = results.get('DuckDuckGo (Main site)', {})
    google_api = results.get('Google Search API', {})
    
    print("DuckDuckGo Status:")
    if ddg_html.get('ssl') and ddg_html['ssl'][0]:
        print("  ✓ DuckDuckGo HTML endpoint is accessible")
    elif ddg_html.get('tcp') and ddg_html['tcp'][0]:
        print("  ⚠ Can reach DuckDuckGo but SSL handshake fails")
        print("    → Possible SSL interception or certificate issue")
    elif ddg_html.get('dns') and ddg_html['dns'][0]:
        print("  ✗ DNS works but connection blocked")
        print("    → Firewall or network blocking port 443 to DuckDuckGo")
    else:
        print("  ✗ Complete block - DNS or network level")
        print("    → ISP/firewall blocking DuckDuckGo entirely")
    print()
    
    print("Google API Status:")
    if google_api.get('ssl') and google_api['ssl'][0]:
        print("  ✓ Google Search API is accessible")
        print("    → You can use Google Custom Search API")
        print("    → Complete setup at: https://programmablesearchengine.google.com/")
    elif google_api.get('tcp') and google_api['tcp'][0]:
        print("  ⚠ Can reach Google but SSL handshake fails")
    else:
        print("  ✗ Google API also blocked")
        print("    → You may be behind a restrictive proxy/firewall")
    print()
    
    # Recommendations
    print("=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print()
    
    if google_api.get('ssl') and google_api['ssl'][0]:
        print("✓ RECOMMENDATION: Use Google Search API")
        print()
        print("  Google's API endpoints are accessible.")
        print("  Complete the setup:")
        print()
        print("  1. Get Search Engine ID:")
        print("     https://programmablesearchengine.google.com/")
        print()
        print("  2. Add to .env:")
        print("     GOOGLE_SEARCH_API_KEY=AIzaSyDC5fDHP42rV4g_PO-QY76aX63N_qMnNwE")
        print("     GOOGLE_SEARCH_ENGINE_ID=your-id-here")
        print()
        print("  3. Restart Grace")
        print()
    elif not (ddg_html.get('ssl') and ddg_html['ssl'][0]):
        print("⚠ ISSUE: Network/Firewall Restrictions Detected")
        print()
        print("  DuckDuckGo is blocked at network level.")
        print()
        print("  Possible solutions:")
        print("  1. Add firewall exception for Python")
        print("  2. Configure proxy settings if behind corporate firewall")
        print("  3. Use VPN to bypass restrictions")
        print("  4. Contact network administrator")
        print()
        print("  For Grace:")
        print("  - Grace can still work with cached data")
        print("  - Local knowledge base remains functional")
        print("  - Disable web search errors with: DISABLE_WEB_SEARCH=true in .env")
        print()
    
    print("=" * 70)
    print()

if __name__ == "__main__":
    main()
