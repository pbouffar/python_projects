#!/usr/bin/env python3
"""
Yang-Gateway RESTCONF API CLI Tool

A command-line interface for interacting with the Yang-Gateway RESTCONF API.
Provides commands for managing endpoints, sessions, services, alerts, and metadata.

Copyright (c) 2025 Cisco Systems, Inc.
All rights reserved.
"""

import requests
import argparse
import json
import sys
from typing import Optional, Dict, Any
import urllib3

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box
from rich.tree import Tree

import utils
from config import get_tenant_id, get_user_roles
from config import ygw as orchestrator

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize Rich console
console = Console()


# ============================================================================
# Core API Request Functions
# ============================================================================

def send_request(method: str, url: str, body: Optional[Dict] = None, 
                params: Optional[Dict] = None):
    """Send an HTTP request with appropriate headers and log the response."""
    try:
        headers = None
        if orchestrator.is_replicated():
            headers = {
                "X-Forwarded-Tenant-Id": get_tenant_id(),
                "X-Forwarded-User-Id": "12345",
                "X-Forwarded-User-Username": "pierre",
                "X-Forwarded-User-Roles": get_user_roles(),
                "X-Forwarded-User-groups": "pierres"
            }
        resp = orchestrator.send_request(method, url, body=body, params=params, headers=headers)
        if not resp.ok:
            console.print(f"[bold red]Error:[/bold red] Request failed with status {resp.status_code}")
            utils.log_response(resp)
        return resp
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


# ============================================================================
# Service Endpoint Management
# ============================================================================

