#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2021, Rudder
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

import json

from ansible.module_utils.basic import AnsibleModule

# Check if 'requests' is installed
# Use : 'pip3 install requests' if not
try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
except ImportError:
    HAS_REQUESTS = False
else:
    HAS_REQUESTS = True

__metaclass__ = type

# Disable SSL certificate warning messages
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

DOCUMENTATION = """
---
module: rudder_node_settings
author:
  - Rudder
version_added: '2.9'
short_description: Configure Rudder Nodes parameters via APIs
requirements:
    - 'python >= 2.7'

options:

  rudder_url:
    description:
      - Providing Rudder server IP address. Defaults to localhost.
    required: false
    type: str

  rudder_token:
    description:
      - Providing Rudder server token. Defaults to the content of /var/rudder/run/api-token if not set.
    required: false
    type: str

  validate_certs:
    description:
      - Choosing either to ignore or not Rudder certificate validation. Defaults to true.
    required: false
    type: boolean

  node_id:
    description:
      - Define the identifier of the node to be configured
    required: false
    type: str

  policy_mode:
    description:
      - Set the policy mode to (default, enforce or audit)
    required: false
    type: str

  state:
    description:
      - Set the node life cycle state to (enabled, ignored, empty-policies, initializing or preparing-eol)
    required: false
    type: str

  properties:
    description:
      - Define a properties (with "name:" and "value:")
    required: false
    type: dict

  agent_key:
    description:
      - Define information about agent key or certificate (update PEM with ("value:<PEM>") and status with "status:<certified|undefined>")
    required: false
    type: dict

  include:
    description:
      - Level of information to include from the node inventory.
    required: false
    type: str

  query:
    description:
      - The criterion you want to find for your nodes.
    required: false
    type: dict

"""

EXAMPLES = r"""
  - name: Simple Modify Rudder Node Settings
    rudder_node_settings:
        rudder_url: "https://my.rudder.server/rudder"
        node_id: my_node_id
        policy_mode: enforce

  - name: Complex Modify Rudder Node Settings
    rudder_node_settings:
        rudder_url: "https://my.rudder.server/rudder"
        rudder_token: "<rudder_server_token>"
        node_id: root
        pending: accepted
        policy_mode: audit
        state: enabled
        properties:
          name: "env_type"
          value: "production"
        validate_certs: False

  - name: Complex Modify Rudder Node Settings with query
    rudder_node_settings:
        rudder_url: "https://my.rudder.server/rudder"
        rudder_token: "<rudder_server_token>"
        pending: accepted
        policy_mode: audit
        state: enabled
        properties:
          name: "env_type"
          value: "production"
        query:
          select: "nodeAndPolicyServer"
          composition: "and"
          where:
            object_type: "node"
            attribute: "nodeHostname"
            comparator: "regex"
            value: "rudder-ansible-node.*"
"""


