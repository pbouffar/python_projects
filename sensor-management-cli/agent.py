#!/usr/bin/env python3
"""
  Copyright (c) 2025 Cisco Systems, Inc.
  All rights reserved.

  This code is provided under the terms of the Cisco Software License Agreement.
  Unauthorized copying, modification, or distribution is strictly prohibited.

  Cisco Systems,Inc.
  170 West Tasman Drive,San Jose,CA 95134,USA
"""

import argparse
import json
import sys
from typing import Optional, Dict, Any
import urllib3

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

import utils
from config import agent as orchestrator

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize Rich console
console = Console()

# API Configuration
API_URL = "/api/orchestrate/v3/agents"


# ============================================================================
# API Request Functions
# ============================================================================

def send_request(method: str, url: str, body: Optional[Dict] = None):
    """Send an HTTP request and log the response."""
    try:
        resp = orchestrator.send_request(method, url, body)
        utils.log_response(resp)
        return resp
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


# ============================================================================
# Session Management
# ============================================================================

def create_session(data: Dict[str, Any]):
    """Create a new session."""
    url = f"{API_URL}/session"
    return orchestrator.post(url, body=data)


def get_session(session_id: str):
    """Get a specific session by ID."""
    url = f"{API_URL}/session/{session_id}"
    return orchestrator.get(url)


def get_sessions():
    """Get all sessions."""
    url = f"{API_URL}/sessions"
    return orchestrator.get(url)


def update_session(data: Dict[str, Any]):
    """Update an existing session."""
    url = f"{API_URL}/session"
    return orchestrator.put(url, body=data)


def delete_session(session_id: str):
    """Delete a session by ID."""
    url = f"{API_URL}/session/{session_id}"
    return orchestrator.delete(url)


def get_session_status(session_id: str):
    """Get status for a specific session."""
    url = f"{API_URL}/sessionstatus/{session_id}"
    return orchestrator.get(url)


def get_sessions_status():
    """Get status for all sessions."""
    url = f"{API_URL}/sessionstatuses"
    return orchestrator.get(url)


# ============================================================================
# Agent Management
# ============================================================================

def get_agents():
    """Get all agents."""
    url = f"{API_URL}"
    header = {"Content-type": "application/vnd.api+json"}
    return orchestrator.get(url, headers=header)


def get_agent(agent_id: str):
    """Get a specific agent by ID."""
    url = f"{API_URL}/{agent_id}"
    header = {"Content-type": "application/vnd.api+json"}
    return orchestrator.get(url, headers=header)


def get_agent_config(agent_id: str):
    """Get configuration for a specific agent."""
    url = f"{API_URL}/configuration/{agent_id}"
    header = {"Content-type": "application/vnd.api+json"}
    return orchestrator.get(url, headers=header)


def update_agent_config(agent_id: str, data: Dict[str, Any]):
    """Update agent configuration."""
    url = f"{API_URL}/configuration/{agent_id}"
    return orchestrator.put(url, body=data)


# ============================================================================
# Display Functions with Rich Formatting
# ============================================================================

def print_sessions_status(raw: bool = False) -> None:
    """Display status for all sessions in a formatted table."""
    try:
        response = get_sessions_status()
        
        if not response.ok:
            console.print(f"[bold red]Error:[/bold red] Failed to fetch sessions status (Status: {response.status_code})")
            utils.log_response(response)
            return

        if raw:
            utils.log_response(response)
            return

        sessions = response.json().get('data', [])
        
        if not sessions:
            console.print("[yellow]No sessions found.[/yellow]\n")
            return

        # Create a rich table
        table = Table(
            title="Sessions Status", 
            box=box.ROUNDED, 
            show_header=True, 
            header_style="bold cyan"
        )
        table.add_column("Session ID", style="green", width=40)
        table.add_column("Status", style="yellow", width=20)
        table.add_column("Status Message", style="white")

        for session in sessions:
            session_id = session.get('sessionId', 'N/A')
            status = session.get('status', 'N/A')
            status_message = session.get('statusMessage', 'N/A')
            
            # Color code status
            if status.lower() == 'active':
                status_style = "[green]" + status + "[/green]"
            elif status.lower() == 'failed':
                status_style = "[red]" + status + "[/red]"
            else:
                status_style = status
                
            table.add_row(session_id, status_style, status_message)

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


