#!/usr/bin/python
# Copyright: (c) 2022, Rudder <dev@rudder.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

DOCUMENTATION = r"""
module: rudder_node_settings
short_description: Configure Rudder Nodes parameters via APIs
description:
    - Configure Rudder nodes parameters via APIs.
version_added: '1.0.0'
author: Rudder (@Normation)
requirements:
    - 'python >= 2.7'

options:
  rudder_url:
    description:
      - Providing Rudder server IP address. Defaults to localhost.
    type: str

  rudder_token:
    description:
      - Providing Rudder server token. Defaults to the content of /var/rudder/run/api-token if not set.
    type: str

  validate_certs:
    description:
      - Choosing either to ignore or not Rudder certificate validation. Defaults to true.
    type: bool
    default: yes

  node_id:
    description:
      - Define the identifier of the node to be configured
    type: str

  policy_mode:
    description:
      - Set the policy mode to (default, enforce or audit)
    type: str
    choices:
      - audit
      - enforce
      - default
      - keep

  pending:
    description:
      - Set the status of the (pending) node
    type: str
    choices:
      - accepted
      - refused

  state:
    description:
      - Set the node life cycle state to (enabled, ignored, empty-policies, initializing or preparing-eol)
    type: str
    choices:
      - enabled
      - ignored
      - empty-policies
      - initializing
      - preparing-eol

  properties:
    type: list
    elements: dict
    description:
      - Define a list of properties (with "name:" and "value:")
    suboptions:
      name:
        description: property name
        required: yes
        type: str
      value:
        description: property value
        required: yes
        type: str

  agent_key:
    description:
      - Define information about agent key or certificate
    type: dict
    suboptions:
      status:
        description: TODO
        required: yes
        choices:
          - certified
          - undefined
        type: str
      value:
        description: Agent key, PEM format
        type: str

  include:
    description:
      - Level of information to include from the node inventory.
    type: str

  query:
    description:
      - The criterion you want to find for your nodes.
    type: dict
    suboptions:
      composition:
        choices:
          - or
          - and
        type: str
        description: Boolean operator to use between each where criteria.
      select:
        description: What kind of data we want to include. Here we can get policy servers/relay by setting nodeAndPolicyServer. Only used if where is defined.
        type: str
      where:
        type: dict
        description: The criterion you want to find for your nodes.
        suboptions:
          object_type:
            description: Object type from which the attribute will be taken.
            type: str
          attribute:
            description: Attribute to compare to value.
            type: str
          comparator:
            description: Comparator type to use.
            choices:
              - and
              - or
            type: str
          value:
            type: str
            description: Value to compare to.
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

import json
import requests
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

# API available settings for the nodes
nodeSettingsParams = ['state', 'properties', 'agent_key', 'policy_mode']

# Ansible module parameters
allParams = [
    'rudder_url',
    'rudder_token',
    'node_id',
    'pending',
    'include',
    'query',
    'validate_certs',
] + nodeSettingsParams


class RudderNodeSettingsInterface(object):
    def __init__(self, module):
        self._module = module
        self.validate_certs = True
        for param in allParams:
            if param in module.params:
                setattr(self, param, module.params[param])

        if module.params.get('rudder_url', None) is None:
            self.rudder_url = 'https://localhost/rudder'
            self.validate_certs = False
        if module.params.get('rudder_token', None) is None:
            with open('/var/rudder/run/api-token') as system_token:
                token = system_token.read()
        else:
            token = module.params['rudder_token']
        self.headers = {
            'X-API-Token': token,
            'Content-Type': 'application/json',
        }

        raw_settings_to_set = {}
        for param in nodeSettingsParams:
            if param in module.params:
                raw_settings_to_set.update({param: module.params[param]})
        self.settings_to_set = self._translate_settings(raw_settings_to_set)

    def _send_request(
        self,
        path,
        data=None,
        serialize_json=None,
        headers=None,
        method='GET',
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

        full_url = '{rudder_url}{path}'.format(
            rudder_url=self.rudder_url, path=path
        )

        if method == 'POST':
            resp = requests.post(
                url=full_url,
                headers=self.headers,
                data=s_data,
                params=params,
                verify=verify,
            )

        elif method == 'GET':
            resp = requests.get(
                url=full_url,
                headers=self.headers,
                params=params,
                verify=verify,
            )
        else:
            self._module.fail_json(
                failed=True,
                msg="Method not supported by the function '_send_request'!",
            )

        status_code = resp.status_code
        if status_code == 200:
            return self._module.from_json(resp.content)
        else:
            self._module.fail_json(
                failed=True,
                msg='Rudder API answered with HTTP {} details: {} '.format(
                    status_code, resp.content
                ),
            )

    def _translate_settings(self, settings_dict):
        api_formatted_settings = {}
        for key, value in settings_dict.items():
            if key == 'policy_mode' and value is not None:
                api_formatted_settings.update({'policyMode': value})
            elif key == 'agent_key' and value is not None:
                key_data = {'status': value['status']}
                if 'value' in value:
                    key_data.update({'value': value['value']})
                api_formatted_settings.update({'agentKey': key_data})
            elif value is not None:
                api_formatted_settings.update({key: value})
        return api_formatted_settings

    def get_node_settings(self, node_id):
        return self._send_request(
            method='GET',
            path='/api/latest/nodes/{node_id}'.format(node_id=node_id),
            data={},
            headers=self.headers,
        )['data']['nodes'][0]

    def set_node_settings(self, node_id):
        current_node_settings = self.get_node_settings(node_id)
        update = False
        for i_settings in self.settings_to_set:
            if (
                current_node_settings[i_settings]
                != self.settings_to_set[i_settings]
            ):
                update = True
        if update:
            self._send_request(
                path='/api/latest/nodes/{node_id}'.format(node_id=node_id),
                data=self.settings_to_set,
                headers=self.headers,
                serialize_json=True,
                method='POST',
            )
        return update

    def evaluate_node_query(self):
        """Get all nodes (with query)

        Returns:
            str: All nodes who match with query
        """

        url = '/api/latest/nodes'

        query_json_struct = {
            'select': self.query_select,
            'composition': self.query_composition,
        }

        where_json_struct = {
            'objectType': self.where_object_type,
            'attribute': self.where_attribute,
            'comparator': self.where_comparator,
            'value': self.where_value,
        }

        params = {
            'where': json.dumps(where_json_struct),
            'query': json.dumps(query_json_struct),
            'include': self.include,
        }

        response = self._send_request(
            path=url,
            headers=self.headers,
            serialize_json=False,
            params=params,
            method='GET',
        )

        # Init list
        nodes_id = []
        for value in response['data']['nodes']:
            nodes_id.append(value['id'])
        return nodes_id


def main():
    # Definition of the arguments and options
    # of the 'rudder_node_settings' module
    module = AnsibleModule(
        argument_spec=dict(
            rudder_url=dict(type='str', required=False),
            rudder_token=dict(type='str', required=False),
            node_id=dict(type='str', required=False),
            properties=dict(
                type='list',
                required=False,
                elements='dict',
                options=dict(
                    name=dict(type='str', required=True),
                    value=dict(type='str', required=True),
                ),
            ),
            agent_key=dict(
                type='dict',
                required=False,
                options=dict(
                    value=dict(required=False, type='str'),
                    status=dict(
                        type='str',
                        required=True,
                        choices=['certified', 'undefined'],
                    ),
                ),
            ),
            pending=dict(
                type='str', required=False, choices=['accepted', 'refused']
            ),
            state=dict(
                type='str',
                choices=[
                    'enabled',
                    'ignored',
                    'empty-policies',
                    'initializing',
                    'preparing-eol',
                ],
                required=False,
            ),
            validate_certs=dict(type='bool', required=False, default=True),
            policy_mode=dict(
                type='str',
                choices=['audit', 'enforce', 'default', 'keep'],
                required=False,
            ),
            include=dict(type='str', required=False),
            query=dict(
                type='dict',
                required=False,
                options=dict(
                    select=dict(type='str', required=False),
                    composition=dict(
                        type='str', required=False, choices=['or', 'and']
                    ),
                    where=dict(
                        type='dict',
                        required=False,
                        options=dict(
                            object_type=dict(type='str', required=False),
                            attribute=dict(type='str', required=False),
                            comparator=dict(
                                type='str',
                                choices=['and', 'or'],
                                required=False,
                            ),
                            value=dict(type='str', required=False),
                        ),
                    ),
                ),
            ),
        ),
        supports_check_mode=False,
    )

    rudder_node_iface = RudderNodeSettingsInterface(module)

    # Define the target nodes
    target_nodes = []
    if 'node_id' in module.params:
        target_nodes.append(module.params['node_id'])
    elif 'query' not in module.params:
        module.fail_json(msg='No target node_id nor query found!')
    else:
        target_nodes = rudder_node_iface.evaluate_node_query()

    changed = False
    impacted_nodes = {i: False for i in target_nodes}
    for node_id in target_nodes:
        try:
            node_changed = rudder_node_iface.set_node_settings(node_id)
            changed = node_changed or changed
            impacted_nodes[node_id] = node_changed
        except Exception as exception:
            module.fail_json(msg=exception)

    module.exit_json(
        failed=False,
        changed=changed,
        meta=module.params,
        audited_settings=rudder_node_iface.settings_to_set,
        nodes=impacted_nodes,
    )


if __name__ == '__main__':
    main()