class RudderNodeSettingsInterface(object):
    def __init__(self, module):
        self._module = module
        self.headers = {"Content-Type": "application/json"}
        self.validate_certs = True
        self.rudder_url = "https://localhost/rudder"

        # Get local API Token (when is not specified)
        if module.params.get("rudder_token", None):
            self.headers = {
                "X-API-Token": module.params["rudder_token"],
                "Content-Type": "application/json",
            }
        else:
            with open("/var/rudder/run/api-token") as f:
                token = f.read()
            self.headers = {
                "X-API-Token": token,
                "Content-Type": "application/json",
            }
        if module.params.get("rudder_url", None):
            self.rudder_url = module.params["rudder_url"]
        else:
            self.validate_certs = False

        if module.params.get("validate_certs", None):
            self.validate_certs = module.params["validate_certs"]

        self.node_id = module.params["node_id"]

        if module.params.get("policy_mode", None):
            self.policy_mode = module.params["policy_mode"]

        if module.params.get("state", None):
            self.state = module.params["state"]

        if module.params.get("pending", None):
            self.pending = module.params["pending"]

        if module.params.get("properties", None):
            self.properties_name = module.params["properties"]["name"]
            self.properties_value = module.params["properties"]["value"]

        if module.params.get("agent_key", None):
            self.agent_key_value = module.params["agent_key"]["value"]
            self.agent_key_status = module.params["agent_key"]["status"]

        if module.params.get("include", None):
            self.include = module.params["include"]

        if module.params.get("query", None):
            self.query_select = module.params["query"]["select"]
            self.query_composition = module.params["query"]["composition"]
            self.where_object_type = module.params["query"]["where"][
                "object_type"
            ]
            self.where_attribute = module.params["query"]["where"]["attribute"]
            self.where_comparator = module.params["query"]["where"][
                "comparator"
            ]
            self.where_value = module.params["query"]["where"]["value"]

    def _send_request(
        self,
        path,
        data=None,
        serialize_json=None,
        headers=None,
        method="GET",
        verify=False,
        params=None,
    ):
        """Send HTTP request

        Args:
            path (str): Specify the API path (for example: "/rudder/api/latest/nodes/{nodeId}") .
            data (str): Specify all JSON data (for example: "{'policyMode':'audit'}").
            serialize_json (bool): Specify if you want to serialize obj into a JSON formatted string.
            headers (str, optional): Specify HTTP headers. Defaults to None.
            method (str, optional): Specify HTTP method (GET or POST only). Defaults to "GET".
            verify (bool, optional): Specify if you want to check SSL certificate
            params (str, optional): Specify all params

        Returns:
            str: return request content as an object.
        """

        # Serialise obj into a str formatted as JSON or not
        s_data = json.dumps(data) if serialize_json is not None else data

        if not headers:
            headers = []

        full_url = "{rudder_url}{path}".format(
            rudder_url=self.rudder_url, path=path
        )

        if method == "POST":
            resp = requests.post(
                url=full_url,
                headers=self.headers,
                params=params,
                data=s_data,
                verify=verify,
            )

        elif method == "GET":
            resp = requests.get(
                url=full_url,
                params=params,
                headers=self.headers,
                verify=verify,
            )
        else:
            self._module.fail_json(
                failed=True,
                msg="Method not supported by the function '_send_request'!",
            )

        status_code = resp.status_code
        if status_code == 404:
            return None
        elif status_code == 401:
            self._module.fail_json(
                failed=True,
                msg="Unauthorized to perform action '{}' on '{}'".format(
                    method, full_url
                ),
            )
        elif status_code == 403:
            self._module.fail_json(failed=True, msg="Permission Denied")
        elif status_code == 200:
            return self._module.from_json(resp.content)
        else:
            self._module.fail_json(
                failed=True,
                msg="Rudder API answered with HTTP {} details: {} ".format(
                    status_code, resp.content
                ),
            )

    def set_NodeSettingValue(self, node_id, cfg_type):
        """Function to define a setting or properties via the API

        Args:
            node_id (str): ID of the Rudder node to configure
            data (str): Data in JSON format to be sent, see here: 'https://docs.rudder.io/api/v/13/#operation/nodeDetails'
            cfg_type (str): Setting type (state, policyMode)

        Returns:
            str: Returns the result of the query
        """
        url = "/api/latest/nodes/{node_id}".format(node_id=self.node_id)

        if cfg_type == "policy_mode":
            data = {"policyMode": self.policy_mode}

            return self._send_request(
                path=url,
                data=data,
                headers=self.headers,
                serialize_json=False,
                method="POST",
            )
        elif cfg_type == "state":
            data = {"state": self.state}

            return self._send_request(
                path=url,
                data=data,
                headers=self.headers,
                serialize_json=False,
                method="POST",
            )
        elif cfg_type == "agent_key_without_value":
            data = {
                "agentKey": {
                    "status": self.agent_key_status,
                }
            }

            return self._send_request(
                path=url,
                data=data,
                headers=self.headers,
                serialize_json=True,
                method="POST",
            )

        elif cfg_type == "agent_key_with_value":
            data = {
                "agentKey": [
                    {
                        "value": self.agent_key_value,
                        "status": self.agent_key_status,
                    }
                ]
            }

            return self._send_request(
                path=url,
                data=data,
                headers=self.headers,
                serialize_json=False,
                method="POST",
            )

        elif cfg_type == "properties":
            data = {
                "properties": [
                    {
                        "name": self.properties_name,
                        "value": self.properties_value,
                    }
                ]
            }

            return self._send_request(
                path=url,
                data=data,
                headers=self.headers,
                serialize_json=True,
                method="POST",
            )

        else:
            module.fail_json(
                failed=True, msg=f"Unsupported cfg type: '{cfg_type}'"
            )

    def set_NodePendingValue(self, node_id):
        """Function to define pending status for a specific node via the API

        Args:
            node_id (str): ID of the Rudder node (in pending nodes)

        Returns:
            str: Return the result of the query
        """
        url = "/api/latest/nodes/pending/{node_id}".format(
            node_id=self.node_id
        )

        data = {"status": self.pending}

        return self._send_request(
            path=url,
            data=data,
            headers=self.headers,
            serialize_json=False,
            method="POST",
        )

    def get_QueryNodesValue(self):
        """Get all nodes (with query)

        Returns:
            str: All nodes who match with query
        """

        url = "/api/latest/nodes"

        query_json_struct = {
            "select": self.query_select,
            "composition": self.query_composition,
        }

        where_json_struct = {
            "objectType": self.where_object_type,
            "attribute": self.where_attribute,
            "comparator": self.where_comparator,
            "value": self.where_value,
        }

        params = {
            "where": json.dumps(where_json_struct),
            "query": json.dumps(query_json_struct),
            "include": self.include,
        }

        response = self._send_request(
            path=url,
            headers=self.headers,
            serialize_json=False,
            params=params,
            method="GET",
        )

        list_id = []

        for value in response["data"]["nodes"]:
            list_id.append(value["id"])

        return list_id