def print_session_status(session_id: str) -> None:
    """Display status for a specific session."""
    try:
        response = get_session_status(session_id)
        
        if not response.ok:
            console.print(f"[bold red]Error:[/bold red] Session '{session_id}' not found or request failed")
            return
            
        utils.log_response(response)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


def print_sessions() -> None:
    """Display all sessions."""
    try:
        response = get_sessions()
        
        if not response.ok:
            console.print(f"[bold red]Error:[/bold red] Failed to fetch sessions")
            utils.log_response(response)
            return
            
        utils.log_response(response)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


def print_agents() -> None:
    """Display all agents in a formatted table."""
    try:
        response = get_agents()
        
        if not response.ok:
            console.print(f"[bold red]Error:[/bold red] Failed to fetch agents")
            utils.log_response(response)
            return

        agents = response.json().get('data', [])
        
        if not agents:
            console.print("[yellow]No agents found.[/yellow]\n")
            return

        # Helper function to sort metadata
        def _meta_sort_value(v):
            if isinstance(v, dict):
                return json.dumps(v, sort_keys=True)
            return "" if v is None else str(v)

        # Extract agent information
        agents_info = [
            (
                agent.get('id'),
                agent.get("attributes", {}).get("agentName"),
                agent.get("attributes", {}).get("agentType"),
                agent.get("attributes", {}).get("status"),
                agent.get("attributes", {}).get("state"),
                agent.get("attributes", {}).get("metadata")
            )
            for agent in agents
        ]
        
        # Sort by type and metadata
        agents_info.sort(key=lambda a: ((a[2] or ""), _meta_sort_value(a[5])))

        # Create a rich table
        table = Table(
            title="Registered Agents", 
            box=box.ROUNDED, 
            show_header=True, 
            header_style="bold cyan"
        )
        table.add_column("ID", style="green", width=36)
        table.add_column("Name", style="magenta", width=16)
        table.add_column("Type", style="blue", width=12)
        table.add_column("Status", style="yellow", width=12)
        table.add_column("State", style="cyan", width=12)
        table.add_column("Metadata", style="white", no_wrap=False)

        for agent in agents_info:
            agent_id = str(agent[0]) if agent[0] else 'N/A'
            name = str(agent[1]) if agent[1] else 'N/A'
            agent_type = str(agent[2]) if agent[2] else 'N/A'
            status = str(agent[3]) if agent[3] else 'N/A'
            state = str(agent[4]) if agent[4] else 'N/A'
            metadata = str(agent[5]) if agent[5] else 'N/A'
            
            # Color code status
            if status.lower() == 'online':
                status_display = f"[green]{status}[/green]"
            elif status.lower() == 'offline':
                status_display = f"[red]{status}[/red]"
            else:
                status_display = status
            
            table.add_row(agent_id, name, agent_type, status_display, state, metadata)

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


def print_agent(agent_id: str) -> None:
    """Display a specific agent."""
    try:
        response = get_agent(agent_id)
        
        if not response.ok:
            console.print(f"[bold red]Error:[/bold red] Agent '{agent_id}' not found")
            return
            
        utils.log_response(response)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


def print_agent_config(agent_id: str) -> None:
    """Display configuration for a specific agent."""
    try:
        response = get_agent_config(agent_id)
        
        if not response.ok:
            console.print(f"[bold red]Error:[/bold red] Configuration for agent '{agent_id}' not found")
            return
            
        utils.log_response(response)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


