#  Copyright (c) 2025 Cisco Systems, Inc.
#  All rights reserved.
#
#  This code is provided under the terms of the Cisco Software License Agreement.
#  Unauthorized copying, modification, or distribution is strictly prohibited.
#
#  Cisco Systems,Inc.
#  170 West Tasman Drive,San Jose,CA 95134,USA

from dataclasses import dataclass
from typing import Optional

@dataclass
class OrchestratorConfig:
    name: str
    url: str
    port: str
    replicated: bool
    username: Optional[str] = None
    password: Optional[str] = None
    login_api: Optional[str] | Optional[list] = None
    logout_api: Optional[str] = None
    tenant_id: Optional[str] = None
    user_roles: Optional[str] = None

    def __str__(self):
        output = f"  name: {self.name}\n" \
            f"  url: {self.url}\n" \
            f"  port: {self.port}\n" \
            f"  replicated: {self.replicated}\n"

        if self.replicated:
            output += f"  tenant_id: {self.tenant_id}\n" \
                f"  user_roles: {self.user_roles}\n"
        else:
            output += f"  username: {self.username}\n" \
                f"  password: {'***' if self.password else None}\n" \
                f"  login_api: {self.login_api}\n" \
                f"  logout_api: {self.logout_api}\n"

    def get_url_info(self):
        output = f"{self.url}\n"
        return output
    
