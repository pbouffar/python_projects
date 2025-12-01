#!/usr/bin/env python3
"""
  Copyright (c) 2025 Cisco Systems, Inc.
  All rights reserved.

  This code is provided under the terms of the Cisco Software License Agreement.
  Unauthorized copying, modification, or distribution is strictly prohibited.

  Cisco Systems,Inc.
  170 West Tasman Drive,San Jose,CA 95134,USA
"""

import traceback
import argparse
import json
import sys
from typing import Optional, Dict, Any
import urllib3

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn

import utils
from config import analytics as orchestrator

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
# Alerting Policy Management
# ============================================================================

def get_alerting_policy_with_tag(tag: str):
    """Get alerting policies filtered by tag."""
    url = f"/api/v2/policies/alerting?tag={tag}"
    return orchestrator.get(url)


def print_alerting_policy_with_tag(tag: str) -> None:
    """Display alerting policies with a specific tag."""
    try:
        response = get_alerting_policy_with_tag(tag)

        if not response.ok:
            console.print(f"[bold red]Error:[/bold red] Failed to fetch alerting policies with tag '{tag}'")
            utils.log_response(response)
            return

        policies = response.json().get('data', [])

        if not policies:
            console.print(f"[yellow]No alerting policies found with tag '{tag}'[/yellow]")
            return

        console.print(f"\n[bold cyan]Alerting Policies with tag '{tag}':[/bold cyan]")
        utils.log_response(response)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


def get_alerting_policies():
    """Get all alerting policies."""
    url = "/api/v2/policies/alerting"
    return orchestrator.get(url)


