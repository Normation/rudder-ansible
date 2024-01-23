#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, Rudder
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

DOCUMENTATION = """
---
module: server_settings
author: Rudder (@Normation)
version_added: '1.0.0'
short_description: Configure Rudder Server parameters via APIs.
description:
    - Configure Rudder Server parameters via APIs.
requirements:
    - 'python >= 2.7'

options:
  rudder_url:
    description:
      - Providing Rudder server IP address. Defaults to localhost.
    required: false
    default: https://localhost/rudder
    type: str

  rudder_token:
    description:
      - Providing Rudder server token. Defaults to the content of /var/rudder/run/api-token if not set.
    type: str

  name:
    description:
      - The name of the parameter to set.
    required: true
    type: str

  value:
    description:
      - The value defined to modify a given parameter name.
    required: true
    type: raw

  validate_certs:
    description:
      - Choosing either to ignore or not Rudder certificate validation. Defaults to true.
    type: bool
    default: yes

"""

EXAMPLES = r"""
- name: Simple Modify Rudder Settings
  server_settings:
      name: "modified_file_ttl"
      value: "23"

- name: Complex Modify Rudder Settings
  server_settings:
      rudder_url: "https://my.rudder.server/rudder"
      rudder_token: "<rudder_server_token>"
      name: "modified_file_ttl"
      value: "22"
      validate_certs: False
"""

import json
import traceback
from urllib.error import HTTPError

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import basic_auth_header, fetch_url, open_url
from ansible.module_utils.common.text.converters import to_native

__metaclass__ = type

# Ansible module parameters
allParams = ['rudder_url', 'rudder_token', 'name', 'value', 'validate_certs']


class RudderSettingsInterface(object):
    def __init__(self, module):
        self._module = module
        self.validate_certs = True
        self.variables = {
            'raw_value': [],
            'requests': []
        }

        self.rudder_url = module.params['rudder_url']
        self.validate_certs = module.params['validate_certs']

        if module.params.get('rudder_token', None) is None:
            try:
                with open('/var/rudder/run/api-token') as system_token:
                    token = system_token.read()
            except Exception as e:
                self.fail(
                    msg="No token found in parameters, could not find the default system token under '/var/rudder/run/api-token'.",
                    exception=str(e)
                )
        else:
            token = module.params['rudder_token']
        self.headers = {
            'X-API-Token': token,
            'Content-Type': 'application/json',
        }

    def _value_to_test(self, value):
        """Function for unit test to test value overload

        Args:
            value (str): parameter type
        """
        if value == 'url':
            return self.rudder_url
        elif value == 'validate_certs':
            return self.validate_certs

    def fail(self, msg, exception):
        self._module.fail_json(
            changed=False,
            failed=True,
            msg=msg,
            exception=exception,
            variables=self.variables
        )

    def success(self, msg, changed):
        self._module.exit_json(
            failed=False,
            changed=changed,
            message=msg,
            variables=self.variables
        )

    def _send_request(self, url, data=None, headers=None, method='GET'):
        if not headers:
            headers = []
        printable_headers = headers.copy()
        if 'X-API-Token' in printable_headers:
            printable_headers.update({'X-API-Token': '*****'})

        full_url = '{rudder_url}{path}'.format(
            rudder_url=self.rudder_url, path=url
        )
        self.variables['requests'].append({
            'req': {
                'url': full_url,
                'headers': printable_headers,
                'method': method,
                'validate_certs': self.validate_certs,
                'data': data
            },
            'resp': {}
        })
        try:
            r = open_url(
                full_url,
                headers=headers,
                validate_certs=self.validate_certs,
                method=method,
                data=json.dumps(data, sort_keys=True)
            ).read().decode('utf-8')
            resp = json.loads(r)
            self.variables['requests'][-1]['resp'] = resp
            return resp
        except HTTPError as e:
            self.variables['requests'][-1]['resp'] = self._module.from_json(e.read().decode('utf-8'))
            self.fail(exception=None, msg="The API call returned an unexpected HTTP error code: {code}".format(code=e.code))
        except Exception as e:
            self.fail(
                msg='Rudder API call failed',
                exception=str(e)
            )

    def compare_settings_value(self, left, right):
        if isinstance(left, list):
            return sorted(left) == sorted(right)
        elif isinstance(left, str) or isinstance(left, bool) or isinstance(left, int):
            return left == right
        else:
            self.fail(
                msg='Unsupported settings value type: {v_type}'.format(v_type=str(type(left))),
                exception=None
            )

    def log_variable(self, name, value):
        self.variables[name] = value

    def get_SettingValue(self, name):
        try:
            url = '/api/latest/settings/{name}'.format(name=name)
            raw_value = self._send_request(url, headers=self.headers, method='GET')
            self.log_variable('raw_value', raw_value)
            if 'allowed_networks' in name:
                return raw_value['data']['allowed_networks']
            else:
                return raw_value['data']['settings'][name]
        except Exception as e:
            self.fail(
                msg="Could not read settings value from the API",
                exception=str(e)
            )

    def set_SettingValue(self, name, value):
        self._send_request(
            url='/api/latest/settings/{name}'.format(name=name),
            headers=self.headers,
            method='POST',
            data={'allowed_networks': value} if 'allowed_networks' in name else {'value': value}
        )


def main():
    module = AnsibleModule(
        argument_spec={
            'rudder_url': {
                'type': 'str',
                'required': False,
                'default': 'https://localhost/rudder',
            },
            'rudder_token': {'type': 'str', 'required': False},
            'name': {'type': 'str', 'required': True},
            'value': {'type': 'raw', 'required': True},
            'validate_certs': {'type': 'bool', 'default': True},
        },
        supports_check_mode=False,
    )

    rudder_url = module.params['rudder_url']
    rudder_token = module.params['rudder_token']
    name = module.params['name']
    value = module.params['value']
    if isinstance(value, str):
        try:
            value = module.from_json(module.params['value'])
        except:
            value = value

    rudder_server_iface = RudderSettingsInterface(module)

    OLD_VALUE = rudder_server_iface.get_SettingValue(name)
    rudder_server_iface.log_variable('old_value', OLD_VALUE)

    # For common settings
    if rudder_server_iface.compare_settings_value(value, OLD_VALUE):
        rudder_server_iface.success(
            changed=False,
            msg='Already correct'
        )

    rudder_server_iface.set_SettingValue(name, value)
    NEW_VALUE = rudder_server_iface.get_SettingValue(name)
    rudder_server_iface.log_variable('new_value', NEW_VALUE)

    if rudder_server_iface.compare_settings_value(value, NEW_VALUE):
        rudder_server_iface.success(
            changed=True,
            msg='Settings successfully updated'
        )
    else:
        rudder_server_iface.fail(
            msg='Could not apply the expected settings',
            exception=None
        )


if __name__ == '__main__':
    main()
