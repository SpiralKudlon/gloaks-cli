import socket
import requests
import concurrent.futures

def get_ip(target):
    try:
        ip = socket.gethostbyname(target)
        return ip
    except socket.gaierror:
        return None

def scan_headers(target):
    """Returns a dictionary of HTTP headers."""
    try:
        response = requests.get(f"http://{target}", timeout=5)
        return dict(response.headers)
    except requests.exceptions.RequestException:
        return None

def check_port(target_ip, port):
    """Helper function to check a single port."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex((target_ip, port))
    sock.close()
    if result == 0:
        return port
    return None

import config

def scan_ports(target_ip, ports=None):
    """Returns a list of open ports using concurrent scanning."""
    if ports is None:
        ports = config.DEFAULT_PORTS
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_port = {executor.submit(check_port, target_ip, port): port for port in ports}
        for future in concurrent.futures.as_completed(future_to_port):
            port = future_to_port[future]
            try:
                result = future.result()
                if result:
                    open_ports.append(result)
            except Exception:
                pass
    return sorted(open_ports)

def geo_locate(ip):
    """Returns a dictionary of geolocation data."""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}").json()
        return {
            "isp": response.get("isp"),
            "city": response.get("city"),
            "country": response.get("country"),
            "lat": response.get("lat"),
            "lon": response.get("lon")
        }
    except (requests.exceptions.RequestException, ValueError):
        return None