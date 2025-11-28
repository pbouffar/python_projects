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
from config import analytics as orchestrator

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def send_request(method, url, body=None):
    resp = orchestrator.send_request(method, url, body)
    #utils.log_response(resp)
    return resp

def get_alerting_policy_with_tag(tag):
    url = f"/api/v2/policies/alerting?tag={tag}"
    response = orchestrator.get(url)
    #utils.log_response(response)
    return response

def print_alerting_policy_with_tag(tag):
    utils.log_response(get_alerting_policy_with_tag(tag))

def get_alerting_policies():
    url = f"/api/v2/policies/alerting"
    response = orchestrator.get(url)
    #utils.log_response(response)
    return response

def print_alerting_policies():
    utils.log_response(get_alerting_policies())

def delete_alerting_policy_v2(policy_id):
    url = f"/api/v2/policies/alerting/{policy_id}"
    response = orchestrator.delete(url)
    utils.log_response(response)
    return response

def delete_alerting_policy_v3(policy_id, ignore_alerts=True):
    url = f"/api/v3/policies/alerting/{policy_id}"
    params = {'ignoreAlerts': str(ignore_alerts).lower()}
    response = orchestrator.delete(url, params=params)
    utils.log_response(response)
    return response

#
# MACRO COMMANDS.
#
def delete_all_policies():
    # GET
    get_resp = get_alerting_policies()
    print("GET /api/v2/policies/alerting:", get_resp.status_code, get_resp.json())
    policy_ids = [policy['id'] for policy in get_resp.json().get('data', [])]
    print("Policies ID: ", policy_ids)

    for policy_id in policy_ids:
        del_resp_v2 = delete_alerting_policy_v2(policy_id)
        print(f"DELETE /api/v2/policies/alerting/{policy_id}:", del_resp_v2.status_code, del_resp_v2.text)
        del_resp_v3 = delete_alerting_policy_v3(policy_id, ignore_alerts=True)
        print(f"DELETE /api/v3/policies/alerting/{policy_id}?ignoreAlerts=true:", del_resp_v3.status_code, del_resp_v3.text)

#
# Monitored Objects APIs
#
def create_monitored_object(data):
    url = f"/api/v2/monitored-objects"
    response = send_request("POST", url, body=data)
    return response

def update_monitored_object(object_id, data):
    url = f"/api/v2/monitored-objects/{object_id}"
    response = send_request("PATCH", url, body=data)
    return response

def delete_monitored_object(object_id):
    url = f"/api/v2/monitored-objects/{object_id}"
    response = send_request("DELETE", url)
    return response

def get_monitored_object(object_id):
    url = f"/api/v2/monitored-objects/{object_id}"
    response = send_request("GET", url)
    utils.log_response(response)
    return response

def get_monitored_objects():
    url = f"/api/v2/monitored-objects"
    response = send_request("GET", url)
    utils.log_response(response)
    return response

def get_monitored_object_ids_with_name(data):
    url = f"/api/v2/monitored-objects/id-list"
    response = send_request("POST", url, body=data)
    return response

#
# Metadata Mapping APIs
#
def update_metadata_mapping(data):
    url = f"/api/v2/metadata-category-mappings/activeMetrics"
    response = send_request("PATCH", url, body=data)
    return response

def get_metadata_mapping():
    url = f"/api/v2/metadata-category-mappings/activeMetrics"
    response = send_request("GET", url)
    utils.log_response(response)
    return response

def get_all_tenant_metadata():
    """
    Function used to fetch the all tenant metadata
    """
    url = f"/api/v2/tenant-metadata"
    response = send_request("GET", url)
    return response

def get_tenant_metadata(tenant_id):
    """
    Function used to fetch the all tenant metadata
    """
    url = f"/api/v2/tenant-metadata/{tenant_id}"
    response = orchestrator.get(url)
    utils.log_response(response)
    return response

def print_tenant_metadata(tenant_id):
    response = get_tenant_metadata(tenant_id)
    utils.log_response(response)

def update_tenant_metadata(tenant_id, data):
    url = f"/api/v2/tenant-metadata/{tenant_id}"
    response = orchestrator.patch(url, body=data)
    if not response.ok:
        utils.log_response(response)
    return response