def print_agents_config() -> None:
    """Display configuration for all agents."""
    try:
        response = get_agents()
        
        if not response.ok:
            console.print(f"[bold red]Error:[/bold red] Failed to fetch agents")
            utils.log_response(response)
            return

        agents = response.json().get('data', [])
        
        if not agents:
            console.print("[yellow]No agents found.[/yellow]\n")
            return

        console.print(Panel.fit(
            f"[bold cyan]Fetching configuration for {len(agents)} agent(s)...[/bold cyan]",
            border_style="cyan"
        ))

        for data in agents:
            agent_id = data['id']
            agent_name = data.get('attributes', {}).get('agentName', 'Unknown')
            
            console.print(f"\n[bold green]Agent:[/bold green] {agent_name} (ID: {agent_id})")
            console.rule(style="green")
            
            response = get_agent_config(agent_id)
            utils.log_response(response)
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


def delete_sessions(prefix: str) -> None:
    """Delete sessions matching a prefix."""
    try:
        response = get_sessions()
        
        if not response.ok:
            console.print(f"[bold red]Error:[/bold red] Failed to fetch sessions")
            utils.log_response(response)
            return

        data = response.json().get('data', [])
        sessions = [
            session.get('attributes', {}).get('session', {}).get('sessionId') 
            for session in data
        ]
        
        # Filter sessions by prefix
        sessions_to_delete = [
            session_id for session_id in sessions 
            if prefix == "all" or session_id.startswith(prefix)
        ]

        if not sessions_to_delete:
            console.print(f"[yellow]No sessions found matching prefix '{prefix}'[/yellow]")
            return

        console.print(f"[bold yellow]Found {len(sessions_to_delete)} session(s) to delete:[/bold yellow]")
        for session_id in sessions_to_delete:
            console.print(f"  • {session_id}")

        # Confirm deletion
        console.print("\n[bold red]⚠ This action cannot be undone![/bold red]")
        confirm = console.input("[bold]Proceed with deletion? (yes/no): [/bold]")
        
        if confirm.lower() not in ['yes', 'y']:
            console.print("[yellow]Deletion cancelled.[/yellow]")
            return

        # Delete sessions
        success_count = 0
        for session_id in sessions_to_delete:
            console.print(f"[cyan]Deleting session:[/cyan] {session_id} ...", end=" ")
            response = delete_session(session_id)
            
            if response.ok:
                console.print("[green]✓ Success[/green]")
                success_count += 1
            else:
                console.print("[red]✗ Failed[/red]")
                utils.log_response(response)

        console.print(f"\n[bold green]Successfully deleted {success_count}/{len(sessions_to_delete)} session(s)[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


# ============================================================================
# Custom Formatter for argparse
# ============================================================================

class CustomHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Custom formatter for better help text layout."""
    
    def __init__(self, prog, indent_increment=2, max_help_position=35, width=None):
        super().__init__(prog, indent_increment, max_help_position, width)
    
    def _format_action_invocation(self, action):
        """Format action invocation to add color to metavars."""
        if not action.option_strings:
            default = self._get_default_metavar_for_positional(action)
            metavar, = self._metavar_formatter(action, default)(1)
            return metavar
        else:
            parts = []
            if action.nargs == 0:
                parts.extend(action.option_strings)
            else:
                default = self._get_default_metavar_for_optional(action)
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append(option_string)
                return '%s %s' % (', '.join(parts), args_string)
            return ', '.join(parts)


# ============================================================================
# Argument Parser Setup
# ============================================================================

def build_parser() -> argparse.ArgumentParser:
    """Build and configure the argument parser."""
    
    # Create description with visual formatting
    description = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    Sensor Agent API CLI Tool                             ║
╚══════════════════════════════════════════════════════════════════════════╝

API Endpoint: {orchestrator.get_url_info()}
"""
    
    epilog = """
"""
    
    parser = argparse.ArgumentParser(
        prog='agent.py',
        description=description,
        epilog=epilog,
        formatter_class=CustomHelpFormatter,
        add_help=True
    )

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="COMMAND",
        title="Available Commands",
        description="Use one of the following commands to interact with the Sensor Agent API"
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
        help="Perform a GET request to a specified URI",
        description="Executes a GET request to retrieve data from the API.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("uri", metavar="URI", help="URI path to request (relative to base URL)")
    sp.set_defaults(func=lambda a: send_request("GET", f"{orchestrator.get_url()}/{a.uri}"))

    sp = subparsers.add_parser(
        "post",
        help="Perform a POST request to a specified URI",
        description="Executes a POST request to create or submit data to the API.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("uri", metavar="URI", help="URI path to request (relative to base URL)")
    sp.set_defaults(func=lambda a: send_request("POST", f"{orchestrator.get_url()}/{a.uri}"))

    sp = subparsers.add_parser(
        "put",
        help="Perform a PUT request to a specified URI",
        description="Executes a PUT request to update existing data on the API.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("uri", metavar="URI", help="URI path to request (relative to base URL)")
    sp.set_defaults(func=lambda a: send_request("PUT", f"{orchestrator.get_url()}/{a.uri}"))

    sp = subparsers.add_parser(
        "patch",
        help="Perform a PATCH request to a specified URI",
        description="Executes a PATCH request to partially update data on the API.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("uri", metavar="URI", help="URI path to request (relative to base URL)")
    sp.set_defaults(func=lambda a: send_request("PATCH", f"{orchestrator.get_url()}/{a.uri}"))

    sp = subparsers.add_parser(
        "delete",
        help="Perform a DELETE request to a specified URI",
        description="Executes a DELETE request to remove data from the API.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("uri", metavar="URI", help="URI path to request (relative to base URL)")
    sp.set_defaults(func=lambda a: send_request("DELETE", f"{orchestrator.get_url()}/{a.uri}"))

    # ========================================================================
    # Session Management Commands
    # ========================================================================
    
    sp = subparsers.add_parser(
        "get_sessions",
        help="Retrieve all active sessions",
        description="Fetches and displays all currently active sessions from the API.",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: print_sessions())

    sp = subparsers.add_parser(
        "get_sessions_status",
        help="Retrieve status for all sessions",
        description="Displays the status of all sessions in a formatted table.",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: print_sessions_status())

    sp = subparsers.add_parser(
        "get_session_status",
        help="Retrieve status for a specific session",
        description="Fetches and displays the status of a single session by ID.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("session_id", metavar="SESSION_ID", help="The ID of the session to query")
    sp.set_defaults(func=lambda a: print_session_status(a.session_id))

    sp = subparsers.add_parser(
        "delete_sessions",
        help="Delete sessions matching a prefix",
        description="""Delete all sessions that start with the specified prefix.
Use "all" to delete all sessions.

WARNING: This operation cannot be undone!
You will be prompted for confirmation before deletion.""",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument(
        "prefix",
        metavar="PREFIX",
        help='Session ID prefix to match (use "all" to delete all sessions)'
    )
    sp.set_defaults(func=lambda a: delete_sessions(a.prefix))

    # ========================================================================
    # Agent Management Commands
    # ========================================================================
    
    sp = subparsers.add_parser(
        "get_agents",
        help="Retrieve all registered agents",
        description="Fetches and displays all agents registered with the API in a formatted table.",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: print_agents())

    sp = subparsers.add_parser(
        "get_agent",
        help="Retrieve details for a specific agent",
        description="Fetches and displays detailed information about a single agent by ID.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("agent_id", metavar="AGENT_ID", help="The ID of the agent to query")
    sp.set_defaults(func=lambda a: print_agent(a.agent_id))

    sp = subparsers.add_parser(
        "get_agents_config",
        help="Retrieve configuration for all agents",
        description="Fetches and displays the configuration for all registered agents.",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: print_agents_config())

    sp = subparsers.add_parser(
        "get_agent_config",
        help="Retrieve configuration for a specific agent",
        description="Fetches and displays the configuration for a single agent by ID.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("agent_id", metavar="AGENT_ID", help="The ID of the agent to query")
    sp.set_defaults(func=lambda a: print_agent_config(a.agent_id))


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
            import traceback
            if '--debug' in sys.argv:
                traceback.print_exc()
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()