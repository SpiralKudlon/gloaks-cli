import sys
import time
import pyfiglet
from colorama import init, Fore, Style
import scanner

# Initialize Colorama for auto-resetting colors
init(autoreset=True)

def print_banner():
    # This generates the ASCII art 'Gloaks'
    ascii_banner = pyfiglet.figlet_format("Gloaks")
    print(Fore.BLUE + ascii_banner)
    print(f"{Fore.WHITE}      Automated Recon Framework {Fore.CYAN}v2.1{Fore.RESET}\n")
    print(f"{Fore.BLUE}{'-'*60}")
    print(f"{Fore.RED}[!] DISCLAIMER: For educational/authorized testing only.")
    print(f"{Fore.BLUE}{'-'*60}\n")

def main():
    print_banner()
    
    target = input(f"{Fore.GREEN}[?] Enter Target Domain or IP: {Fore.WHITE}")
    
    if not target:
        print(f"{Fore.RED}[!] No target provided. Exiting.")
        sys.exit()

    print(f"\n{Fore.YELLOW}[*] Resolving Target...")
    target_ip = scanner.get_ip(target)

    if not target_ip:
        print(f"{Fore.RED}[!] Could not resolve domain.")
        sys.exit()

    print(f"{Fore.GREEN}[+] Target Locked: {target_ip}\n")
    time.sleep(1)

    # --- Start Modules ---
    
    # Headers
    print(f"{Fore.CYAN}[*] Scanning HTTP Headers...{Fore.RESET}")
    headers = scanner.scan_headers(target)
    if headers:
        for key, value in headers.items():
            print(f"  {Fore.YELLOW}├─ {key}: {Fore.WHITE}{value}")
    else:
        print(f"{Fore.RED}[!] Could not connect to HTTP service.{Fore.RESET}")
        
    time.sleep(0.5)
    
    # Ports
    print(f"\n{Fore.CYAN}[*] Quick Port Scan (Top ports)...{Fore.RESET}")
    open_ports = scanner.scan_ports(target_ip)
    if open_ports:
        for port in open_ports:
            print(f"  {Fore.GREEN}[+] Port {port} OPEN{Fore.RESET}")
    else:
        print(f"  {Fore.YELLOW}[-] No common ports found open.{Fore.RESET}")
        
    time.sleep(0.5)
    
    # GeoIP
    print(f"\n{Fore.CYAN}[*] Geolocation Data...{Fore.RESET}")
    geo_data = scanner.geo_locate(target_ip)
    if geo_data:
        print(f"  {Fore.YELLOW}├─ ISP: {Fore.WHITE}{geo_data.get('isp')}")
        print(f"  {Fore.YELLOW}├─ Location: {Fore.WHITE}{geo_data.get('city')}, {geo_data.get('country')}")
        print(f"  {Fore.YELLOW}└─ Coordinates: {Fore.WHITE}{geo_data.get('lat')}, {geo_data.get('lon')}")
    else:
        print(f"{Fore.RED}[!] Geo-lookup failed.{Fore.RESET}")
    
    print(f"\n{Fore.BLUE}{'-'*60}")
    print(f"{Fore.GREEN}[✓] Reconnaissance Complete.")
    print(f"{Fore.BLUE}{'-'*60}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Operation Cancelled by User.")
        sys.exit()