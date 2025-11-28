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
import sys

import requests
import urllib3

import utils
from config import so as orchestrator

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def send_request(method, url, body=None):
    resp = orchestrator.send_request(method, url, body)
    #utils.log_response(resp)
    return resp

def print_echo_session(identifier):
    response = send_request("GET", f"/nbapi/session/echo/{identifier}")
    utils.log_response(response)

def print_twamp_session(identifier):
    response = send_request("GET", f"/nbapi/session/twamp/{identifier}")
    utils.log_response(response)

def print_all_y1564_sessions():
    response = send_request("GET", f"/nbapiemswsweb/rest/v1/Search/Y1564TestConfig")
    if not response.ok:
        utils.log_response(response)
        return
    content =  response.json().get('content', [])
    if len(content) > 0:
        print("Y1564:\n", json.dumps(content, indent=4))
    else:
        print("Y1564:\nNo session found.")

def print_all_rfc2544_sessions():
    response = send_request("GET", f"/nbapiemswsweb/rest/v1/Search/RFC2544TestConfig")
    if not response.ok:
        utils.log_response(response)
        return
    content =  response.json().get('content', [])
    if len(content) > 0:
        print("RFC2544:\n", json.dumps(content, indent=4))
    else:
        print("RFC2544:\nNo session found.")

def print_all_sat_sessions():
    print_all_y1564_sessions()
    print_all_rfc2544_sessions()

class CustomFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

def build_parser():
    parser = argparse.ArgumentParser(
        description=f"CLI for Sensor Orchestrator API: {orchestrator.get_url_info()}",
        formatter_class=CustomFormatter
    )
    subparsers = parser.add_subparsers(dest="command", title="Commands", metavar="<command>")
    add_commands(subparsers)
    return parser

def add_commands(subparsers):

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
    """

    # Convenience domain-specific helpers
    sp = subparsers.add_parser("get_session_echo", help="GET a specific echo session")
    sp.add_argument("identifier")
    sp.set_defaults(func=lambda a: print_echo_session(a.identifier))

    sp = subparsers.add_parser("get_session_twamp", help="GET a specific twamp session")
    sp.add_argument("identifier")
    sp.set_defaults(func=lambda a: print_twamp_session(a.identifier))

    sp = subparsers.add_parser("get_sessions_y1564", help="GET all Y1564 sessions")
    sp.set_defaults(func=lambda a: print_all_y1564_sessions())

    sp = subparsers.add_parser("get_sessions_rfc2544", help="GET all RFC2544 sessions")
    sp.set_defaults(func=lambda a: print_all_rfc2544_sessions())

    sp = subparsers.add_parser("get_sessions_sat", help="GET all SAT sessions")
    sp.set_defaults(func=lambda a: print_all_sat_sessions())

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