def print_alerting_policies() -> None:
    """Display all alerting policies."""
    try:
        response = get_alerting_policies()

        if not response.ok:
            console.print("[bold red]Error:[/bold red] Failed to fetch alerting policies")
            utils.log_response(response)
            return

        policies = response.json().get('data', [])

        if not policies:
            console.print("[yellow]No alerting policies found[/yellow]")
            return

        # Create a rich table
        table = Table(
            title=f"Alerting Policies ({len(policies)} total)",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("ID", style="green", width=36)
        table.add_column("Name", style="magenta", width=30)
        table.add_column("Status", style="yellow", width=12)
        table.add_column("Tags", style="blue", no_wrap=False)

        for policy in policies:
            policy_id = str(policy.get('id', 'N/A'))
            name = policy.get('attributes', {}).get('name', 'N/A')
            status = policy.get('attributes', {}).get('status', 'N/A')
            tags = ', '.join(policy.get('attributes', {}).get('tags', []))

            # Color code status
            if status.lower() == 'enabled':
                status_display = f"[green]{status}[/green]"
            elif status.lower() == 'disabled':
                status_display = f"[red]{status}[/red]"
            else:
                status_display = status

            table.add_row(policy_id, name, status_display, tags)

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


def delete_alerting_policy_v2(policy_id: str):
    """Delete alerting policy using v2 API."""
    url = f"/api/v2/policies/alerting/{policy_id}"
    response = orchestrator.delete(url)
    return response


def delete_alerting_policy_v3(policy_id: str, ignore_alerts: bool = True):
    """Delete alerting policy using v3 API."""
    url = f"/api/v3/policies/alerting/{policy_id}"
    params = {'ignoreAlerts': str(ignore_alerts).lower()}
    response = orchestrator.delete(url, params=params)
    return response


def delete_all_policies() -> None:
    """Delete all alerting policies (both v2 and v3)."""
    try:
        console.print("[bold cyan]Fetching all policies...[/bold cyan]")
        get_resp = get_alerting_policies()

        if not get_resp.ok:
            console.print("[bold red]Error:[/bold red] Failed to fetch policies")
            utils.log_response(get_resp)
            return

        policies = get_resp.json().get('data', [])
        policy_ids = [policy['id'] for policy in policies]

        if not policy_ids:
            console.print("[yellow]No policies found to delete[/yellow]")
            return

        console.print(f"[bold yellow]Found {len(policy_ids)} policy/policies:[/bold yellow]")
        for pid in policy_ids:
            console.print(f"  • {pid}")

        # Confirm deletion
        console.print("\n[bold red]⚠ This action cannot be undone![/bold red]")
        confirm = console.input("[bold]Proceed with deletion? (yes/no): [/bold]")

        if confirm.lower() not in ['yes', 'y']:
            console.print("[yellow]Deletion cancelled.[/yellow]")
            return

        # Delete policies
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Deleting policies...", total=len(policy_ids) * 2)

            for policy_id in policy_ids:
                # Try v2 API
                progress.update(task, description=f"[cyan]Deleting {policy_id} (v2)...")
                del_resp_v2 = delete_alerting_policy_v2(policy_id)

                if del_resp_v2.ok:
                    console.print(f"[green]✓[/green] Deleted {policy_id} via v2 API")
                else:
                    console.print(f"[yellow]⚠[/yellow] v2 deletion failed for {policy_id}: {del_resp_v2.status_code}")

                progress.advance(task)

                # Try v3 API
                progress.update(task, description=f"[cyan]Deleting {policy_id} (v3)...")
                del_resp_v3 = delete_alerting_policy_v3(policy_id, ignore_alerts=True)

                if del_resp_v3.ok:
                    console.print(f"[green]✓[/green] Deleted {policy_id} via v3 API")
                else:
                    console.print(f"[yellow]⚠[/yellow] v3 deletion failed for {policy_id}: {del_resp_v3.status_code}")

                progress.advance(task)

        console.print("\n[bold green]Policy deletion completed![/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


# ============================================================================
# Monitored Objects Management
# ============================================================================

def create_monitored_object(data: Dict[str, Any]):
    """Create a new monitored object."""
    url = "/api/v2/monitored-objects"
    return send_request("POST", url, body=data)


def update_monitored_object(object_id: str, data: Dict[str, Any]):
    """Update an existing monitored object."""
    url = f"/api/v2/monitored-objects/{object_id}"
    return send_request("PATCH", url, body=data)


def delete_monitored_object(object_id: str):
    """Delete a monitored object."""
    url = f"/api/v2/monitored-objects/{object_id}"
    return send_request("DELETE", url)


def get_monitored_object(object_id: str):
    """Get a specific monitored object."""
    url = f"/api/v2/monitored-objects/{object_id}"
    response = send_request("GET", url)

    if not response.ok:
        console.print(f"[bold red]Error:[/bold red] Monitored object '{object_id}' not found")
        return response

    utils.log_response(response)
    return response


def get_monitored_objects():
    """Get all monitored objects."""
    url = "/api/v2/monitored-objects"
    response = send_request("GET", url)

    if not response.ok:
        console.print("[bold red]Error:[/bold red] Failed to fetch monitored objects")
        return response

    objects = response.json().get('data', [])

    if not objects:
        console.print("[yellow]No monitored objects found[/yellow]")
        return response

    # Create a rich table
    table = Table(
        title=f"Monitored Objects ({len(objects)} total)",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    table.add_column("ID", style="green", width=40)
    table.add_column("Type", style="blue", width=20)
    table.add_column("Name", style="magenta", no_wrap=False)

    for obj in objects:
        obj_id = str(obj.get('id', 'N/A'))
        obj_type = obj.get('type', 'N/A')
        obj_name = obj.get('attributes', {}).get('name', 'N/A')

        table.add_row(obj_id, obj_type, obj_name)

    console.print(table)
    console.print()

    return response


def get_monitored_object_ids_with_name(data: Dict[str, Any]):
    """Get monitored object IDs filtered by name."""
    url = "/api/v2/monitored-objects/id-list"
    return send_request("POST", url, body=data)


def get_monitored_object_stitchit(session_id: str):
    """Get monitored object from StitchIt API."""
    url = f"/api/v1/stitchit/monitoredObjects?objectId={session_id}"
    return send_request("GET", url)


# ============================================================================
# Metadata Management
# ============================================================================

def update_metadata_mapping(data: Dict[str, Any]):
    """Update metadata category mappings."""
    url = "/api/v2/metadata-category-mappings/activeMetrics"
    return send_request("PATCH", url, body=data)


def get_metadata_mapping():
    """Get metadata category mappings."""
    url = "/api/v2/metadata-category-mappings/activeMetrics"
    response = send_request("GET", url)

    if not response.ok:
        console.print("[bold red]Error:[/bold red] Failed to fetch metadata mapping")
        return response

    utils.log_response(response)
    return response


def get_all_tenant_metadata():
    """Get metadata for all tenants."""
    url = "/api/v2/tenant-metadata"
    return send_request("GET", url)


def get_tenant_metadata(tenant_id: str):
    """Get metadata for a specific tenant."""
    url = f"/api/v2/tenant-metadata/{tenant_id}"
    return orchestrator.get(url)


def print_tenant_metadata(tenant_id: str) -> None:
    """Display tenant metadata."""
    try:
        response = get_tenant_metadata(tenant_id)

        if not response.ok:
            console.print(f"[bold red]Error:[/bold red] Failed to fetch tenant metadata for '{tenant_id}'")
            return

        console.print(f"\n[bold cyan]Tenant Metadata for {tenant_id}:[/bold cyan]")
        utils.log_response(response)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


def update_tenant_metadata(tenant_id: str, data: Dict[str, Any]):
    """Update tenant metadata."""
    url = f"/api/v2/tenant-metadata/{tenant_id}"
    response = orchestrator.patch(url, body=data)

    if not response.ok:
        utils.log_response(response)

    return response


def set_tenant_metadata_store_metadata_value_casesensitive_to_true() -> None:
    """Set storeMetadataValueCaseSensitive to true in tenant metadata."""
    try:
        tenant_id = orchestrator.get_tenant_id()
        console.print(f"[cyan]Fetching tenant metadata for {tenant_id}...[/cyan]")

        resp = get_tenant_metadata(tenant_id)
        if not resp.ok:
            console.print("[bold red]Error:[/bold red] Failed to fetch tenant metadata")
            utils.log_response(resp)
            return

        metadata = json.loads(resp.content)
        store_metadata_value_case_sensitive = (
            metadata.get('data', {})
            .get('attributes', {})
            .get('storeMetadataValueCaseSensitive')
        )

        if store_metadata_value_case_sensitive is None or store_metadata_value_case_sensitive is False:
            console.print("[yellow]Setting storeMetadataValueCaseSensitive to true...[/yellow]")
            metadata['data']['attributes']['storeMetadataValueCaseSensitive'] = True

            resp = update_tenant_metadata(tenant_id, metadata)
            if resp.ok:
                console.print(
                    "[bold green]✓ Successfully set [bold]storeMetadataValueCaseSensitive[/bold] to true.[/bold green]"
                )
            else:
                console.print("[bold red]Error:[/bold red] Failed to update tenant metadata")
                utils.log_response(resp)
        else:
            console.print(
                "[bold cyan]ℹ[/bold cyan] [bold]storeMetadataValueCaseSensitive[/bold] is already set to "
                f"{'[green]true[/green]' if store_metadata_value_case_sensitive else '[red]false[/red]'}"
            )

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


def get_metadata_categories():
    """Get metadata categories."""
    url = "/api/v2/metadata-category-mappings/activeMetrics"
    return send_request("GET", url)


def verify_metadata_categories() -> None:
    """Verify that required metadata categories exist."""
    try:
        console.print("[cyan]Verifying metadata categories...[/cyan]\n")

        resp = get_metadata_categories()
        if not resp.ok:
            console.print("[bold red]Error:[/bold red] Failed to fetch metadata categories")
            return

        data = json.loads(resp.content).get('data', {}).get('attributes', {}).get('metadataCategoryMap')
        expected = ["service_id", "ne_id_sender", "service_name", "ne_id_reflector"]

        if not data:
            console.print("[yellow]No metadata categories found[/yellow]")
            return

        # Find active categories
        found = []
        for key in data.keys():
            is_active = data[key].get('isActive')
            if is_active:
                found.append(data[key].get('name'))

        # Create results table
        table = Table(
            title="Metadata Category Verification",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("Category", style="blue", width=30)
        table.add_column("Status", style="white", width=15)

        for category in expected:
            if category in found:
                table.add_row(category, "[green]✓ Found[/green]")
            else:
                table.add_row(category, "[red]✗ Missing[/red]")

        console.print(table)
        console.print()

        # Summary
        not_found = [x for x in expected if x not in found]
        if not_found:
            console.print(
                f"[bold red]FAIL![/bold red] Missing {len(not_found)} metadata "
                f"categor{'y' if len(not_found) == 1 else 'ies'}:"
            )
            for cat in not_found:
                console.print(f"  • {cat}")
        else:
            console.print("[bold green]PASS![/bold green] All expected metadata categories exist.")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


# ============================================================================
# Ingestion Profiles & Metrics
# ============================================================================

def get_ingestion_profiles():
    """Get ingestion profiles."""
    url = "/api/v2/ingestion-profiles"
    return send_request("GET", url)


# Expected TWAMP-SF metrics
EXPECTED_TWAMPSF_METRICS = [
    "delayAvg", "delayMax", "delayMin", "delayP25", "delayP50", "delayP75", "delayP95",
    "delayPHi", "delayPLo", "delayPMi", "delayStdDevAvg", "delayVarAvg", "delayVarMax",
    "delayVarMin", "delayVarP25", "delayVarP50", "delayVarP75", "delayVarP95", "delayVarPHi",
    "delayVarPLo", "delayVarPMi", "duration", "fCongestion", "jitterAvg", "jitterMax",
    "jitterP95", "jitterPHi", "jitterPLo", "jitterPMi", "jitterStdDev", "lostBurstMax",
    "packetsLost", "packetsLostPct", "packetsReceived", "periodsLost", "syncQuality", "syncState"
]


def verify_twampsf_metrics() -> None:
    """Verify that required TWAMP-SF metrics are enabled."""
    try:
        console.print("[cyan]Verifying TWAMP-SF metrics...[/cyan]\n")

        resp = get_ingestion_profiles()
        if not resp.ok:
            console.print("[bold red]Error:[/bold red] Failed to fetch ingestion profiles")
            return

        data = json.loads(resp.content).get('data', [])

        if not data:
            console.print("[yellow]No ingestion profiles found[/yellow]")
            return

        # Find enabled TWAMP-SF metrics
        found = []
        for item in data:
            metrics = item.get('attributes', {}).get('metrics', {}).get('vendorMap', {})
            if metrics:
                for key in metrics:
                    if key == "accedian-twamp":
                        metric_map = (
                            metrics[key]
                            .get('monitoredObjectTypeMap', {})
                            .get('twamp-sf', {})
                            .get('metricMap', {})
                        )
                        for metric_key in metric_map:
                            if metric_map[metric_key] is True:
                                found.append(metric_key)

        # Create results table
        table = Table(
            title=f"TWAMP-SF Metrics Verification ({len(EXPECTED_TWAMPSF_METRICS)} total)",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("Metric", style="blue", width=25)
        table.add_column("Status", style="white", width=15)

        for metric in EXPECTED_TWAMPSF_METRICS:
            if metric in found:
                table.add_row(metric, "[green]✓ Enabled[/green]")
            else:
                table.add_row(metric, "[red]✗ Disabled[/red]")

        console.print(table)
        console.print()

        # Summary
        not_found = [x for x in EXPECTED_TWAMPSF_METRICS if x not in found]
        if not_found:
            console.print(
                f"[bold red]FAIL![/bold red] {len(not_found)} metric{'s are' if len(not_found) > 1 else ' is'} disabled:"
            )
            for metric in not_found:
                console.print(f"  • {metric}")
        else:
            console.print("[bold green]PASS![/bold green] All expected TWAMP-SF metrics are enabled.")

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
║                    Analytics REST API CLI Tool                           ║
╚══════════════════════════════════════════════════════════════════════════╝

API Endpoint: {orchestrator.get_url_info()}
"""

    epilog = """
"""

    parser = argparse.ArgumentParser(
        prog='analytics.py',
        description=description,
        epilog=epilog,
        formatter_class=CustomHelpFormatter,
        add_help=True
    )

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="COMMAND",
        title="Available Commands",
        description="Use one of the following commands to interact with the Analytics REST API"
    )

    add_commands(subparsers)
    return parser


def add_commands(subparsers):
    """Add all subcommands to the parser."""

    # ========================================================================
    # Monitored Objects Commands
    # ========================================================================

    sp = subparsers.add_parser(
        "get_monitored_object",
        help="Get details for a specific monitored object",
        description="Fetches and displays information about a single monitored object by ID.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("object_id", metavar="OBJECT_ID", help="The ID of the monitored object")
    sp.set_defaults(func=lambda a: get_monitored_object(a.object_id))

    sp = subparsers.add_parser(
        "get_monitored_objects",
        help="Get all monitored objects",
        description="Fetches and displays all monitored objects in a formatted table.",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: get_monitored_objects())

    # ========================================================================
    # Metadata Commands
    # ========================================================================

    sp = subparsers.add_parser(
        "get_metadata_mapping",
        help="Get metadata category mappings",
        description="Fetches and displays the current metadata category mappings.",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: get_metadata_mapping())

    sp = subparsers.add_parser(
        "get_tenant_metadata",
        help="Get tenant metadata",
        description="Fetches and displays metadata for the current tenant.",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: print_tenant_metadata(orchestrator.get_tenant_id()))

    sp = subparsers.add_parser(
        "update_tenant_metadata",
        help="Update tenant metadata from file",
        description="Updates tenant metadata using data from a JSON file.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument(
        "patched_data_filename",
        metavar="FILE",
        help="Path to JSON file containing updated metadata"
    )
    sp.set_defaults(func=lambda a: update_tenant_metadata(
        orchestrator.get_tenant_id(),
        a.patched_data_filename
    ))

    sp = subparsers.add_parser(
        "patch_storeMetadataValueCaseSensitive",
        help="Enable case-sensitive metadata values",
        description="Sets the storeMetadataValueCaseSensitive attribute to true in tenant metadata.",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: set_tenant_metadata_store_metadata_value_casesensitive_to_true())

    # ========================================================================
    # Policy Commands
    # ========================================================================

    sp = subparsers.add_parser(
        "delete_all_policies",
        help="Delete all alerting policies",
        description="""Delete all alerting policies using both v2 and v3 APIs.

WARNING: This operation cannot be undone!
You will be prompted for confirmation before deletion.""",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: delete_all_policies())

    sp = subparsers.add_parser(
        "get_alerting_policy",
        help="Get alerting policies by tag",
        description="Fetches and displays alerting policies filtered by a specific tag.",
        formatter_class=CustomHelpFormatter
    )
    sp.add_argument("tag", metavar="TAG", help="Tag to filter policies by")
    sp.set_defaults(func=lambda a: print_alerting_policy_with_tag(a.tag))

    sp = subparsers.add_parser(
        "get_alerting_policies",
        help="Get all alerting policies",
        description="Fetches and displays all alerting policies in a formatted table.",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: print_alerting_policies())

    # ========================================================================
    # Verification Commands
    # ========================================================================

    sp = subparsers.add_parser(
        "verify_metadata_categories",
        help="Verify required metadata categories",
        description="""Verifies that all required metadata categories exist and are active.

Required categories:
  • service_id
  • ne_id_sender
  • service_name
  • ne_id_reflector""",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: verify_metadata_categories())

    sp = subparsers.add_parser(
        "verify_twampsf_metrics",
        help="Verify TWAMP-SF metrics are enabled",
        description=f"""Verifies that all required TWAMP-SF metrics are enabled.

Checks {len(EXPECTED_TWAMPSF_METRICS)} metrics including:
  • Delay metrics (avg, min, max, percentiles)
  • Jitter metrics
  • Packet loss metrics
  • Synchronization metrics""",
        formatter_class=CustomHelpFormatter
    )
    sp.set_defaults(func=lambda a: verify_twampsf_metrics())


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
                traceback.print_exc()
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