def set_tenant_metadata_storeMetadataValueCaseSensitive_to_true():
    resp = get_tenant_metadata(orchestrator.get_tenant_id())
    if not resp.ok:
        utils.log_response(resp)
        return
    metadata = json.loads(resp.content)
    store_metadata_value_case_sensitive = metadata.get('data', {}).get('attributes', {}).get('storeMetadataValueCaseSensitive')
    if store_metadata_value_case_sensitive is None or store_metadata_value_case_sensitive is False:
        metadata['data']['attributes']['storeMetadataValueCaseSensitive'] = True
        resp = update_tenant_metadata(orchestrator.get_tenant_id(), metadata)
        if resp.ok:
            print(f"Successfully patched value of {utils.BOLD}storeMetadataValueCaseSensitive{utils.RESET} to true.")
        else:
            utils.log_response(resp)
    else:
        print(f"Value of {utils.BOLD}storeMetadataValueCaseSensitive{utils.RESET} is already {'true' if store_metadata_value_case_sensitive else 'false'}.")

def get_metadata_categories():
    url = f"/api/v2/metadata-category-mappings/activeMetrics"
    response = send_request("GET", url)
    return response

def verify_metadata_categories():
    resp = get_metadata_categories()
    data = json.loads(resp.content).get('data', {}).get('attributes', {}).get('metadataCategoryMap')
    expected = ["service_id", "ne_id_sender", "service_name", "ne_id_reflector"]
    if data:
        found = []
        for key in data.keys():
            is_active = data[key].get('isActive')
            if is_active:
                found.append(data[key].get('name'))
        print(f"Found these metadata category: \n- {"\n- ".join(found)}\n")
        not_found = [x for x in expected if x not in found]
        if len(not_found) > 0:
            print(f"{utils.YELLOW}FAIL!{utils.RESET} Missing the following metadata category: \n- {"\n- ".join(not_found)}")
        else:
            print(f"{utils.GREEN}PASS!{utils.RESET} All expected metadata categories exist.")
    else:
        print("No data.")

def get_ingestion_profiles():
    url = f"/api/v2/ingestion-profiles"
    response = send_request("GET", url)
    return response

expected_twampsf_metrics = ["delayAvg", "delayMax", "delayMin", "delayP25", "delayP50", "delayP75", "delayP95",
    "delayPHi", "delayPLo", "delayPMi", "delayStdDevAvg", "delayVarAvg", "delayVarMax", "delayVarMin", "delayVarP25",
    "delayVarP50", "delayVarP75", "delayVarP95", "delayVarPHi", "delayVarPLo", "delayVarPMi", "duration",
    "fCongestion", "jitterAvg", "jitterMax", "jitterP95", "jitterPHi", "jitterPLo", "jitterPMi", "jitterStdDev",
    "lostBurstMax", "packetsLost", "packetsLostPct", "packetsReceived", "periodsLost", "syncQuality", "syncState"
]

def verify_twampsf_metrics():
    resp = get_ingestion_profiles()
    data = json.loads(resp.content).get('data',[])
    if len(data) > 0:
        """
        for item in data:
            metrics = item.get('attributes', {}).get('metricList', [])
            if len(metrics) > 0:
                for metric in metrics:
                    if metric.get('monitoredObjectType') == "twamp-sf":
                        print(f"{metric.get('metric')}: {metric.get('enabled')}")
        """
        found = []
        for item in data:
            metrics = item.get('attributes', {}).get('metrics', {}).get('vendorMap', {})
            if len(metrics.keys()) > 0:
                for key in metrics:
                    if key == "accedian-twamp":
                        metricMap = metrics[key].get('monitoredObjectTypeMap', {}).get('twamp-sf', {}).get('metricMap', {})
                        for key in metricMap:
                            if metricMap[key] is True:
                                found.append(key)
        not_found = [x for x in expected_twampsf_metrics if x not in found]
        if len(not_found) > 0:
            print(f"{utils.YELLOW}FAIL!{utils.RESET} The following metrics are not enabled: \n- {"\n- ".join(not_found)}")
        else:
            print(f"{utils.GREEN}PASS!{utils.RESET} All expected metrics are enabled.")
    else:
        print("No data.")


