"""
  Copyright (c) 2025 Cisco Systems, Inc.
  All rights reserved.

  This code is provided under the terms of the Cisco Software License Agreement.
  Unauthorized copying, modification, or distribution is strictly prohibited.

  Cisco Systems,Inc.
  170 West Tasman Drive,San Jose,CA 95134,USA
"""

import requests

import utils
from orchestrator_config import OrchestratorConfig


class Orchestrator:

    token: list[dict] = []

    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.config.url = self.config.url + ":" + str(self.config.port)

    def __str__(self):
        return str(self.config)

    def get_url_info(self):
        return self.config.get_url_info()

    def _login(self, login_api, username, password):
        auth_url = self.config.url + login_api
        auth = {"username": username, "password": password}
        r = requests.post(auth_url, verify=False, data=auth)
        try:
            token = r.headers["Authorization"]
            self.token.append({"login_api": login_api, "token": token})
        except KeyError:
            self.token.append({"login_api": login_api, "cookies": r.cookies})
        return r.ok

    def _logout(self, logout_api, token):
        auth_url = self.config.url + logout_api
        r = requests.post(
            auth_url,
            verify=False,
            headers={
                "Authorization": token,
                "Content-type": "application/vnd.api+json",
            },
        )
        return r.ok

    def login(self):
        if self.config.replicated:
            return None
        if self._is_auth_token():
            return None
        if not self.config.login_api:
            return None
        if self.config.username is None or self.config.password is None:
            utils.print_warning(f"username and/or password may be required to use the {self.config.name} API.")

        # Login to all APIs.
        if isinstance(self.config.login_api, list):
            for login_api in self.config.login_api:
                self._login(login_api, self.config.username, self.config.password)
        else:
            self._login(self.config.login_api, self.config.username, self.config.password)
        # print(self.token)
        return len(self.token) > 0

    def logout(self):
        if self.config.replicated:
            return None
        # Logout of all APIs.
        if self.config.logout_api and self._is_auth_token():
            if isinstance(self.config.logout_api, list):
                for logout_api in self.config.logout_api:
                    self._logout(logout_api, self._get_auth_token(logout_api))
            else:
                self._logout(self.config.logout_api, self._get_auth_token(self.config.logout_api))
        return None

    def get_url(self):
        return self.config.url

    def get_tenant_id(self):
        return self.config.tenant_id

    def get_user_roles(self):
        return self.config.user_roles

    def _get_auth_token(self, uri):
        if len(self.token) > 1:
            for t in self.token:
                if t.get("login_api").split('/')[1] == uri.split('/')[1]:
                    return t.get("token")
        if len(self.token) > 0:
            return self.token[0].get("token")
        return None

    def _get_auth_cookies(self, uri):
        if len(self.token) > 1:
            for t in self.token:
                if t.get("login_api").split('/')[1] == uri.split('/')[1]:
                    return t.get("cookies")
        if len(self.token) > 1:
            return self.token[0].get("cookies")
        return None

    def _is_auth_token(self):
        return len(self.token) > 0

    def build_http_headers(self, uri, extra_headers=None):
        headers = {'Accept': 'application/json'}
        if self.config.replicated:
            headers["X-Forwarded-Tenant-Id"] = self.config.tenant_id
            headers["X-Forwarded-User-Roles"] = self.config.user_roles
        if self._is_auth_token():
            headers["Authorization"] = self._get_auth_token(uri)
        # else:
        #    raise Exception("token is required")
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def is_replicated(self):
        return self.config.replicated

    def send_request(self, method, uri, headers=None, params=None, body=None):
        url = self.config.url + uri
        resp = requests.request(method, url, headers=self.build_http_headers(uri, headers),
                                cookies=self._get_auth_cookies(uri), params=params,
                                json=body, verify=False)
        # utils.log_response(resp)
        return resp

    def get(self, uri, headers=None, params=None, body=None):
        return self.send_request("GET", uri, headers, params, body)

    def post(self, uri, headers=None, params=None, body=None):
        return self.send_request("POST", uri, headers, params, body)

    def put(self, uri, headers=None, params=None, body=None):
        return self.send_request("PUT", uri, headers, params, body)

    def patch(self, uri, headers=None, params=None, body=None):
        return self.send_request("PATCH", uri, headers, params, body=body)

    def delete(self, uri, headers=None, params=None, body=None):
        return self.send_request("DELETE", uri, headers, params, body)