def get_all_endpoints() -> None:
    """Get and display all service endpoints."""
    try:
        console.print("[cyan]Fetching all service endpoints...[/cyan]")
        url = "/restconf/data/Accedian-service-endpoint:service-endpoints"
        
        resp = send_request("GET", url)        
        if not resp.ok:
            console.print(f"[bold red]Error:[/bold red] Failed to fetch endpoints (Status: {resp.status_code})")
            utils.log_response(resp)
            return
        
        if len(str(resp.text)) == 0:
            console.print("[yellow]No data.[/yellow]\n")
            utils.log_response(resp)
            return

        data = resp.json()
        endpoints = data.get('Accedian-service-endpoint:service-endpoints', {}).get('service-endpoint', [])
        
        if not endpoints:
            console.print("[yellow]No service endpoints found.[/yellow]\n")
            utils.log_response(resp)
            return
        
        # Create a rich table
        table = Table(
            title=f"Service Endpoints ({len(endpoints)} total)",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("Name", style="green", width=30)
        table.add_column("Type", style="blue", width=20)
        table.add_column("Status", style="yellow", width=15)
        table.add_column("Description", style="white", no_wrap=False)
        
        for idx, endpoint in enumerate(endpoints, 1):
            name = endpoint.get('name', 'N/A')
            ep_type = endpoint.get('type', 'N/A')
            status = endpoint.get('status', 'N/A')
            description = endpoint.get('description', 'N/A')
            
            # Color code status
            if status.lower() in ['active', 'up', 'enabled']:
                status_display = f"[green]{status}[/green]"
            elif status.lower() in ['inactive', 'down', 'disabled']:
                status_display = f"[red]{status}[/red]"
            else:
                status_display = status
            
            table.add_row(str(idx), name, ep_type, status_display, description)
        
        console.print(table)
        console.print()
        
        # Option to show detailed JSON
        if console.input("\n[bold]Show detailed JSON? (y/n): [/bold]").lower() == 'y':
            syntax = Syntax(
                json.dumps(data, indent=2),
                "json",
                theme="monokai",
                line_numbers=True
            )
            console.print(syntax)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


def get_specific_endpoint(identifier: str) -> None:
    """Get and display a specific service endpoint."""
    try:
        console.print(f"[cyan]Fetching endpoint:[/cyan] {identifier}")
        url = f"/restconf/data/Accedian-service-endpoint:service-endpoints/service-endpoint={identifier}"
        
        resp = send_request("GET", url)        
        if not resp.ok:
            console.print(f"[bold red]Error:[/bold red] Endpoint '{identifier}' not found (Status: {resp.status_code})")
            utils.log_response(resp)
            return
        
        if len(str(resp.text)) == 0:
            console.print("[yellow]No data.[/yellow]\n")
            utils.log_response(resp)
            return

        data = resp.json()
        
        # Display in a panel with syntax highlighting
        console.print(Panel.fit(
            f"[bold green]Service Endpoint:[/bold green] {identifier}",
            border_style="green"
        ))
        
        syntax = Syntax(
            json.dumps(data, indent=2),
            "json",
            theme="monokai",
            line_numbers=True
        )
        console.print(syntax)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


# ============================================================================
# Alert Policy Management
# ============================================================================

def get_all_alerts() -> None:
    """Get and display all alert policies."""
    try:
        console.print("[cyan]Fetching all alert policies...[/cyan]")
        url = "/restconf/data/Accedian-alert:alert-policies"
        
        resp = send_request("GET", url)        
        if not resp.ok:
            console.print(f"[bold red]Error:[/bold red] Failed to fetch alert policies (Status: {resp.status_code})")
            utils.log_response(resp)
            return
        
        if len(str(resp.text)) == 0:
            console.print("[yellow]No data.[/yellow]\n")
            utils.log_response(resp)
            return

        data = resp.json()
        policies = data.get('Accedian-alert:alert-policies', {}).get('alert-policy', [])
        
        if not policies:
            console.print("[yellow]No alert policies found.[/yellow]\n")
            utils.log_response(resp)
            return
        
        # Create a rich table
        table = Table(
            title=f"Alert Policies ({len(policies)} total)",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("Name", style="green", width=30)
        table.add_column("Severity", style="yellow", width=15)
        table.add_column("Status", style="blue", width=15)
        table.add_column("Condition", style="white", no_wrap=False)
        
        for idx, policy in enumerate(policies, 1):
            name = policy.get('name', 'N/A')
            severity = policy.get('severity', 'N/A')
            status = policy.get('status', 'N/A')
            condition = policy.get('condition', 'N/A')
            
            # Color code severity
            if severity.lower() == 'critical':
                severity_display = f"[red bold]{severity}[/red bold]"
            elif severity.lower() == 'major':
                severity_display = f"[red]{severity}[/red]"
            elif severity.lower() == 'minor':
                severity_display = f"[yellow]{severity}[/yellow]"
            elif severity.lower() == 'warning':
                severity_display = f"[yellow]{severity}[/yellow]"
            else:
                severity_display = severity
            
            # Color code status
            if status.lower() in ['active', 'enabled']:
                status_display = f"[green]{status}[/green]"
            elif status.lower() in ['inactive', 'disabled']:
                status_display = f"[dim]{status}[/dim]"
            else:
                status_display = status
            
            table.add_row(str(idx), name, severity_display, status_display, str(condition)[:50])
        
        console.print(table)
        console.print()
        
        # Option to show detailed JSON
        if console.input("\n[bold]Show detailed JSON? (y/n): [/bold]").lower() == 'y':
            syntax = Syntax(
                json.dumps(data, indent=2),
                "json",
                theme="monokai",
                line_numbers=True
            )
            console.print(syntax)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


# ============================================================================
# Session Management
# ============================================================================

def get_all_sessions() -> None:
    """Get and display all sessions."""
    try:
        console.print("[cyan]Fetching all sessions...[/cyan]")
        url = "/restconf/data/Accedian-session:sessions"
        
        resp = send_request("GET", url)
        if not resp.ok:
            console.print(f"[bold red]Error:[/bold red] Failed to fetch sessions (Status: {resp.status_code})")
            utils.log_response(resp)
            return

        if len(str(resp.text)) == 0:
            console.print("[yellow]No data.[/yellow]\n")
            utils.log_response(resp)
            return

        data = resp.json()
        sessions = data.get('Accedian-session:sessions', {}).get('session', [])        
        if not sessions:
            console.print("[yellow]No sessions found.[/yellow]\n")
            utils.log_response(resp)
            return

        # Create a rich table
        table = Table(
            title=f"Sessions ({len(sessions)} total)",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("ID", style="green", width=36)
        table.add_column("Name", style="magenta", width=30)
        table.add_column("Type", style="blue", width=15)
        table.add_column("Status", style="yellow", width=15)
        
        for idx, session in enumerate(sessions, 1):
            session_id = session.get('id', 'N/A')
            name = session.get('name', 'N/A')
            session_type = session.get('type', 'N/A')
            status = session.get('status', 'N/A')
            
            # Color code status
            if status.lower() in ['active', 'running']:
                status_display = f"[green]{status}[/green]"
            elif status.lower() in ['stopped', 'completed']:
                status_display = f"[blue]{status}[/blue]"
            elif status.lower() in ['failed', 'error']:
                status_display = f"[red]{status}[/red]"
            else:
                status_display = status
            
            table.add_row(str(idx), str(session_id), name, session_type, status_display)
        
        console.print(table)
        console.print()
        
        # Option to show detailed JSON
        if console.input("\n[bold]Show detailed JSON? (y/n): [/bold]").lower() == 'y':
            syntax = Syntax(
                json.dumps(data, indent=2),
                "json",
                theme="monokai",
                line_numbers=True
            )
            console.print(syntax)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


def get_specific_session(identifier: str) -> None:
    """Get and display a specific session."""
    try:
        console.print(f"[cyan]Fetching session:[/cyan] {identifier}")
        url = f"/restconf/data/Accedian-session:sessions/session={identifier}"
        
        resp = send_request("GET", url)        
        if not resp.ok:
            console.print(f"[bold red]Error:[/bold red] Session '{identifier}' not found (Status: {resp.status_code})")
            utils.log_response(resp)
            return
        
        if len(str(resp.text)) == 0:
            console.print("[yellow]No data.[/yellow]\n")
            utils.log_response(resp)
            return

        data = resp.json()
        
        # Display in a panel with syntax highlighting
        console.print(Panel.fit(
            f"[bold blue]Session:[/bold blue] {identifier}",
            border_style="blue"
        ))
        
        syntax = Syntax(
            json.dumps(data, indent=2),
            "json",
            theme="monokai",
            line_numbers=True
        )
        console.print(syntax)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


# ============================================================================
# Service Management
# ============================================================================

def get_all_services() -> None:
    """Get and display all services."""
    try:
        console.print("[cyan]Fetching all services...[/cyan]")
        url = "/restconf/data/Accedian-service:services"
        
        resp = send_request("GET", url)
        if not resp.ok:
            console.print(f"[bold red]Error:[/bold red] Failed to fetch services (Status: {resp.status_code})")
            utils.log_response(resp)
            return
        
        if len(str(resp.text)) == 0:
            console.print("[yellow]No data.[/yellow]\n")
            utils.log_response(resp)
            return

        data = resp.json()
        services = data.get('Accedian-service:services', {}).get('service', [])
        
        if not services:
            console.print("[yellow]No services found.[/yellow]\n")
            utils.log_response(resp)
            return
        
        # Create a rich table
        table = Table(
            title=f"Services ({len(services)} total)",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("ID", style="green", width=36)
        table.add_column("Name", style="magenta", width=30)
        table.add_column("Type", style="blue", width=20)
        table.add_column("Status", style="yellow", width=15)
        
        for idx, service in enumerate(services, 1):
            service_id = service.get('id', 'N/A')
            name = service.get('name', 'N/A')
            service_type = service.get('type', 'N/A')
            status = service.get('status', 'N/A')
            
            # Color code status
            if status.lower() in ['active', 'operational']:
                status_display = f"[green]{status}[/green]"
            elif status.lower() in ['inactive', 'down']:
                status_display = f"[red]{status}[/red]"
            else:
                status_display = status
            
            table.add_row(str(idx), str(service_id), name, service_type, status_display)
        
        console.print(table)
        console.print()
        
        # Option to show detailed JSON
        if console.input("\n[bold]Show detailed JSON? (y/n): [/bold]").lower() == 'y':
            syntax = Syntax(
                json.dumps(data, indent=2),
                "json",
                theme="monokai",
                line_numbers=True
            )
            console.print(syntax)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


# ============================================================================
# Metadata Management
# ============================================================================

def get_metadata_config() -> None:
    """Get and display metadata configuration."""
    try:
        console.print("[cyan]Fetching metadata configuration...[/cyan]")
        url = "/restconf/data/Accedian-metadata:metadata-config"
        
        resp = send_request("GET", url)
        if not resp.ok:
            console.print(f"[bold red]Error:[/bold red] Failed to fetch metadata config (Status: {resp.status_code})")
            utils.log_response(resp)
            return
        
        if len(str(resp.text)) == 0:
            console.print("[yellow]No data.[/yellow]\n")
            utils.log_response(resp)
            return

        data = resp.json()
        
        # Display in a panel with syntax highlighting
        console.print(Panel.fit(
            "[bold magenta]Metadata Configuration[/bold magenta]",
            border_style="magenta"
        ))
        
        syntax = Syntax(
            json.dumps(data, indent=2),
            "json",
            theme="monokai",
            line_numbers=True
        )
        console.print(syntax)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


# ============================================================================
# Custom Formatter for argparse
# ============================================================================

class CustomHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Custom formatter for better help text layout."""
    
    def __init__(self, prog, indent_increment=2, max_help_position=35, width=None):
        super().__init__(prog, indent_increment, max_help_position, width)


# ============================================================================
# Argument Parser Setup
# ============================================================================

def build_parser() -> argparse.ArgumentParser:
    """Build and configure the argument parser."""
    
    description = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                Yang-Gateway RESTCONF API CLI Tool                        ║
╚══════════════════════════════════════════════════════════════════════════╝

API Endpoint: {orchestrator.get_url_info()}
"""
    
    epilog = """
"""
    
    parser = argparse.ArgumentParser(
        prog='ygw.py',
        description=description,
        epilog=epilog,
        formatter_class=CustomHelpFormatter,
        add_help=True
    )

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="COMMAND",
        title="Available Commands",
        description="Use one of the following commands to interact with the Yang-Gateway RESTCONF API"
    )

    add_commands(subparsers)
    return parser


def add_commands(subparsers):
    """Add all subcommands to the parser."""
    
    # ========================================================================
    # Generic HTTP Methods
    # ========================================================================
    
    sp = subparsers.add_parser(
        "get",
        help="Perform a GET request",
        description="Executes a GET request to retrieve data from the RESTCONF API.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("uri", metavar="URI", help="URI path to request (e.g., /restconf/data/...)")
    sp.set_defaults(func=lambda a: send_request("GET", a.uri))

    sp = subparsers.add_parser(
        "post",
        help="Perform a POST request",
        description="Executes a POST request to create or invoke operations on the RESTCONF API.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("uri", metavar="URI", help="URI path to request")
    sp.set_defaults(func=lambda a: send_request("POST", a.uri))

    sp = subparsers.add_parser(
        "put",
        help="Perform a PUT request",
        description="Executes a PUT request to replace existing data on the RESTCONF API.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("uri", metavar="URI", help="URI path to request")
    sp.set_defaults(func=lambda a: send_request("PUT", a.uri))

    sp = subparsers.add_parser(
        "patch",
        help="Perform a PATCH request",
        description="Executes a PATCH request to merge data on the RESTCONF API.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("uri", metavar="URI", help="URI path to request")
    sp.set_defaults(func=lambda a: send_request("PATCH", a.uri))

    sp = subparsers.add_parser(
        "delete",
        help="Perform a DELETE request",
        description="Executes a DELETE request to remove data from the RESTCONF API.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("uri", metavar="URI", help="URI path to request")
    sp.set_defaults(func=lambda a: send_request("DELETE", a.uri))

    # ========================================================================
    # Service Endpoint Commands
    # ========================================================================
    
    sp = subparsers.add_parser(
        "get_endpoints",
        help="Get all service endpoints",
        description="Fetches and displays all service endpoints in a formatted table.",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: get_all_endpoints())

    sp = subparsers.add_parser(
        "get_endpoint",
        help="Get a specific service endpoint",
        description="Fetches and displays detailed information about a specific service endpoint.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("identifier", metavar="ENDPOINT_ID", help="The identifier of the service endpoint")
    sp.set_defaults(func=lambda a: get_specific_endpoint(a.identifier))

    # ========================================================================
    # Alert Policy Commands
    # ========================================================================
    
    sp = subparsers.add_parser(
        "get_alerts",
        help="Get all alert policies",
        description="Fetches and displays all alert policies with severity and status information.",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: get_all_alerts())

    # ========================================================================
    # Session Commands
    # ========================================================================
    
    sp = subparsers.add_parser(
        "get_sessions",
        help="Get all sessions",
        description="Fetches and displays all sessions in a formatted table.",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: get_all_sessions())

    sp = subparsers.add_parser(
        "get_session",
        help="Get a specific session",
        description="Fetches and displays detailed information about a specific session.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("identifier", metavar="SESSION_ID", help="The identifier of the session")
    sp.set_defaults(func=lambda a: get_specific_session(a.identifier))

    # ========================================================================
    # Service Commands
    # ========================================================================
    
    sp = subparsers.add_parser(
        "get_services",
        help="Get all services",
        description="Fetches and displays all services in a formatted table.",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: get_all_services())

    # ========================================================================
    # Metadata Commands
    # ========================================================================
    
    sp = subparsers.add_parser(
        "get_metadata",
        help="Get metadata configuration",
        description="Fetches and displays the complete metadata configuration.",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: get_metadata_config())


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for the CLI application."""
    parser = build_parser()
    
    # Show help if no arguments provided
    if len(sys.argv) == 1:
        # Show replicated mode info if applicable
        if orchestrator.is_replicated():
            console.print(Panel.fit(
                "[bold yellow]Replicated Mode Enabled[/bold yellow]\n"
                f"Tenant ID: {get_tenant_id()}\n"
                f"User Roles: {get_user_roles()}",
                border_style="yellow"
            ))
        
        parser.print_help()
        return

    args = parser.parse_args()
    
    # Execute the command if it has a function
    if hasattr(args, "func"):
        try:
            # Display connection info
            info_text = f"[bold cyan]Connecting to:[/bold cyan] {orchestrator.get_url_info()}"
            if orchestrator.is_replicated():
                info_text += f"\n[bold yellow]Replicated Mode:[/bold yellow] Tenant {get_tenant_id()}"
            
            console.print(Panel.fit(info_text, border_style="cyan"))
            
            orchestrator.login()
            args.func(args)
            orchestrator.logout()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user.[/yellow]")
            sys.exit(0)
        except Exception as e:
            console.print(f"\n[bold red]Unexpected error:[/bold red] {str(e)}")
            if '--debug' in sys.argv:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()