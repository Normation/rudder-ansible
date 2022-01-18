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
    type: str

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

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import basic_auth_header, fetch_url

__metaclass__ = type

# Ansible module parameters
allParams = ['rudder_url', 'rudder_token', 'name', 'value', 'validate_certs']


class RudderSettingsInterface(object):
    def __init__(self, module):
        self._module = module
        self.validate_certs = True

        self.rudder_url = module.params['rudder_url']
        self.validate_certs = module.params['validate_certs']

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

    def _send_request(self, url, data=None, headers=None, method='GET'):
        if data is not None:
            data = json.dumps(data, sort_keys=True)

        if not headers:
            headers = []

        full_url = '{rudder_url}{path}'.format(
            rudder_url=self.rudder_url, path=url
        )

        resp, info = fetch_url(
            self._module, full_url, data=data, headers=headers, method=method
        )

        status_code = info['status']
        if status_code == 404:
            self._module.fail_json(failed=True, msg='Not found')
        elif status_code == 401:
            self._module.fail_json(
                failed=True,
                msg="Unauthorized to perform action '{}' on '{}'".format(
                    method, full_url
                ),
            )
        elif status_code == 200:
            return self._module.from_json(resp.read())
        else:
            self._module.fail_json(
                failed=True,
                msg='Rudder API answered with HTTP {} details: {} '.format(
                    status_code, info['msg']
                ),
            )

    def get_SettingValue(self, name):
        url = '/api/latest/settings/{name}'.format(name=name)
        response = self._send_request(url, headers=self.headers, method='GET')
        return response['data']['settings'][name]

    def set_SettingValue(self, name, value):
        url = '/api/latest/settings/{name}'.format(name=name)
        current_server_settings = self.get_SettingValue(name)
        data = value

        update = False

        if (current_server_settings != self.get_SettingValue(name)):
            update = True

        if update:
            self._send_request(
                url, headers=self.headers, method='POST', data=data
            )


def main():
    module = AnsibleModule(
        argument_spec={
            'rudder_url': {'type': 'str', 'required': False, 'default': 'https://localhost/rudder'},
            'rudder_token': {'type': 'str', 'required': False},
            'name': {'type': 'str', 'required': True},
            'value': {'type': 'str', 'required': True},
            'validate_certs': {'type': 'bool', 'default': True},
        },
        supports_check_mode=False,
    )

    rudder_url = module.params['rudder_url']
    rudder_token = module.params['rudder_token']
    name = module.params['name']
    value = module.params['value']
    validate_certs = module.params['validate_certs']

    rudder_server_iface = RudderSettingsInterface(module)

    VALUE = rudder_server_iface.get_SettingValue(name)

    changed = False

    if str(VALUE) != value:
        rudder_server_iface.set_SettingValue(name, value)
        changed = True
        module.exit_json(
            failed=False,
            changed=changed,
            meta=module.params,
            new_value=str(VALUE),
            message='changed succefully',
        )
    else:
        rudder_server_iface.get_SettingValue(name)
        changed = False
        module.exit_json(
            failed=False,
            changed=False,
            meta=module.params,
            message='Already exist',
        )


if __name__ == '__main__':
    main()
