#!/usr/bin/env python3
"""
Sensor Orchestrator API CLI Tool

A command-line interface for interacting with the Sensor Orchestrator API.
Provides commands for managing Echo, TWAMP, Y.1564, and RFC2544 test sessions.

Copyright (c) 2025 Cisco Systems, Inc.
All rights reserved.
"""

import argparse
import json
import sys
from typing import Optional, Dict, Any, List
import urllib3

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box
from rich.tree import Tree

import utils
from config import so as orchestrator

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize Rich console
console = Console()


# ============================================================================
# Core API Request Functions
# ============================================================================

def send_request(method: str, url: str, body: Optional[Dict] = None):
    """Send an HTTP request and return the response."""
    try:
        resp = orchestrator.send_request(method, url, body)
        return resp
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


# ============================================================================
# Echo Session Management
# ============================================================================

def get_echo_session(identifier: str):
    """Get a specific Echo session by identifier."""
    url = f"/nbapi/session/echo/{identifier}"
    return send_request("GET", url)


def print_echo_session(identifier: str) -> None:
    """Display a specific Echo session."""
    try:
        console.print(f"[cyan]Fetching Echo session:[/cyan] {identifier}")
        response = get_echo_session(identifier)
        
        if not response.ok:
            console.print(f"[bold red]Error:[/bold red] Echo session '{identifier}' not found (Status: {response.status_code})")
            utils.log_response(response)
            return
        
        session_data = response.json()
        
        # Display in a panel with syntax highlighting
        console.print(Panel.fit(
            f"[bold green]Echo Session:[/bold green] {identifier}",
            border_style="green"
        ))
        
        syntax = Syntax(
            json.dumps(session_data, indent=2),
            "json",
            theme="monokai",
            line_numbers=True
        )
        console.print(syntax)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


# ============================================================================
# TWAMP Session Management
# ============================================================================

def get_twamp_session(identifier: str):
    """Get a specific TWAMP session by identifier."""
    url = f"/nbapi/session/twamp/{identifier}"
    return send_request("GET", url)


def print_twamp_session(identifier: str) -> None:
    """Display a specific TWAMP session."""
    try:
        console.print(f"[cyan]Fetching TWAMP session:[/cyan] {identifier}")
        response = get_twamp_session(identifier)
        
        if not response.ok:
            console.print(f"[bold red]Error:[/bold red] TWAMP session '{identifier}' not found (Status: {response.status_code})")
            utils.log_response(response)
            return
        
        session_data = response.json()
        
        # Display in a panel with syntax highlighting
        console.print(Panel.fit(
            f"[bold blue]TWAMP Session:[/bold blue] {identifier}",
            border_style="blue"
        ))
        
        syntax = Syntax(
            json.dumps(session_data, indent=2),
            "json",
            theme="monokai",
            line_numbers=True
        )
        console.print(syntax)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


# ============================================================================
# Y.1564 Session Management
# ============================================================================

def get_all_y1564_sessions():
    """Get all Y.1564 test sessions."""
    url = "/nbapiemswsweb/rest/v1/Search/Y1564TestConfig"
    return send_request("GET", url)


