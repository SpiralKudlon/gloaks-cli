import socket
import requests

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

def scan_ports(target_ip, ports=[21, 22, 80, 443, 3306, 8080]):
    """Returns a list of open ports."""
    open_ports = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((target_ip, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    return open_ports

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
    except Exception:
        return None