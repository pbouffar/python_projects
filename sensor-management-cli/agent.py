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
from config import agent as orchestrator

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


API_URL = "/api/orchestrate/v3/agents"

def send_request(method, url, body=None):
    resp = orchestrator.send_request(method, url, body)
    utils.log_response(resp)

def create_session(data):
    url = f"{API_URL}/session"
    return orchestrator.post(url, body=data)

def get_session(session_id):
    url = f"{API_URL}/session/{session_id}"
    return orchestrator.get(url)

def get_sessions():
    url = f"{API_URL}/sessions"
    return orchestrator.get(url)

def update_session(data):
    url = f"{API_URL}/session"
    return orchestrator.put(url, body=data)

def delete_session(session_id):
    url = f"{API_URL}/session/{session_id}"
    print(url)
    return orchestrator.delete(url)

def get_agents():
    url = f"{API_URL}"
    header = { "Content-type": "application/vnd.api+json" }
    return orchestrator.get(url, headers=header)

def get_agent(agent_id):
    url = f"{API_URL}/{agent_id}"
    header = { "Content-type": "application/vnd.api+json" }
    return orchestrator.get(url, headers=header)

def get_agent_config(agent_id):
    url = f"{API_URL}/configuration/{agent_id}"
    header = { "Content-type": "application/vnd.api+json" }
    return orchestrator.get(url, headers=header)

def update_agent_config(agent_id, data):
    url = f"{API_URL}/configuration/{agent_id}"
    return orchestrator.put(url, body=data)

def get_session_status(session_id):
    url = f"{API_URL}/sessionstatus/{session_id}"
    return orchestrator.get(url)

def get_sessions_status(page=0, limit=10):
    #url = f"{API_URL}/sessionstatuses?page={page}&limit={limit}"
    url = f"{API_URL}/sessionstatuses"
    return orchestrator.get(url)

def print_sessions_status(raw: bool = False):
    response = get_sessions_status()
    if raw:
        utils.log_response(response)
        return
    sessions = response.json().get('data', [])
    print(f"{'Session Id':<{16}} {'Status':<{16}} Status Message")
    print(f"{'----------':<{16}} {'------':<{16}} --------------")
    if len(sessions) > 0:
        for session in sessions:
            print(f"{session.get('sessionId', 'n.a.'):<{16}} {session.get('status', 'n.a.'):<{16}} {session.get('statusMessage', 'n.a.')}")
    else:
        print("No sessions found.")
    print("\n")

def print_session_status(session_id):
    response = get_session_status(session_id)
    utils.log_response(response)

def print_sessions():
    response = get_sessions()
    utils.log_response(response)

def print_agents():
    response = get_agents()
    if not response.ok:
        utils.log_response(response)
        return
    agents = response.json().get('data', [])
    def _meta_sort_value(v):
        if isinstance(v, dict):
            return json.dumps(v, sort_keys=True)
        return "" if v is None else str(v)
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
    agents_info.sort(key=lambda a: ((a[2] or ""), _meta_sort_value(a[5])))
    col_widths = [
        max(4, max(len(str(agent[i])) for agent in agents_info)) for i in range(6)
    ]
    print(
        f"{utils.GREEN}"
        f"| {'id':<{col_widths[0]}} "
        f"| {'name':<{col_widths[1]}} "
        f"| {'type':<{col_widths[2]}} "
        f"| {'status':<{col_widths[3]}} "
        f"| {'state':<{col_widths[4]}} "
        f"| {'metadata':<{col_widths[5]}} |"
        f"{utils.RESET}"
    )
    for agent in agents_info:
        print(
            f"| {str(agent[0]):<{col_widths[0]}} "
            f"| {str(agent[1]):<{col_widths[1]}} "
            f"| {str(agent[2]):<{col_widths[2]}} "
            f"| {str(agent[3]):<{col_widths[3]}} "
            f"| {str(agent[4]):<{col_widths[4]}} "
            f"| {str(agent[5]):<{col_widths[5]}} |"
        )

def print_agent(agent_id):
    response = get_agent(agent_id)
    utils.log_response(response)

def print_agent_config(agent_id):
    response = get_agent_config(agent_id)
    utils.log_response(response)

