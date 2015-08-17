# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A script which applies RBAC definitions and role assignments stored on disk.
"""

from st2common import config
from st2common.service_setup import db_setup
from st2common.service_setup import db_teardown
from st2common.transport.bootstrap_utils import register_exchanges
from st2common.rbac.loader import RBACDefinitionsLoader
from st2common.rbac.syncer import RBACDefinitionsDBSyncer

__all__ = [
    'main'
]


def setup(argv):
    config.parse_args()

    db_setup()
    register_exchanges()


def teartown():
    db_teardown()


def apply_definitions():
    loader = RBACDefinitionsLoader()
    result = loader.load()

    role_definition_apis = result['roles'].values()
    role_assignment_apis = result['role_assignments'].values()

    syncer = RBACDefinitionsDBSyncer()
    result = syncer.sync(role_definition_apis=role_definition_apis,
                         role_assignment_apis=role_assignment_apis)

    return result


def main(argv):
    setup(argv)
    apply_definitions()
    teartown()
