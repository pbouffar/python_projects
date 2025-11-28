#!/usr/bin/env python3
#  Copyright (c) 2025 Cisco Systems, Inc.
#  All rights reserved.
#
#  This code is provided under the terms of the Cisco Software License Agreement.
#  Unauthorized copying, modification, or distribution is strictly prohibited.
#
#  Cisco Systems,Inc.
#  170 West Tasman Drive,San Jose,CA 95134,USA
import argparse
import json
import requests
import sys
import urllib3

import utils
from config import get_tenant_id, get_user_roles
from config import ygw as orchestrator

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def send_request(method, url, body=None, params=None):
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
    utils.log_response(resp)

class CustomFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

def build_parser():
    parser = argparse.ArgumentParser(
        description=f"CLI for Yang-Gateway RESTCONF API: {orchestrator.get_url_info()}",
        formatter_class=CustomFormatter
    )
    subparsers = parser.add_subparsers(dest="command", title="Commands", metavar="<command>")
    add_commands(subparsers)
    return parser

def add_commands(subparsers):

    """
    # Generic data resource operations
    sp = subparsers.add_parser("get_data_identifier",
                               help="GET /restconf/data/{identifier}")
    sp.add_argument("identifier", help="YANG data resource path")
    sp.set_defaults(func=lambda a: send_request("GET", f"{BASE_URL}/restconf/data/{a.identifier}"))

    sp = subparsers.add_parser("put_data_identifier",
                               help="PUT /restconf/data/{identifier} (replace)")
    sp.add_argument("identifier")
    sp.add_argument("--body", required=True, help="JSON file")
    sp.set_defaults(func=lambda a: send_request("PUT", f"{BASE_URL}/restconf/data/{a.identifier}", body=a.body))

    sp = subparsers.add_parser("post_data_identifier",
                               help="POST /restconf/data/{identifier} (create)")
    sp.add_argument("identifier")
    sp.add_argument("--body", required=True, help="JSON file")
    sp.set_defaults(func=lambda a: send_request("POST", f"{BASE_URL}/restconf/data/{a.identifier}", body=a.body))

    sp = subparsers.add_parser("patch_data_identifier",
                               help="PATCH /restconf/data/{identifier} (merge)")
    sp.add_argument("identifier")
    sp.add_argument("--body", required=True, help="JSON file")
    sp.set_defaults(func=lambda a: send_request("PATCH", f"{BASE_URL}/restconf/data/{a.identifier}", body=a.body))

    # Param variants
    sp = subparsers.add_parser("get_data_identifier_param",
                               help="GET /restconf/data/{identifier}{param}")
    sp.add_argument("identifier")
    sp.add_argument("param")
    sp.set_defaults(func=lambda a: send_request("GET", f"{BASE_URL}/restconf/data/{a.identifier}{a.param}"))

    sp = subparsers.add_parser("delete_data_identifier_param",
                               help="DELETE /restconf/data/{identifier}{param}")
    sp.add_argument("identifier")
    sp.add_argument("param")
    sp.set_defaults(func=lambda a: send_request("DELETE", f"{BASE_URL}/restconf/data/{a.identifier}{a.param}"))

    sp = subparsers.add_parser("delete_data_identifier_param_param2",
                               help="DELETE /restconf/data/{identifier}{param}{param2}")
    sp.add_argument("identifier")
    sp.add_argument("param")
    sp.add_argument("param2")
    sp.set_defaults(func=lambda a: send_request("DELETE", f"{BASE_URL}/restconf/data/{a.identifier}{a.param}{a.param2}"))

    # RPC / operations
    sp = subparsers.add_parser("post_data_identifier_param_id_action",
                               help="POST /restconf/data/{identifier}/{param}={id}/{action}")
    sp.add_argument("identifier")
    sp.add_argument("param")
    sp.add_argument("id")
    sp.add_argument("action")
    sp.set_defaults(func=lambda a: send_request(
        "POST", f"{BASE_URL}/restconf/data/{a.identifier}/{a.param}={a.id}/{a.action}"))

    sp = subparsers.add_parser("post_operations_identifier",
                               help="POST /restconf/operations/{identifier} (invoke RPC)")
    sp.add_argument("identifier")
    sp.add_argument("--body", required=True, help="JSON file")
    sp.set_defaults(func=lambda a: send_request(
        "POST", f"{BASE_URL}/restconf/operations/{a.identifier}", body=a.body))

    # Discovery
    for name, path, h in [
        ("get_well_known_host_meta", "/.well-known/host-meta", "GET /.well-known/host-meta"),
        ("get_well_known_host_meta_json", "/.well-known/host-meta.json", "GET /.well-known/host-meta.json"),
        ("get_modules_identifier", "/restconf/modules/{identifier}", "GET /restconf/modules/{identifier}"),
        ("get_ietf_yang_library", "/restconf/ietf-yang-library:yang-library", "GET yang-library"),
        ("get_yang_library_version", "/restconf/yang-library-version", "GET yang-library-version"),
        ("get_operations", "/restconf/operations", "GET list of RPC operations"),
        ("get_streams", "/restconf/data/ietf-restconf-monitoring:restconf-state/streams", "GET event streams"),
    ]:
        sp = subparsers.add_parser(name, help=h)
        if "{identifier}" in path:
            sp.add_argument("identifier")
            sp.set_defaults(func=lambda a, p=path: send_request(
                "GET", f"{BASE_URL}{p.replace('{identifier}', a.identifier)}"))
        else:
            sp.set_defaults(func=lambda a, p=path: send_request("GET", f"{BASE_URL}{p}"))

    sp = subparsers.add_parser("get_streams_stream_identifier",
                               help="GET a specific stream")
    sp.add_argument("identifier")
    sp.set_defaults(func=lambda a: send_request(
        "GET", f"{BASE_URL}/restconf/data/ietf-restconf-monitoring:restconf-state/streams/stream={a.identifier}"))
    """

    sp = subparsers.add_parser("get", help="GET method")
    sp.add_argument("uri")
    sp.set_defaults(func=lambda a: send_request("GET", f"{a.uri}"))

    sp = subparsers.add_parser("post", help="POST method")
    sp.add_argument("uri")
    sp.set_defaults(func=lambda a: send_request("POST", f"{a.uri}"))

    sp = subparsers.add_parser("put", help="PUT method")
    sp.add_argument("uri")
    sp.set_defaults(func=lambda a: send_request("PUT", f"{a.uri}"))

    sp = subparsers.add_parser("patch", help="PATCH method")
    sp.add_argument("uri")
    sp.set_defaults(func=lambda a: send_request("PATCH", f"{a.uri}"))

    sp = subparsers.add_parser("delete",help="DELETE method")
    sp.add_argument("uri")
    sp.set_defaults(func=lambda a: send_request("DELETE", f"{a.uri}"))

    # Convenience domain-specific helpers
    sp = subparsers.add_parser("get_endpoints",help="GET all endpoints")
    sp.set_defaults(func=lambda a: send_request(
        "GET", f"/restconf/data/Accedian-service-endpoint:service-endpoints"))

    sp = subparsers.add_parser("get_endpoint", help="GET a specific endpoint")
    sp.add_argument("identifier")
    sp.set_defaults(func=lambda a: send_request(
        "GET", f"/restconf/data/Accedian-service-endpoint:service-endpoints/service-endpoint={a.identifier}"))

    sp = subparsers.add_parser("get_alerts", help="GET all alert policies")
    sp.set_defaults(func=lambda a: send_request(
        "GET", f"/restconf/data/Accedian-alert:alert-policies"))

    sp = subparsers.add_parser("get_sessions", help="GET all sessions")
    sp.set_defaults(func=lambda a: send_request(
        "GET", f"/restconf/data/Accedian-session:sessions"))

    sp = subparsers.add_parser("get_session", help="GET a specific session")
    sp.add_argument("identifier")
    sp.set_defaults(func=lambda a: send_request(
        "GET", f"/restconf/data/Accedian-session:sessions/session={a.identifier}"))

    sp = subparsers.add_parser("get_services", help="GET all services")
    sp.set_defaults(func=lambda a: send_request(
        "GET", f"/restconf/data/Accedian-service:services"))

    sp = subparsers.add_parser("get_metadata", help="GET all metadata-config")
    sp.set_defaults(func=lambda a: send_request(
        "GET", f"/restconf/data/Accedian-metadata:metadata-config"))

def main():
    parser = build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        return
    args = parser.parse_args()
    if hasattr(args, "func"):
        orchestrator.login()
        args.func(args)
        orchestrator.logout()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
