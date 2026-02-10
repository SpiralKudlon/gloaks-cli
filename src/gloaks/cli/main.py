import asyncio
import click
import structlog
from gloaks.core.config import load_config
from gloaks.core.logging_setup import configure_logging
from gloaks.core.engine import GloaksEngine
from gloaks.cli import output

# Initialize logging immediately for CLI usage
# User requested visible startup messages, so default to INFO
configure_logging(level="INFO", log_format="console")
logger = structlog.get_logger()

@click.group()
def cli():
    """Gloaks-CLI: Advanced Network Reconnaissance Tool"""
    pass

@cli.command()
@click.argument("target")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
@click.option("--output-file", "-o", help="Save results to JSON file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--scope", "-s", type=click.Path(exists=True), help="Path to scope definition file")
def scan(target: str, config: str, output_file: str, verbose: bool, scope: str):
    """Scan a target domain or IP address."""
    output.print_banner()
    
    # Reconfigure logging based on verbosity
    log_level = "DEBUG" if verbose else "INFO"
    configure_logging(level=log_level, log_format="console")
    
    # Load configuration
    app_config = load_config(config)
    
    # Input Validation
    from gloaks.utils.validators import InputValidator
    is_valid, error_msg = InputValidator.validate_target(target)
    if not is_valid:
        output.console.print(f"[bold red]Security Error:[/bold red] {error_msg}")
        return

    # Validate Scope
    from gloaks.core.scope import ScopeValidator
    validator = ScopeValidator(scope or app_config.scope_file)
    
    # Run async scope check
    loop = asyncio.new_event_loop()
    try:
        is_allowed = loop.run_until_complete(validator.is_target_allowed(target))
    finally:
        loop.close()

    if scope and not is_allowed:
        output.console.print(f"[bold red]Error:[/bold red] Target '{target}' is not in the authorized scope.")
        output.console.print(f"Scope file: {scope}")
        return

    
    # Initialize Engine
    engine = GloaksEngine(app_config)
    
    # Run Async Loop
    try:
        results = asyncio.run(engine.run(target))
        
        # Render Results
        modules = results.get("modules", {})
        
        output.console.rule("[bold blue]Scan Results")
        
        if "geolocation" in modules:
            output.print_geolocation(modules["geolocation"])
            
        if "port_scan" in modules:
            output.print_ports(modules["port_scan"])
            
        if "dns_enumeration" in modules:
            output.print_dns_records(modules["dns_enumeration"])

        if "http_analysis" in modules:
            output.print_http_analysis(modules["http_analysis"])
            
        if output_file:
            output.export_json(results, output_file)
            
    except Exception as e:
        logger.exception("Scan failed")
        click.echo(f"Error: {e}", err=True)

if __name__ == "__main__":
    cli()
