"""
  Copyright (c) 2025 Cisco Systems, Inc.
  All rights reserved.

  This code is provided under the terms of the Cisco Software License Agreement.
  Unauthorized copying, modification, or distribution is strictly prohibited.

  Cisco Systems,Inc.
  170 West Tasman Drive,San Jose,CA 95134,USA
"""

from orchestrator_config import OrchestratorConfig
from orchestrator import Orchestrator

_TENANT_ID = "94f4456d-d5d4-48f4-a5c6-69d8d2e48ced"
_USER_ROLES = "system,skylight-admin,tenant-admin"


def get_tenant_id():
    return _TENANT_ID


def get_user_roles():
    return _USER_ROLES


_AGENT_CONFIG_DEV0 = OrchestratorConfig(
    name="Agent-Orchestrate",
    url="https://dev1.cisco-nso.agentslab.analytics.accedian.io",
    port="",
    replicated=False,
    username="admin@datahub.com",
    password="3PKT9fhZ#33ed",
    login_api="/api/v1/auth/login",
    logout_api="/api/v1/auth/logout"
)

_AGENT_CONFIG_DEV1 = OrchestratorConfig(
    name="Agent-Orchestrate",
    url="https://10.250.1.192",
    port="10015",
    replicated=True,
    tenant_id=_TENANT_ID,
    user_roles=_USER_ROLES
)

_ANALYTICS_CONFIG_DEV0 = OrchestratorConfig(
    name="Analytics",
    url="https://dev1.cisco-nso.agentslab.analytics.accedian.io",
    port="",
    replicated=False,
    username="admin@datahub.com",
    password="3PKT9fhZ#33ed",
    login_api="/api/v1/auth/login",
    logout_api="/api/v1/auth/logout"
)

_ANALYTICS_CONFIG_DEV1 = OrchestratorConfig(
    name="Analytics",
    url="https://10.250.1.192",
    port="10001",
    replicated=True,
    tenant_id=_TENANT_ID,
    user_roles=_USER_ROLES
)

_SO_CONFIG_DEV0 = OrchestratorConfig(
    name="Sensor-Orchestrator",
    url="https://10.250.4.254",
    port="9081",
    replicated=False,
    username="admin",
    password="2admin$admin",
    login_api=["/nbapi/login", "/nbapiemswsweb/login"]
)

_SO_CONFIG_DEV1 = OrchestratorConfig(
    name="Sensor-Orchestrator",
    url="https://10.250.1.192",
    port="9081",
    replicated=True,
    tenant_id=_TENANT_ID,
    user_roles=_USER_ROLES
)

_YGW_CONFIG_DEV0 = OrchestratorConfig(
    name="Yang-Gateway",
    url="http://localhost",
    port="8444",
    replicated=False
)

_YGW_CONFIG_DEV1 = OrchestratorConfig(
    name="Yang-Gateway",
    url="http://localhost",
    port="8444",
    replicated=True
)

_AGENT_CONFIG = _AGENT_CONFIG_DEV1
_ANALYTICS_CONFIG = _ANALYTICS_CONFIG_DEV1
_SO_CONFIG = _SO_CONFIG_DEV1
_YGW_CONFIG = _YGW_CONFIG_DEV1

agent = Orchestrator(_AGENT_CONFIG)
analytics = Orchestrator(_ANALYTICS_CONFIG)
so = Orchestrator(_SO_CONFIG)
ygw = Orchestrator(_YGW_CONFIG)
