#  Copyright (c) 2025 Cisco Systems, Inc.
#  All rights reserved.
#
#  This code is provided under the terms of the Cisco Software License Agreement.
#  Unauthorized copying, modification, or distribution is strictly prohibited.
#
#  Cisco Systems,Inc.
#  170 West Tasman Drive,San Jose,CA 95134,USA
import json
import requests
import urllib3
#from dataclasses import dataclass
#from typing import Optional

# Define color and style codes
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
BG_CYAN = "\033[46m"

def print_error(msg):
    print(f"{RED}ERROR{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}WARNING{RESET} {msg}")

def log_response(response):
    req_body = None
    if response.request.body is not None and response.request.body:
        try:
            js = json.loads(response.request.body)
            req_body = json.dumps(js, indent=4)
        except Exception as e:
            req_body = str(response.request.body)

    resp_body = None
    if response.content is not None and response.content:
        try:
            resp_body = json.dumps(response.json(), indent=4)
        except Exception as e:
            resp_body = response.text
    elif response.text is not None and response.text:
        resp_body = response.text

    result = f"{RED}ERROR{RESET}" if not response.ok else f"{GREEN}SUCCESS{RESET}"
    print(
        f"{result}: {response.status_code} {response.request.method} {response.request.url}\n"
        f"   {UNDERLINE}REQUEST{RESET} : {req_body}\n"
        f"   {UNDERLINE}RESPONSE{RESET}: {resp_body}"
    )




