from __future__ import absolute_import, division, print_function
import unittest
from plugins.modules.server_settings import RudderSettingsInterface
from parameterized import parameterized
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type


class TestParameterMethods(unittest.TestCase):
    module = AnsibleModule(
        argument_spec={
            'rudder_url': {'required': False},
            'validate_certs': {'required': False},
        }
    )
    iface = RudderSettingsInterface(module)

    def test_url_parameter_overload(self):
        value = iface._value_to_test(value='url')
        self.assertIsNotNone(value)

    def test_validate_certs_parameter_overload(self):
        value = iface._value_to_test(value='validate_certs')
        self.assertIsNotNone(value)


if __name__ == '__main__':
    unittest.main()
