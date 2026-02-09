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
    scanner.scan_headers(target)
    time.sleep(0.5)
    scanner.scan_ports(target_ip)
    time.sleep(0.5)
    scanner.geo_locate(target_ip)
    
    print(f"\n{Fore.BLUE}{'-'*60}")
    print(f"{Fore.GREEN}[✓] Reconnaissance Complete.")
    print(f"{Fore.BLUE}{'-'*60}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Operation Cancelled by User.")
        sys.exit()