from __future__ import absolute_import, division, print_function
import unittest
from plugins.modules import server_settings
from parameterized import parameterized

__metaclass__ = type


class TestStringMethods(unittest.TestCase):
    @parameterized.expand(
        [
            [
                [
                    {
                        'object_type': 'node',
                        'attribute': 'nodeHostname',
                        'comparator': 'eq',
                        'value': 'my_machine.my_domain',
                    }
                ],
                'where=[{"objectType":"node","attribute":"nodeHostname","comparator":"eq","value":"my_machine.my_domain"}]',
            ],
            [
                [
                    {
                        'object_type': 'node',
                        'attribute': 'OS',
                        'comparator': 'eq',
                        'value': 'Linux',
                    },
                    {
                        'object_type': 'node',
                        'attribute': 'osFullName',
                        'comparator': 'regex',
                        'value': '.*Linux.*',
                    },
                    {
                        'object_type': 'memoryPhysicalElement',
                        'attribute': 'quantity',
                        'comparator': 'gteq',
                        'value': '1',
                    },
                ],
                'where=[{"objectType":"node","attribute":"OS","comparator":"eq","value":"Linux"},{"objectType":"node","attribute":"osFullName","comparator":"regex","value":".*Linux.*"},{"objectType":"memoryPhysicalElement","attribute":"quantity","comparator":"gteq","value":"1"}]',
            ],
        ]
    )
    def test_query_translation(self, json_query, expected):
        self.maxDiff = None
        self.assertEqual(
            node_settings.json_query_to_url_query(json_query), expected
        )


if __name__ == '__main__':
    unittest.main()