def get_monitored_object_stitchit(session_id):
    """
    Function used to fetch the all tenant metadata
    """
    url = f"/api/v1/stitchit/monitoredObjects?objectId={session_id}"
    response = send_request("GET", url)
    #utils.log_response(response)
    return response

class CustomFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

def build_parser():
    parser = argparse.ArgumentParser(
        description=f"CLI for Analytics REST API: {orchestrator.get_url_info()}",
        formatter_class=CustomFormatter
    )
    subparsers = parser.add_subparsers(dest="command", title="Commands", metavar="<command>")
    add_commands(subparsers)
    return parser

def add_commands(subparsers):

    """
    sp = subparsers.add_parser("get", help=f"GET method using {orchestrator.get_url()}")
    sp.add_argument("uri")
    sp.set_defaults(func=lambda a: send_request("GET", f"/{a.uri}"))

    sp = subparsers.add_parser("post", help=f"POST method {orchestrator.get_url()}")
    sp.add_argument("uri")
    sp.set_defaults(func=lambda a: send_request("POST", f"/{a.uri}"))

    sp = subparsers.add_parser("put", help=f"PUT method {orchestrator.get_url()}")
    sp.add_argument("uri")
    sp.set_defaults(func=lambda a: send_request("PUT", f"/{a.uri}"))

    sp = subparsers.add_parser("patch", help=f"PATCH method {orchestrator.get_url()}")
    sp.add_argument("uri")
    sp.set_defaults(func=lambda a: send_request("PATCH", f"/{a.uri}"))

    sp = subparsers.add_parser("delete",help=f"DELETE method {orchestrator.get_url()}")
    sp.add_argument("uri")
    sp.set_defaults(func=lambda a: send_request("DELETE", f"/{a.uri}"))
    """

    # Convenience domain-specific helpers
    sp = subparsers.add_parser("get_monitored_object",help="GET monitored object")
    sp.add_argument("id")
    sp.set_defaults(func=lambda a: get_monitored_object(a.id))

    sp = subparsers.add_parser("get_monitored_objects",help="GET all monitored objects")
    sp.set_defaults(func=lambda a: get_monitored_objects())

    sp = subparsers.add_parser("get_metadata_mapping",help="GET metadata mapping")
    sp.set_defaults(func=lambda a: get_metadata_mapping())

    sp = subparsers.add_parser("get_tenant_metadata",help="GET tenant metadata")
    sp.set_defaults(func=lambda a: print_tenant_metadata(orchestrator.get_tenant_id()))

    sp = subparsers.add_parser("update_tenant_metadata",help="PATCH tenant metadata")
    sp.add_argument("patched_data_filename")
    sp.set_defaults(func=lambda a: update_tenant_metadata(orchestrator.get_tenant_id(), a.patched_data_filename))

    sp = subparsers.add_parser("patch_storeMetadataValueCaseSensitive",help="PATCH tenant metadata storeMetadataValueCaseSensitive attribute to true.")
    sp.set_defaults(func=lambda a: set_tenant_metadata_storeMetadataValueCaseSensitive_to_true())

    sp = subparsers.add_parser("delete_all_policies",help="DELETE all policies")
    sp.set_defaults(func=lambda a: delete_all_policies())

    sp = subparsers.add_parser("get_alerting_policy",help="GET a specific alerting policy by tag")
    sp.add_argument("tag")
    sp.set_defaults(func=lambda a: print_alerting_policy_with_tag(a.tag))

    sp = subparsers.add_parser("get_alerting_policies",help="GET all alerting policies")
    sp.set_defaults(func=lambda a: print_alerting_policies())

    sp = subparsers.add_parser("verify_metadata_categories",help="Verify required metadata categories exists.")
    sp.set_defaults(func=lambda a: verify_metadata_categories())

    sp = subparsers.add_parser("verify_twampsf_metrics",help="Verify required TWAMP-SF metrics are enabled.")
    sp.set_defaults(func=lambda a: verify_twampsf_metrics())


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
