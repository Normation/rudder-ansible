#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, Normation
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (
  absolute_import, 
  division, 
  print_function
)

DOCUMENTATION = '''
---
module: ruddersettings
author:
  - Normation
version_added: '2.9'
short_description: Configure Rudder Server 6.1 parameters via APIs
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
    required: false
    type: boolean

'''

''' EXAMPLE = '''

'''
- name: Simple Modify Rudder Settings
  rudder_settings:
      name: "modified_file_ttl"
      value: "23"

- name: Complex Modify Rudder Settings
  rudder_settings:
      rudder_url: "https://my.rudder.server/rudder"
      rudder_token: "<rudder_server_token>"
      name: "modified_file_ttl"
      value: "22"
      validate_certs: False
'''

import json
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import (
  fetch_url, 
  basic_auth_header
)
__metaclass__ = type

class RudderSettingsInterface(object):
    def __init__(self, module):
        self._module = module
        # {{{ Authentication header
        self.headers = {"Content-Type": "application/json"}
        self.validate_certs = True
        if module.params.get('rudder_token', None):
            self.headers = {"X-API-Token": module.params['rudder_token']}
        else:
            with open('/var/rudder/run/api-token') as f:
                token = f.read()
            self.headers = {"X-API-Token": token}
        # }}}
        if module.params.get('rudder_url', None):
            self.rudder_url = module.params.get("rudder_url")
        else:
            self.rudder_url = "https://localhost/rudder"
            self.validate_certs = False
        if module.params.get('validate_certs',None):
            self.validate_certs = module.params.get("validate_certs")

    def _send_request(self, url, data=None, headers=None, method="GET"):
        if data is not None:
            data = json.dumps(
              data, 
              sort_keys=True
              )
        if not headers:
            headers = []

        full_url = "{rudder_url}{path}".format(
          rudder_url=self.rudder_url, 
          path=url
          )
        resp, info = fetch_url(
          self._module, 
          full_url, 
          data=data, 
          headers=headers, 
          method=method
          )

        status_code = info["status"]
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
            return self._module.from_json(resp.read())
        else:
            self._module.fail_json(
              failed=True, 
              msg="Rudder API answered with HTTP {} details: {} ".format(
                status_code, 
                info['msg']
                )
              )

    def get_SettingValue(self, name):
        url = "/api/latest/settings/{name}".format(name=name)
        response = self._send_request(
          url, 
          headers=self.headers, 
          method="GET"
          )
        VALUE = response.get("data")
        return VALUE.get("settings").get(name)

    def set_SettingValue(self, name, value):
        url ="/api/latest/settings/{name}?value={value}".format(
          name=name, 
          value=value
          )
        
        return self._send_request(
          url, 
          headers=self.headers, 
          method="POST"
          )

def main():

    module_args = dict(
        name=dict(
          type='str', 
          required=True
          ),
        value=dict(required=True),
        rudder_url=dict(
          type='str', 
          required=True
          ),
        rudder_token=dict(
          type='str', 
          required=False
          ),
        validate_certs=dict(
          type='bool', 
          default=False
          ),

    )
    module = AnsibleModule(
        argument_spec={
        'rudder_url': {
          'type': 'str', 
          'required': True
          },
        'rudder_token': {
          'type': 'str', 
          'required': False
          },
        'name': {
          'type': 'str', 
          'required': True
          },
        'value': {
          'type': 'str', 
          'required': True
          },
        'validate_certs': {
          'type': 'bool', 
          'default': False
          },
        },
        supports_check_mode=False,
    )

    rudder_url = module.params['rudder_url']
    rudder_token = module.params['rudder_token']
    name = module.params['name']
    value = module.params['value']
    validate_certs = module.params['validate_certs']

    rudder_iface = RudderSettingsInterface(module)
    VALUE = rudder_iface.get_SettingValue(name)
    ''' module.exit_json(failed=False, changed=True, message=VALUE) '''

    if str(VALUE) != value:
        rudder_iface.set_SettingValue(
          name,
          value
          )
        changed = True
        module.exit_json(
          failed=False, 
          changed=changed, 
          message="changed succefully"
          )
    else:
        rudder_iface.get_SettingValue(name)
        module.exit_json(
          failed=False, 
          changed=True, 
          ok=True, 
          message="Already exist"
          )

if __name__ == '__main__':
    main()