def print_agents_config():
    response = get_agents()
    if not response.ok:
        utils.log_response(response)
        return
    agents = response.json().get('data', [])
    for data in agents:
        agent_id = data['id']
        response = get_agent_config(agent_id)
        utils.log_response(response)

def delete_sessions(prefix):
    response = get_sessions()
    if not response.ok:
        utils.log_response(response)
        return
    data = response.json().get('data', [])
    sessions = [session.get('attributes', {}).get('session', {}).get('sessionId') for session in data]
    sessions_to_delete = [ session_id for session_id in sessions if prefix == "all" or session_id.startswith(prefix) ]
    if len(sessions_to_delete) > 0:
        print("Found sessions: ", ", ".join(sessions_to_delete))
        for session_id in sessions_to_delete:
            print("> Deleting session", session_id, "...")
            response = delete_session(session_id)
            if not response.ok:
                utils.log_response(response)
                return
    else:
        print("No sessions found")

class CustomFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    def __init__(self, prog, indent_increment=1, max_help_position=None, width=None):
        if max_help_position is None:
            max_help_position = 30 # You can adjust this value as needed
        super().__init__(prog, indent_increment, max_help_position, width)

def build_parser():
    parser = argparse.ArgumentParser(
        description=f"CLI for Sensor Agent API: {orchestrator.get_url_info()}",
        formatter_class=CustomFormatter
    )
    subparsers = parser.add_subparsers(
        #dest="command", 
        #help='Available commands.',
        title="This is the title", 
        #metavar="<command>"
    )
    add_commands(subparsers)
    return parser

def add_commands(subparsers):

    sp = subparsers.add_parser("get", help=f"GET method using {orchestrator.get_url()}")
    sp.add_argument("uri")
    sp.set_defaults(func=lambda a: send_request("GET", f"{orchestrator.get_url()}/{a.uri}"))

    sp = subparsers.add_parser("post", help=f"POST method {orchestrator.get_url()}")
    sp.add_argument("uri")
    sp.set_defaults(func=lambda a: send_request("POST", f"{orchestrator.get_url()}/{a.uri}"))

    sp = subparsers.add_parser("put", help=f"PUT method {orchestrator.get_url()}")
    sp.add_argument("uri")
    sp.set_defaults(func=lambda a: send_request("PUT", f"{orchestrator.get_url()}/{a.uri}"))

    sp = subparsers.add_parser("patch", help=f"PATCH method {orchestrator.get_url()}")
    sp.add_argument("uri")
    sp.set_defaults(func=lambda a: send_request("PATCH", f"{orchestrator.get_url()}/{a.uri}"))

    sp = subparsers.add_parser("delete",help=f"DELETE method {orchestrator.get_url()}")
    sp.add_argument("uri")
    sp.set_defaults(func=lambda a: send_request("DELETE", f"{orchestrator.get_url()}/{a.uri}"))

    # Convenience domain-specific helpers
    sp = subparsers.add_parser("get_sessions",help=f"GET all sessions.")
    sp.set_defaults(func=lambda a: print_sessions())

    sp = subparsers.add_parser("get_sessions_status",help=f"GET all sessions status.")
    sp.set_defaults(func=lambda a: print_sessions_status())

    sp = subparsers.add_parser("get_session_status",help=f"GET session status.")
    sp.add_argument("session_name")
    sp.set_defaults(func=lambda a: print_session_status(a.session_name))

    sp = subparsers.add_parser("delete_sessions",help=f"DELETE all sessions starting with the specified prefix.")
    sp.add_argument("prefix")
    sp.set_defaults(func=lambda a: delete_sessions(a.prefix))

    sp = subparsers.add_parser("get_agents",help=f"GET all agents.")
    sp.set_defaults(func=lambda a: print_agents())

    sp = subparsers.add_parser("get_agent",help=f"GET a specific agent.")
    sp.add_argument("id")
    sp.set_defaults(func=lambda a: print_agent(a.id))

    sp = subparsers.add_parser("get_agents_config",help=f"GET all agents configuration.")
    sp.set_defaults(func=lambda a: print_agents_config())

    sp = subparsers.add_parser("get_agent_config",help=f"GET a specific agent's configuration.")
    sp.add_argument("id")
    sp.set_defaults(func=lambda a: print_agent_config(a.id))

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