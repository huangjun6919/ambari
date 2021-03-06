"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

from resource_management.libraries.functions.version import format_hdp_stack_version, compare_versions
from resource_management.libraries.functions.default import default
from resource_management import *

from status_params import *

config = Script.get_config()

stack_name = default("/hostLevelParams/stack_name", None)

# New Cluster Stack Version that is defined during the RESTART of a Rolling Upgrade
version = default("/commandParams/version", None)

stack_version_unformatted = str(config['hostLevelParams']['stack_version'])
hdp_stack_version = format_hdp_stack_version(stack_version_unformatted)

# hadoop params
if hdp_stack_version != "" and compare_versions(hdp_stack_version, '2.2') >= 0:
  hadoop_bin_dir = "/usr/hdp/current/hadoop-client/bin"

  # if this is a server action, then use the server binaries; smoke tests
  # use the client binaries
  server_role_dir_mapping = { 'FALCON_SERVER' : 'falcon-server',
    'FALCON_SERVICE_CHECK' : 'falcon-client' }

  command_role = default("/role", "")
  if command_role not in server_role_dir_mapping:
    command_role = 'FALCON_SERVICE_CHECK'

  falcon_root = server_role_dir_mapping[command_role]
  falcon_webapp_dir = format('/usr/hdp/current/{falcon_root}/webapp')
  falcon_home = format('/usr/hdp/current/{falcon_root}')
else:
  hadoop_bin_dir = "/usr/bin"
  falcon_webapp_dir = '/var/lib/falcon/webapp'
  falcon_home = '/usr/lib/falcon'

hadoop_conf_dir = "/etc/hadoop/conf"
falcon_conf_dir_prefix = "/etc/falcon"
falcon_conf_dir = format("{falcon_conf_dir_prefix}/conf")
oozie_user = config['configurations']['oozie-env']['oozie_user']
falcon_user = config['configurations']['falcon-env']['falcon_user']
smoke_user =  config['configurations']['cluster-env']['smokeuser']

user_group = config['configurations']['cluster-env']['user_group']
proxyuser_group =  config['configurations']['hadoop-env']['proxyuser_group']

java_home = config['hostLevelParams']['java_home']
falcon_local_dir = config['configurations']['falcon-env']['falcon_local_dir']
falcon_log_dir = config['configurations']['falcon-env']['falcon_log_dir']

# falcon-startup.properties
store_uri = config['configurations']['falcon-startup.properties']['*.config.store.uri']
# If these properties are present, the directories need to be created.
falcon_graph_storage_directory = default("/configurations/falcon-startup.properties/*.falcon.graph.storage.directory", None)  # explicitly set in HDP 2.2 and higher
falcon_graph_serialize_path = default("/configurations/falcon-startup.properties/*.falcon.graph.serialize.path", None)        # explicitly set in HDP 2.2 and higher

falcon_embeddedmq_data = config['configurations']['falcon-env']['falcon.embeddedmq.data']
falcon_embeddedmq_enabled = config['configurations']['falcon-env']['falcon.embeddedmq']
falcon_emeddedmq_port = config['configurations']['falcon-env']['falcon.emeddedmq.port']

falcon_host = config['clusterHostInfo']['falcon_server_hosts'][0]
falcon_port = config['configurations']['falcon-env']['falcon_port']
falcon_runtime_properties = config['configurations']['falcon-runtime.properties']
falcon_startup_properties = config['configurations']['falcon-startup.properties']
smokeuser_keytab = config['configurations']['cluster-env']['smokeuser_keytab']
falcon_env_sh_template = config['configurations']['falcon-env']['content']

flacon_apps_dir = '/apps/falcon'
#for create_hdfs_directory
security_enabled = config['configurations']['cluster-env']['security_enabled']
hostname = config["hostname"]
hdfs_user_keytab = config['configurations']['hadoop-env']['hdfs_user_keytab']
hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hdfs_principal_name = config['configurations']['hadoop-env']['hdfs_principal_name']
kinit_path_local = functions.get_kinit_path(["/usr/bin", "/usr/kerberos/bin", "/usr/sbin"])
import functools
#create partial functions with common arguments for every HdfsDirectory call
#to create hdfs directory we need to call params.HdfsDirectory in code
HdfsDirectory = functools.partial(
  HdfsDirectory,
  conf_dir=hadoop_conf_dir,
  hdfs_user=hdfs_user,
  security_enabled = security_enabled,
  keytab = hdfs_user_keytab,
  kinit_path_local = kinit_path_local,
  bin_dir = hadoop_bin_dir
)
