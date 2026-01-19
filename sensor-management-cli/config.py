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
from rep import get_tenant_info


_TENANT_URL="https://10.250.1.192" # UCS, Dev1 (Replicated)
#_TENANT_URL="https://dev1.cisco-nso.agentslab.analytics.accedian.io" # Cloud, Dev1 (Swarm)
#_TENANT_URL="https://10.10.0.235" # CNC, Walther (Replicated)

# Get tenant info to retrieve tenant ID.
tenant_info = get_tenant_info(_TENANT_URL)

_TENANT_ID = tenant_info["tenantId"]
_TENANT_ID_WALTHER = "7476c54c-889b-4f21-b0cd-432cf622067e"

_USER_ROLES = "system,skylight-admin,tenant-admin,ug_all_data_access"


_AGENT_CONFIG_WALTHER = OrchestratorConfig(
    name="Agent-Orchestrate",
    url=_TENANT_URL,
    port="10015",
    replicated=True,
    tenant_id=_TENANT_ID_WALTHER,
    user_roles=_USER_ROLES
)

_AGENT_CONFIG_CLOUD_DEV0 = OrchestratorConfig(
    name="Agent-Orchestrate",
    url=_TENANT_URL,
    port="",
    replicated=False,
    username="admin@datahub.com",
    password="3PKT9fhZ#33ed",
    login_api="/api/v1/auth/login",
    logout_api="/api/v1/auth/logout"
)

_AGENT_CONFIG_UCS_DEV1 = OrchestratorConfig(
    name="Agent-Orchestrate",
    url=_TENANT_URL,
    port="10015",
    replicated=True,
    tenant_id=_TENANT_ID,
    user_roles=_USER_ROLES
)

_ANALYTICS_CONFIG_CLOUD_DEV0 = OrchestratorConfig(
    name="Analytics",
    url=_TENANT_URL,
    port="",
    replicated=False,
    tenant_id=_TENANT_ID,
    username="admin@datahub.com",
    password="3PKT9fhZ#33ed",
    login_api="/api/v1/auth/login",
    logout_api="/api/v1/auth/logout"
)

_ANALYTICS_CONFIG_UCS_DEV1 = OrchestratorConfig(
    name="Analytics",
    url=_TENANT_URL,
    port="10001",
    replicated=True,
    tenant_id=_TENANT_ID,
    user_roles=_USER_ROLES
)

_SO_CONFIG_CLOUD_DEV0 = OrchestratorConfig(
    name="Sensor-Orchestrator",
    url="https://10.250.4.254",
    port="9081",
    replicated=False,
    username="admin",
    password="2admin$admin",
    login_api=["/nbapi/login", "/nbapiemswsweb/login"]
)

_SO_CONFIG_UCS_DEV1 = OrchestratorConfig(
    name="Sensor-Orchestrator",
    url=_TENANT_URL,
    port="9081",
    replicated=True,
    tenant_id=_TENANT_ID,
    user_roles=_USER_ROLES
)

_YGW_CONFIG_CLOUD_DEV0 = OrchestratorConfig(
    name="Yang-Gateway",
    url="http://localhost",
    port="8444",
    replicated=False
)

_YGW_CONFIG_UCS_DEV1 = OrchestratorConfig(
    name="Yang-Gateway",
    url="http://localhost",
    port="8444",
    replicated=True
)

_AGENT_CONFIG = _AGENT_CONFIG_UCS_DEV1
_ANALYTICS_CONFIG = _ANALYTICS_CONFIG_UCS_DEV1
_SO_CONFIG = _SO_CONFIG_UCS_DEV1
_YGW_CONFIG = _YGW_CONFIG_UCS_DEV1

agent = Orchestrator(_AGENT_CONFIG)
analytics = Orchestrator(_ANALYTICS_CONFIG)
so = Orchestrator(_SO_CONFIG)
ygw = Orchestrator(_YGW_CONFIG)
