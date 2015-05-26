# -*- coding: utf-8 -*-

#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from tests.product.base_product_case import BaseProductTestCase, \
    DOCKER_MOUNT_POINT, LOCAL_RESOURCES_DIR

topology_with_slave1_coord = """{'coordinator': u'slave1',
 'port': '22',
 'username': 'root',
 'workers': [u'master',
             u'slave2',
             u'slave3']}
"""

normal_topology = """{'coordinator': u'master',
 'port': '22',
 'username': 'root',
 'workers': [u'slave1',
             u'slave2',
             u'slave3']}
"""

local_topology = """{'coordinator': 'localhost',
 'port': '22',
 'username': 'root',
 'workers': ['localhost']}
"""


class TestTopologyShow(BaseProductTestCase):
    def test_topology_show(self):
        self.install_presto_admin()
        self.upload_topology()
        actual = self.run_prestoadmin('topology show')
        expected = normal_topology
        self.assertEqual(expected, actual)

    def test_topology_show_not_exists(self):
        self.install_presto_admin()
        self.assertRaisesRegexp(OSError,
                                'Missing topology configuration in '
                                '/etc/opt/prestoadmin/config.json.  '
                                'More detailed information can be found in'
                                ' /var/log/prestoadmin/presto-admin.log',
                                self.run_prestoadmin,
                                'topology show'
                                )

    def test_topology_show_coord_down(self):
        self.install_presto_admin()
        topology = {"coordinator": "slave1",
                    "workers": ["master", "slave2", "slave3"]}
        self.upload_topology(topology=topology)
        self.client.stop(self.slaves[0])
        actual = self.run_prestoadmin('topology show')
        expected = topology_with_slave1_coord
        self.assertEqual(expected, actual)

    def test_topology_show_worker_down(self):
        self.install_presto_admin()
        self.upload_topology()
        self.client.stop(self.slaves[0])
        actual = self.run_prestoadmin('topology show')
        expected = normal_topology
        self.assertEqual(expected, actual)

    def test_topology_show_empty_config(self):
        self.install_presto_admin()
        self.dump_and_cp_topology(topology={})
        actual = self.run_prestoadmin('topology show')
        self.assertEqual(local_topology, actual)

    def test_topology_show_bad_json(self):
        self.install_presto_admin()
        self.copy_to_master(os.path.join
                            (LOCAL_RESOURCES_DIR, 'invalid_json.json'))
        self.exec_create_start(self.master,
                               "cp %s /etc/opt/prestoadmin/config.json" %
                               os.path.join(DOCKER_MOUNT_POINT,
                                            "invalid_json.json"))
        self.assertRaisesRegexp(OSError,
                                'Expecting , delimiter: line 3 column 3 '
                                '\(char 21\)  More detailed information '
                                'can be found in '
                                '/var/log/prestoadmin/presto-admin.log\n',
                                self.run_prestoadmin,
                                'topology show'
                                )