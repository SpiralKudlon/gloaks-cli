from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.json import JSON
from typing import Dict, Any, List
import json
import yaml

console = Console()

def print_banner():
    """Print the Gloaks ASCII banner."""
    banner = """
     _____ _             _         ____ _     ___
    / ____| |           | |       / ___| |   |_ _|
   | |  __| | ___   __ _| | _____| |   | |    | |
   | | |_ | |/ _ \ / _` | |/ / __| |   | |    | |
   | |__| | | (_) | (_| |   <\__ \ |___| |___ | |
    \_____|_|\___/ \__,_|_|\_\___/\____|_____|___|
    
    v3.0.0 | Network Reconnaissance Toolkit
    """
    console.print(Panel(banner, style="bold blue", expand=False))

def print_geolocation(data: Dict[str, Any]):
    """Print geolocation data in a table."""
    if "error" in data:
        console.print(f"[bold red]Geolocation Error:[/bold red] {data['error']}")
        return

    table = Table(title="Geolocation Data", show_header=False)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Country", data.get("country", "N/A"))
    table.add_row("City", data.get("city", "N/A"))
    table.add_row("ISP", data.get("isp", "N/A"))
    table.add_row("Coordinates", f"{data.get('lat')}, {data.get('lon')}")
    table.add_row("IP", data.get("ip", "N/A"))
    
    console.print(table)

def print_ports(data: Dict[str, Any]):
    """Print open ports in a table."""
    open_ports = data.get("open_ports", [])
    if not open_ports:
        console.print("[yellow]No open ports found.[/yellow]")
        return

    table = Table(title="Open Ports")
    table.add_column("Port", style="cyan")
    table.add_column("Protocol", style="magenta")
    table.add_column("State", style="green")

    for port in open_ports:
        table.add_row(str(port["port"]), port["protocol"], port["state"])
    
    console.print(table)

def print_http_analysis(data: Dict[str, Any]):
    """Print HTTP analysis results."""
    if "error" in data:
        # It's common for HTTP to fail (e.g. port closed), so print distinct error
        # console.print(f"[red]HTTP Analysis Error:[/red] {data['error']}")
        return

    # Info Table
    info_table = Table(title="HTTP Analysis", show_header=False)
    info_table.add_row("URL", data.get("url"))
    info_table.add_row("Status", str(data.get("status_code")))
    console.print(info_table)

    # Technologies
    if data.get("technologies"):
        console.print("[bold]Technologies Detected:[/bold]")
        for tech in data["technologies"]:
            console.print(f"  • {tech}")

    # Security Headers
    sec_headers = data.get("security_headers", {})
    if sec_headers:
        table = Table(title="Security Headers")
        table.add_column("Header", style="cyan")
        table.add_column("Present", style="bold")
        
        for header, present in sec_headers.items():
            color = "green" if present else "red"
            symbol = "✓" if present else "✗"
            table.add_row(header, f"[{color}]{symbol}[/{color}]")
        console.print(table)

def print_dns_records(data: Dict[str, Any]):
    """Print DNS records."""
    if not data:
        return
        
    table = Table(title="DNS Records")
    table.add_column("Type", style="cyan")
    table.add_column("Values", style="white")
    
    for rtype, values in data.items():
        if values:
            # Handle MX records dict
            if rtype == "MX":
                formatted_values = ", ".join([f"{v['host']} ({v['priority']})" for v in values])
            else:
                formatted_values = ", ".join(values)
            table.add_row(rtype, formatted_values)
            
    console.print(table)

def export_json(data: Dict[str, Any], filename: str):
    """Export results to JSON file."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    console.print(f"[bold green]Results exported to {filename}[/bold green]")
