#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2021, Normation
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (
    absolute_import,
    division,
    print_function
)
from ansible.module_utils.basic import AnsibleModule
import json

# import logging

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

# {{{ for debug (remove this)
# logging.basicConfig(
#     filename="/var/log/rudder/ansible/ansible_debug.log",  # tail -f -n0 /var/log/rudder/ansible/ansible_debug.log
#     format='[%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S]',
#     encoding='utf-8',
#     level=logging.DEBUG
# )
# }}}

# Disable SSL certificat warning messages
requests.packages.urllib3.disable_warnings(
    InsecureRequestWarning
    )

DOCUMENTATION = '''
---
module: rudder_node_settings
author:
  - Normation
version_added: '2.9'
short_description: Configure Rudder Nodes 6.2 parameters via APIs
requirements:
    - 'python >= 2.7'

options:

  rudder_url:
    description:
      - Providing Rudder server IP address. Defaults to localhost of the target node if not set, with certificate validation disabled, unless explicitly enabled by setting validate_certs.
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
    required: true
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
    
'''

EXAMPLES = r'''
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
'''

class RudderNodeSettingsInterface(object):
    def __init__(self, module):
        self._module = module
        self.headers = {
            "Content-Type": "application/json"
        }
        self.validate_certs = True
        # Get local API Token (when is not specified)
        if module.params.get('rudder_token', None):
            self.headers = {
                "X-API-Token": module.params['rudder_token'],
                "Content-Type": "application/json"
            }
            # logging.info(self.headers)  # for debug (remove this)
        else:
            with open('/var/rudder/run/api-token') as f:
                token = f.read()
            self.headers = {
                "X-API-Token": token,
                "Content-Type": "application/json"
            }
        if module.params.get('rudder_url', None):
            self.rudder_url = module.params['rudder_url']
            # logging.info(self.rudder_url)  # for debug (remove this)
        else:
            self.rudder_url = "https://localhost/rudder"
            self.validate_certs = False
        if module.params.get('validate_certs', None):
            self.validate_certs = module.params['validate_certs']

        self.node_id = module.params['node_id']

        if module.params.get('policy_mode', None):
            self.policy_mode = module.params['policy_mode']
            
        if module.params.get('state', None):
            self.state = module.params['state']
            
        if module.params.get('pending', None):
            self.pending = module.params['pending']
            
        if module.params.get('properties', None):
            self.properties_name = module.params['properties']['name']
            self.properties_value = module.params['properties']['value']
            
        if module.params.get('agent_key', None):
            self.agent_key_value = module.params['agent_key']['value']
            self.agent_key_status = module.params['agent_key']['status']
            

    def _send_request(self, path: str, data=None, serialize_json=None, headers=None, method="GET") -> str:
        """Send HTTP request

        Args:
            path (str): Specify the API path (for example: "/rudder/api/latest/nodes/{nodeId}") .
            data (str): Specify all JSON datas (for example: "{'policyMode':'audit'}").
            serialize_json (bool): Specify if you want to serialize obj into a JSON formatted string.
            headers (str, optional): Specify HTTP headers. Defaults to None.
            method (str, optional): Specify HTTP method (GET or POST only). Defaults to "GET".

        Returns:
            str: return request content as an object.
        """
        
        # Serialise obj into a str formatted as JSON or not
        s_data = json.dumps(data) if serialize_json is not None else data 
        
        if not headers:
            headers = []

        full_url = "{rudder_url}{path}".format(
            rudder_url=self.rudder_url,
            path=path
        )

        if method == "POST":
            resp = requests.post(
                url=full_url,
                headers=self.headers,
                data=s_data,
                verify=False
            )
            
        elif method == "GET":
            resp = requests.get(
                url=full_url,
                headers=self.headers,
                verify=False
            )
        else:
            self._module.fail_json(
                failed=True,
                msg="Method not supported by the function '_send_request'!"
            )

        status_code = resp.status_code
        if status_code == 404:
            return None
        elif status_code == 401:
            self._module.fail_json(
                failed=True,
                msg="Unauthorized to perform action '{}' on '{}'".format(
                    method,
                    full_url
                )
            )
        elif status_code == 403:
            self._module.fail_json(
                failed=True,
                msg="Permission Denied"
            )
        elif status_code == 200:
            return self._module.from_json(
                resp.content
                )
        else:
            self._module.fail_json(
                failed=True,
                msg="Rudder API answered with HTTP {} details: {} ".format(
                    status_code,
                    resp.content
                )
            )

    def set_NodeSettingValue(self, node_id: str, cfg_type: str) -> str:
        """Function to define a setting or properties via the API

        Args:
            node_id (str): ID of the Rudder node to configure 
            data (str): Data in JSON format to be sent, see here: 'https://docs.rudder.io/api/v/13/#operation/nodeDetails'
            cfg_type (str): Setting type (state, policyMode)

        Returns:
            str: Returns the result of the query
        """
        url = "/api/latest/nodes/{node_id}".format(
            node_id=self.node_id
        )
        
        if cfg_type == "policy_mode":
            data = {
                "policyMode": self.policy_mode
            }
            
            return self._send_request(
                path=url,
                data=data,
                headers=self.headers,
                serialize_json=False,
                method="POST"
            )
        elif cfg_type == "state":
            data = {
                "state": self.state
            }
            
            return self._send_request(
                path=url,
                data=data,
                headers=self.headers,
                serialize_json=False,
                method="POST"
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
                method="POST"
            )
        
        elif cfg_type == "agent_key_with_value":
            data = {
                "agentKey":[
                    {
                        "value": self.agent_key_value,
                        "status": self.agent_key_status
                    }
                ]
            }
            
            return self._send_request(
                path=url,
                data=data,
                headers=self.headers,
                serialize_json=False,
                method="POST"
            )
            
        elif cfg_type == "properties":
            data = {
                "properties":[
                    {
                        "name":self.properties_name, 
                        "value":self.properties_value
                        }
                    ]
                }
            
            return self._send_request(
                path=url,
                data=data,
                headers=self.headers,
                serialize_json=True,
                method="POST"
            )
        else:
            module.fail_json(
                failed=True,
                msg=f"Unsupported cfg type: '{cfg_type}'"
            )

    def set_NodePendingValue(self, node_id: str) -> str:
        """Function to define pending status for a specific node via the API

        Args:
            node_id (str): ID of the Rudder node (in pending nodes)

        Returns:
            str: Return the result of the query
        """
        url = "/api/latest/nodes/pending/{node_id}".format(
            node_id=self.node_id
        ) 
        
        data = {
            'status': self.pending
        }
        
        return self._send_request(
            path=url,
            data=data,
            headers=self.headers,
            serialize_json=False,
            method="POST"
            )

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
                required=True,
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
                choices=[
                    "accepted",
                    "refused"
                ],
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
        ),
        supports_check_mode=False
    )

    rudder_url = module.params['rudder_url']
    rudder_token = module.params['rudder_token']
    rudder_node_id = module.params['node_id']
    rudder_validate_certs = module.params['validate_certs']
    rudder_properties = module.params['properties']
    rudder_policy_mode = module.params['policy_mode']
    rudder_state = module.params['state']
    rudder_pending = module.params['pending']
    rudder_agent_key = module.params['agent_key']

    rudder_node_iface = RudderNodeSettingsInterface(module)

    if not HAS_REQUESTS:
        module.fail_json(
            msg="The Python 'requests' module is required!"
        )

    if rudder_policy_mode is not None and rudder_policy_mode != "keep":
        # logging.debug(f"Send policy mode: '{rudder_policy_mode}' for {rudder_node_id}!")
        try:
            rudder_node_iface.set_NodeSettingValue(
                node_id=rudder_node_id,
                cfg_type="policy_mode"
            )
        except:
            module.fail_json(
                msg=f"Error during 'policy_mode' configuration for node ID: {rudder_node_id}"
            )
    if rudder_state is not None:
        # logging.debug(f"Send node lifecycle state: '{rudder_state}' for {rudder_node_id}!")
        try:
            rudder_node_iface.set_NodeSettingValue(
                node_id=rudder_node_id,
                cfg_type="state"
            )
        except:
            module.fail_json(
                msg=f"Error during the configuration of the state (lifecycle) for node ID: {rudder_node_id}"
            )
    if rudder_pending is not None:
        # logging.debug(f"Send pending status: '{rudder_pending}' for {rudder_node_id}!")
        try:
            rudder_node_iface.set_NodePendingValue(
                node_id=rudder_node_id
                ) 
        except:
            module.fail_json(
                msg=f"Error during node status configuration for: {rudder_node_id}"
            )

    if rudder_properties is not None:
        try:
            rudder_node_iface.set_NodeSettingValue(
                node_id=rudder_node_id, 
                cfg_type="properties"
                )
        except:
            module.fail_json(
                msg=f"Error during definition of nodes properties for: {rudder_node_id}"
            )      
            
    if rudder_agent_key is not None:
        try:
            if module.params['agent_key']['value'] is None:
                rudder_node_iface.set_NodeSettingValue(
                    node_id=rudder_node_id, 
                    cfg_type="agent_key_without_value"
                    )    
            else:
                rudder_node_iface.set_NodeSettingValue(
                    node_id=rudder_node_id, 
                    cfg_type="agent_key_with_value"
                    )     
        except:
            module.fail_json(
                msg=f"Error during agentKey configuration for: {rudder_node_id}"
            )               
      

    module.exit_json( 
        failed=False,
        changed=True,
        meta=module.params, # for debug (remove this)
    )
    
if __name__ == "__main__":
    main()
