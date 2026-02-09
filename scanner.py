import socket
import requests
from colorama import Fore

def get_ip(target):
    try:
        ip = socket.gethostbyname(target)
        return ip
    except socket.gaierror:
        return None

def scan_headers(target):
    print(f"{Fore.CYAN}[*] Scanning HTTP Headers...{Fore.RESET}")
    try:
        response = requests.get(f"http://{target}", timeout=5)
        for key, value in response.headers.items():
            print(f"  {Fore.YELLOW}├─ {key}: {Fore.WHITE}{value}")
    except requests.exceptions.RequestException:
        print(f"{Fore.RED}[!] Could not connect to HTTP service.{Fore.RESET}")

def scan_ports(target_ip, ports=[21, 22, 80, 443, 3306, 8080]):
    print(f"\n{Fore.CYAN}[*] Quick Port Scan (Top ports)...{Fore.RESET}")
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((target_ip, port))
        if result == 0:
            print(f"  {Fore.GREEN}[+] Port {port} OPEN{Fore.RESET}")
        else:
            # Uncomment below if you want to see closed ports
            # print(f"  {Fore.RED}[-] Port {port} CLOSED{Fore.RESET}")
            pass
        sock.close()

def geo_locate(ip):
    print(f"\n{Fore.CYAN}[*] Geolocation Data...{Fore.RESET}")
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}").json()
        print(f"  {Fore.YELLOW}├─ ISP: {Fore.WHITE}{response.get('isp')}")
        print(f"  {Fore.YELLOW}├─ Location: {Fore.WHITE}{response.get('city')}, {response.get('country')}")
        print(f"  {Fore.YELLOW}└─ Coordinates: {Fore.WHITE}{response.get('lat')}, {response.get('lon')}")
    except:
        print(f"{Fore.RED}[!] Geo-lookup failed.{Fore.RESET}")