def print_all_y1564_sessions() -> None:
    """Display all Y.1564 test sessions."""
    try:
        console.print("[cyan]Fetching Y.1564 sessions...[/cyan]")
        response = get_all_y1564_sessions()
        
        if not response.ok:
            console.print(f"[bold red]Error:[/bold red] Failed to fetch Y.1564 sessions (Status: {response.status_code})")
            utils.log_response(response)
            return
        
        content = response.json().get('content', [])
        
        if not content:
            console.print("[yellow]No Y.1564 sessions found.[/yellow]\n")
            return
        
        # Create a rich table
        table = Table(
            title=f"Y.1564 Test Sessions ({len(content)} total)",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("ID", style="green", width=36)
        table.add_column("Name", style="magenta", width=30)
        table.add_column("Status", style="yellow", width=15)
        table.add_column("Type", style="blue", width=20)
        
        for idx, session in enumerate(content, 1):
            session_id = str(session.get('id', 'N/A'))
            name = session.get('name', 'N/A')
            status = session.get('status', 'N/A')
            test_type = session.get('testType', 'N/A')
            
            # Color code status
            if status.lower() in ['active', 'running']:
                status_display = f"[green]{status}[/green]"
            elif status.lower() in ['stopped', 'completed']:
                status_display = f"[blue]{status}[/blue]"
            elif status.lower() in ['failed', 'error']:
                status_display = f"[red]{status}[/red]"
            else:
                status_display = status
            
            table.add_row(str(idx), session_id, name, status_display, test_type)
        
        console.print(table)
        console.print()
        
        # Option to show detailed JSON
        if console.input("\n[bold]Show detailed JSON? (y/n): [/bold]").lower() == 'y':
            syntax = Syntax(
                json.dumps(content, indent=2),
                "json",
                theme="monokai",
                line_numbers=True
            )
            console.print(syntax)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


# ============================================================================
# RFC2544 Session Management
# ============================================================================

def get_all_rfc2544_sessions():
    """Get all RFC2544 test sessions."""
    url = "/nbapiemswsweb/rest/v1/Search/RFC2544TestConfig"
    return send_request("GET", url)


def print_all_rfc2544_sessions() -> None:
    """Display all RFC2544 test sessions."""
    try:
        console.print("[cyan]Fetching RFC2544 sessions...[/cyan]")
        response = get_all_rfc2544_sessions()
        
        if not response.ok:
            console.print(f"[bold red]Error:[/bold red] Failed to fetch RFC2544 sessions (Status: {response.status_code})")
            utils.log_response(response)
            return
        
        content = response.json().get('content', [])
        
        if not content:
            console.print("[yellow]No RFC2544 sessions found.[/yellow]\n")
            return
        
        # Create a rich table
        table = Table(
            title=f"RFC2544 Test Sessions ({len(content)} total)",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("ID", style="green", width=36)
        table.add_column("Name", style="magenta", width=30)
        table.add_column("Status", style="yellow", width=15)
        table.add_column("Type", style="blue", width=20)
        
        for idx, session in enumerate(content, 1):
            session_id = str(session.get('id', 'N/A'))
            name = session.get('name', 'N/A')
            status = session.get('status', 'N/A')
            test_type = session.get('testType', 'N/A')
            
            # Color code status
            if status.lower() in ['active', 'running']:
                status_display = f"[green]{status}[/green]"
            elif status.lower() in ['stopped', 'completed']:
                status_display = f"[blue]{status}[/blue]"
            elif status.lower() in ['failed', 'error']:
                status_display = f"[red]{status}[/red]"
            else:
                status_display = status
            
            table.add_row(str(idx), session_id, name, status_display, test_type)
        
        console.print(table)
        console.print()
        
        # Option to show detailed JSON
        if console.input("\n[bold]Show detailed JSON? (y/n): [/bold]").lower() == 'y':
            syntax = Syntax(
                json.dumps(content, indent=2),
                "json",
                theme="monokai",
                line_numbers=True
            )
            console.print(syntax)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


# ============================================================================
# SAT (Service Acceptance Testing) Sessions
# ============================================================================

def print_all_sat_sessions() -> None:
    """Display all SAT sessions (Y.1564 and RFC2544)."""
    try:
        console.print(Panel.fit(
            "[bold cyan]Service Acceptance Testing (SAT) Sessions[/bold cyan]\n"
            "Fetching Y.1564 and RFC2544 test configurations...",
            border_style="cyan"
        ))
        console.print()
        
        # Fetch Y.1564 sessions
        console.rule("[bold green]Y.1564 Test Sessions[/bold green]")
        y1564_response = get_all_y1564_sessions()
        y1564_count = 0
        
        if y1564_response.ok:
            y1564_content = y1564_response.json().get('content', [])
            y1564_count = len(y1564_content)
            
            if y1564_content:
                table = Table(
                    box=box.ROUNDED,
                    show_header=True,
                    header_style="bold green"
                )
                table.add_column("#", style="dim", width=4)
                table.add_column("ID", style="green", width=36)
                table.add_column("Name", style="magenta", width=30)
                table.add_column("Status", style="yellow", width=15)
                
                for idx, session in enumerate(y1564_content, 1):
                    session_id = str(session.get('id', 'N/A'))
                    name = session.get('name', 'N/A')
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
                    
                    table.add_row(str(idx), session_id, name, status_display)
                
                console.print(table)
            else:
                console.print("[yellow]No Y.1564 sessions found.[/yellow]")
        else:
            console.print("[red]Failed to fetch Y.1564 sessions.[/red]")
        
        console.print()
        
        # Fetch RFC2544 sessions
        console.rule("[bold blue]RFC2544 Test Sessions[/bold blue]")
        rfc2544_response = get_all_rfc2544_sessions()
        rfc2544_count = 0
        
        if rfc2544_response.ok:
            rfc2544_content = rfc2544_response.json().get('content', [])
            rfc2544_count = len(rfc2544_content)
            
            if rfc2544_content:
                table = Table(
                    box=box.ROUNDED,
                    show_header=True,
                    header_style="bold blue"
                )
                table.add_column("#", style="dim", width=4)
                table.add_column("ID", style="green", width=36)
                table.add_column("Name", style="magenta", width=30)
                table.add_column("Status", style="yellow", width=15)
                
                for idx, session in enumerate(rfc2544_content, 1):
                    session_id = str(session.get('id', 'N/A'))
                    name = session.get('name', 'N/A')
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
                    
                    table.add_row(str(idx), session_id, name, status_display)
                
                console.print(table)
            else:
                console.print("[yellow]No RFC2544 sessions found.[/yellow]")
        else:
            console.print("[red]Failed to fetch RFC2544 sessions.[/red]")
        
        console.print()
        
        # Summary
        console.print(Panel.fit(
            f"[bold]SAT Sessions Summary[/bold]\n"
            f"Y.1564 Sessions: [green]{y1564_count}[/green]\n"
            f"RFC2544 Sessions: [blue]{rfc2544_count}[/blue]\n"
            f"Total: [cyan]{y1564_count + rfc2544_count}[/cyan]",
            border_style="cyan"
        ))
        
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
║                 Sensor Orchestrator API CLI Tool                         ║
╚══════════════════════════════════════════════════════════════════════════╝

API Endpoint: {orchestrator.get_url_info()}
"""
    
    epilog = """
"""
    
    parser = argparse.ArgumentParser(
        prog='so.py',
        description=description,
        epilog=epilog,
        formatter_class=CustomHelpFormatter,
        add_help=True
    )

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="COMMAND",
        title="Available Commands",
        description="Use one of the following commands to interact with the Sensor Orchestrator API"
    )

    add_commands(subparsers)
    return parser


def add_commands(subparsers):
    """Add all subcommands to the parser."""
    
    # ========================================================================
    # Echo Session Commands
    # ========================================================================
    
    sp = subparsers.add_parser(
        "get_session_echo",
        help="Get a specific Echo session",
        description="""Fetches and displays detailed information about a specific Echo session.

Echo sessions are used for network connectivity testing and basic latency measurements.""",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument(
        "identifier",
        metavar="SESSION_ID",
        help="The unique identifier of the Echo session"
    )
    sp.set_defaults(func=lambda a: print_echo_session(a.identifier))

    # ========================================================================
    # TWAMP Session Commands
    # ========================================================================
    
    sp = subparsers.add_parser(
        "get_session_twamp",
        help="Get a specific TWAMP session",
        description="""Fetches and displays detailed information about a specific TWAMP session.

TWAMP (Two-Way Active Measurement Protocol) is used for measuring network 
performance metrics like delay, jitter, and packet loss.""",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument(
        "identifier",
        metavar="SESSION_ID",
        help="The unique identifier of the TWAMP session"
    )
    sp.set_defaults(func=lambda a: print_twamp_session(a.identifier))

    # ========================================================================
    # Y.1564 Session Commands
    # ========================================================================
    
    sp = subparsers.add_parser(
        "get_sessions_y1564",
        help="Get all Y.1564 test sessions",
        description="""Fetches and displays all Y.1564 Ethernet service activation test sessions.

Y.1564 is an ITU-T standard for Ethernet service activation testing, providing
a comprehensive methodology for turning up new carrier Ethernet services.""",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: print_all_y1564_sessions())

    # ========================================================================
    # RFC2544 Session Commands
    # ========================================================================
    
    sp = subparsers.add_parser(
        "get_sessions_rfc2544",
        help="Get all RFC2544 test sessions",
        description="""Fetches and displays all RFC2544 benchmarking test sessions.

RFC2544 defines a methodology for benchmarking network interconnect devices,
including throughput, latency, frame loss, and back-to-back tests.""",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: print_all_rfc2544_sessions())

    # ========================================================================
    # SAT (Service Acceptance Testing) Commands
    # ========================================================================
    
    sp = subparsers.add_parser(
        "get_sessions_sat",
        help="Get all SAT sessions (Y.1564 + RFC2544)",
        description="""Fetches and displays all Service Acceptance Testing (SAT) sessions.

This command retrieves both Y.1564 and RFC2544 test configurations, providing
a comprehensive view of all service acceptance testing activities.""",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: print_all_sat_sessions())


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for the CLI application."""
    parser = build_parser()
    
    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()
    
    # Execute the command if it has a function
    if hasattr(args, "func"):
        try:
            # Display connection info
            console.print(Panel.fit(
                f"[bold cyan]Connecting to:[/bold cyan] {orchestrator.get_url_info()}",
                border_style="cyan"
            ))
            
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