def main():
    # Definition of the arguments and options
    # of the 'rudder_node_settings' module
    module = AnsibleModule(
        argument_spec=dict(
            rudder_url=dict(
                type="str",
                required=True,
            ),
            rudder_token=dict(
                type="str",
                required=False,
            ),
            node_id=dict(
                type="str",
                required=False,
            ),
            properties=dict(
                type="dict",
                required=False,
                options=dict(
                    name=dict(
                        type="str",
                        required=True,
                    ),
                    value=dict(
                        type="str",
                        required=True,
                    ),
                ),
            ),
            agent_key=dict(
                type="dict",
                required=False,
                options=dict(
                    value=dict(
                        required=False,
                        type="str",
                    ),
                    status=dict(
                        type="str",
                        required=True,
                        choices=[
                            "certified",
                            "undefined",
                        ],
                    ),
                ),
            ),
            pending=dict(
                type="str",
                required=False,
                choices=["accepted", "refused"],
            ),
            state=dict(
                type="str",
                choices=[
                    "enabled",
                    "ignored",
                    "empty-policies",
                    "initializing",
                    "preparing-eol",
                ],
                required=False,
            ),
            validate_certs=dict(
                type="bool",
                required=False,
            ),
            policy_mode=dict(
                type="str",
                choices=[
                    "audit",
                    "enforce",
                    "default",
                    "keep",
                ],
                required=False,
            ),
            include=dict(
                type="str",
                required=False,
            ),
            query=dict(
                type="dict",
                required=False,
                select=dict(
                    type="str",
                    required=False,
                ),
                composition=dict(
                    type="str",
                    required=False,
                ),
                where=dict(
                    type="dict",
                    required=False,
                    object_type=dict(
                        type="str",
                        required=False,
                    ),
                    attribute=dict(
                        type="str",
                        required=False,
                    ),
                    comparator=dict(
                        type="str",
                        choices=[
                            "and",
                            "or",
                        ],
                        required=False,
                    ),
                    value=dict(
                        type="str",
                        required=False,
                    ),
                ),
            ),
        ),
        supports_check_mode=False,
    )

    rudder_node_id = module.params["node_id"]
    rudder_properties = module.params["properties"]
    rudder_policy_mode = module.params["policy_mode"]
    rudder_state = module.params["state"]
    rudder_pending = module.params["pending"]
    rudder_agent_key = module.params["agent_key"]

    rudder_node_iface = RudderNodeSettingsInterface(module)

    if not HAS_REQUESTS:
        module.fail_json(msg="The Python 'requests' module is required!")

    # Init list
    all_rudder_node_id = []

    if rudder_node_id is not None:
        all_rudder_node_id.append(rudder_node_id)
    else:
        for item in rudder_node_iface.get_QueryNodesValue():
            all_rudder_node_id.append(item)

    for node_id in all_rudder_node_id:
        try:
            if rudder_policy_mode is not None and rudder_policy_mode != "keep":
                rudder_node_iface.set_NodeSettingValue(
                    node_id=node_id, cfg_type="policy_mode"
                )
            if rudder_state is not None:
                rudder_node_iface.set_NodeSettingValue(
                    node_id=node_id, cfg_type="state"
                )
            if rudder_pending is not None:
                rudder_node_iface.set_NodePendingValue(node_id=node_id)

            if rudder_properties is not None:
                rudder_node_iface.set_NodeSettingValue(
                    node_id=node_id, cfg_type="properties"
                )

            if rudder_agent_key is not None:
                if module.params["agent_key"]["value"] is None:
                    rudder_node_iface.set_NodeSettingValue(
                        node_id=node_id, cfg_type="agent_key_without_value"
                    )
                else:
                    rudder_node_iface.set_NodeSettingValue(
                        node_id=node_id, cfg_type="agent_key_with_value"
                    )
        except requests.exceptions.RequestException as err:
            module.fail_json(msg=err)

    module.exit_json(
        failed=False,
        changed=True,
        meta=module.params,
    )


if __name__ == "__main__":
    main()