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
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser(description="Fetch tenant info")
parser.add_argument("TENANT_IP", nargs="?", help="Tenant IP address", default="10.250.1.192")
parser.add_argument("--raw", "-r", action="store_true", help="Print raw JSON response")
args = parser.parse_args()

URL = f"https://{args.TENANT_IP}"
URI = "/api/v1/onboarding/tenant-info"


def get_tenant_info(url: str) -> dict:
    tenant_info = {}
    try:
        response = requests.get(url+URI, verify=False)
        data = response.json()
        tenant_info = {
            "tenantUrl": url,
            "tenantId": data["data"]["attributes"]["tenantId"],
            "tenantName": data["data"]["attributes"]["tenantName"]
        }
    except requests.exceptions.ConnectionError as e:
        tenant_info = {
            "error": "Connection error",
            "message": str(e)
        }
    return tenant_info    


if __name__ == "__main__":
    tenant_info = get_tenant_info(URL)
    if args.raw:
        print(json.dumps(tenant_info, indent=2))
    else:
        output_str = f"URL:        {tenant_info.get('tenantUrl')}\n" \
                    f"tenantId:   {tenant_info.get('tenantId')}\n" \
                    f"tenantName: {tenant_info.get('tenantName')}"
        print(output_str)
