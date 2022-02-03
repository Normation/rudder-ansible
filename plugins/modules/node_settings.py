#!/usr/bin/python
# Copyright: (c) 2022, Rudder <dev@rudder.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

DOCUMENTATION = r"""
module: node_settings
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

  status:
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
    default: default

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
        type: list
        description: The criterion you want to find for your nodes.
        elements: dict
        suboptions:
          object_type:
            description: Object type from which the attribute will be taken.
            type: str
          attribute:
            description: Attribute to compare to value.
            type: str
          comparator:
            description: Comparator type to use.
            type: str
          value:
            type: str
            description: Value to compare to.
"""

EXAMPLES = r"""
- name: Simple Modify Rudder Node Settings
  node_settings:
      rudder_url: "https://my.rudder.server/rudder"
      node_id: my_node_id
      policy_mode: enforce
- name: Complex Modify Rudder Node Settings
  node_settings:
      rudder_url: "https://my.rudder.server/rudder"
      rudder_token: "<rudder_server_token>"
      node_id: root
      status: accepted
      policy_mode: audit
      state: enabled
      properties:
        name: "env_type"
        value: "production"
      validate_certs: False
- name: Complex Modify Rudder Node Settings with query
  node_settings:
      rudder_url: "https://my.rudder.server/rudder"
      rudder_token: "<rudder_server_token>"
      status: accepted
      policy_mode: audit
      state: enabled
      properties:
        name: "env_type"
        value: "production"
      query:
        select: "nodeAndPolicyServer"
        composition: "and"
        where:
          - object_type: "node"
            attribute: "nodeHostname"
            comparator: "regex"
            value: "rudder-ansible-node.*"
"""

import json
import requests
from ansible.module_utils.urls import open_url, fetch_url
from ansible.module_utils.basic import AnsibleModule


__metaclass__ = type

# API available settings for the nodes
nodeSettingsParams = [
    'state',
    'properties',
    'agent_key',
    'policy_mode',
    'status',
]

# Ansible module parameters
allParams = [
    'rudder_url',
    'rudder_token',
    'node_id',
    'include',
    'query',
    'validate_certs',
] + nodeSettingsParams


def json_query_to_url_query(json_query):
    """
    Expects an array of the form:
      [
          {
              "object_type": "node",
              "attribute": "OS",
              "comparator": "eq",
              "value": "Linux"
          },
          {
              "object_type": "node",
              "attribute": "osFullName",
              "comparator": "regex",
              "value": ".*Linux.*"
          },
          {
              "object_type": "memoryPhysicalElement",
              "attribute": "quantity",
              "comparator": "gteq",
              "value": "1"
          }
       ]
    """
    queries = []
    for i in json_query:
        query_struct = {
            'objectType': i['object_type'],
            'attribute': i['attribute'],
            'comparator': i['comparator'],
            'value': i['value'],
        }
        queries.append(query_struct)
    return 'where={dump}'.format(
        dump=json.dumps(queries, separators=(',', ':'))
    )


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
            try:
                with open('/var/rudder/run/api-token') as system_token:
                    token = system_token.read()
            except FileNotFoundError:
                self._module.fail_json(
                    failed=True,
                    msg="No token found in parameters, could not find the default system token under '/var/rudder/run/api-token'.",
                )
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

    def _value_to_test(self, value):
        """Function for unit test to test value overload

        Args:
            value (str): parameter type
        """
        if value == 'url':
            return self.rudder_url
        elif value == 'validate_certs':
            return self.validate_certs

    def _send_request(self, path, data=None, headers=None, method='GET'):
        """Send HTTP request

        Args:
            url (str): API path
            data (str): Specify all JSON data (for example: "{'policyMode':'audit'}").
            headers (str, optional): Specify HTTP headers. Defaults to None.
            method (str, optional): Specify HTTP method (GET or POST only). Defaults to "GET".

        Returns:
            str: return request content as a json object.
        """

        if data is not None:
            data = json.dumps(data, sort_keys=True)

        if not headers:
            headers = []

        full_url = '{rudder_url}{path}'.format(
            rudder_url=self.rudder_url, path=path
        )

        try:
            resp = (
                open_url(
                    full_url,
                    headers=headers,
                    validate_certs=self.validate_certs,
                    method=method,
                    data=data,
                )
                .read()
                .decode('utf8')
            )
            return self._module.from_json(resp)
        except Exception as error:
            self._module.fail_json(
                failed=True, msg='Rudder API call failed!', reason=str(error)
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
                method='POST',
            )
        return update

    def evaluate_node_query(self):
        """Get all nodes (with query)

        Returns:
            str: All nodes who match with query
        """

        query = self._module.params['query']

        query_json_struct = {
            'select': query['select'],
            'composition': query['composition'],
        }

        url_query = '?' + json_query_to_url_query(query['where'])

        nodes = self._send_request(
            method='GET',
            path='/api/latest/nodes' + url_query,
            data={},
            headers=self.headers,
        )['data']['nodes']
        nodes_id = [node['id'] for node in nodes]

        return (url_query, nodes_id)


def main():
    # Definition of the arguments and options
    # of the 'node_settings' module
    where_object = dict(
        object_type=dict(type='str', required=False),
        attribute=dict(type='str', required=False),
        comparator=dict(
            type='str',
            required=False,
        ),
        value=dict(type='str', required=False),
    )
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
            status=dict(
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
            include=dict(type='str', required=False, default='default'),
            query=dict(
                type='dict',
                required=False,
                options=dict(
                    select=dict(type='str', required=False),
                    composition=dict(
                        type='str', required=False, choices=['or', 'and']
                    ),
                    where=dict(
                        type='list',
                        required=False,
                        elements='dict',
                        options=where_object,
                    ),
                ),
            ),
        ),
        supports_check_mode=False,
    )

    rudder_node_iface = RudderNodeSettingsInterface(module)

    # Define the target nodes
    query = ''
    target_nodes = []
    if module.params.get('node_id', None) is not None:
        target_nodes.append(module.params['node_id'])
    else:
        (query, target_nodes) = rudder_node_iface.evaluate_node_query()

    changed = False
    impacted_nodes = {i: False for i in target_nodes}
    errors = []
    for node_id in target_nodes:
        try:
            node_changed = rudder_node_iface.set_node_settings(node_id)
            changed = node_changed or changed
            impacted_nodes[node_id] = node_changed
        except Exception as err:
            errors.append(err)

    failed = bool(errors)
    module.exit_json(
        failed=failed,
        changed=changed,
        meta=module.params,
        audited_settings=rudder_node_iface.settings_to_set,
        nodes=impacted_nodes,
        query=query,
        errors=errors,
    )


if __name__ == '__main__':
    main()
