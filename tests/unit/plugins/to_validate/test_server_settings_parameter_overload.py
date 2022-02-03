from __future__ import absolute_import, division, print_function
import unittest
from plugins.modules.server_settings import RudderSettingsInterface
from parameterized import parameterized
from ansible.module_utils import basic

__metaclass__ = type


class TestParameterMethods(unittest.TestCase):
    module = basic.AnsibleModule(
        argument_spec=dict(
            rudder_url=dict(type='str', required=False, default='test'),
            validate_certs=dict(type='str', required=False, default='test'),
        )
    )

    rudder_url = module.params['rudder_url']
    validate_certs = module.params['validate_certs']

    interface = RudderSettingsInterface(module)

    def test_url_parameter_overload(self):
        value = interface._value_to_test(value='url')
        self.assertIsNotNone(value)

    def test_validate_certs_parameter_overload(self):
        value = interface._value_to_test(value='validate_certs')
        self.assertIsNotNone(value)


if __name__ == '__main__':
    unittest.main()
