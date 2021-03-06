#!/usr/bin/env python

'''
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
'''
import os
from mock.mock import MagicMock, call, patch
from stacks.utils.RMFTestCase import *

class TestHiveMetastore(RMFTestCase):
  COMMON_SERVICES_PACKAGE_DIR = "HIVE/0.12.0.2.0/package"
  STACK_VERSION = "2.0.6"
  
  def test_configure_default(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hive_metastore.py",
                       classname = "HiveMetastore",
                       command = "configure",
                       config_file="../../2.1/configs/default.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assert_configure_default()

  def test_start_default(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hive_metastore.py",
                       classname = "HiveMetastore",
                       command = "start",
                       config_file="../../2.1/configs/default.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )

    self.assert_configure_default()
    self.assertResourceCalled('Execute', 'env HADOOP_HOME=/usr JAVA_HOME=/usr/jdk64/jdk1.7.0_45 /tmp/start_metastore_script /var/log/hive/hive.out /var/log/hive/hive.log /var/run/hive/hive.pid /etc/hive/conf.server /var/log/hive',
                              not_if = 'ls /var/run/hive/hive.pid >/dev/null 2>&1 && ps -p `cat /var/run/hive/hive.pid` >/dev/null 2>&1',
                              environment = {'HADOOP_HOME': '/usr'},
                              path = ["/bin:/usr/lib/hive/bin:/usr/bin"],
                              user = 'hive'
    )

    self.assertResourceCalled('Execute', '/usr/jdk64/jdk1.7.0_45/bin/java -cp /usr/lib/ambari-agent/DBConnectionVerification.jar:/usr/lib/hive/lib//mysql-connector-java.jar org.apache.ambari.server.DBConnectionVerification \'jdbc:mysql://c6402.ambari.apache.org/hive?createDatabaseIfNotExist=true\' hive aaa com.mysql.jdbc.Driver',
        path = ['/usr/sbin:/sbin:/usr/local/bin:/bin:/usr/bin'],
        tries = 5,
        try_sleep = 10,
    )

    self.assertNoMoreResources()

  def test_stop_default(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hive_metastore.py",
                       classname = "HiveMetastore",
                       command = "stop",
                       config_file="../../2.1/configs/default.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )

    self.assertResourceCalled('Execute', 'sudo kill `cat /var/run/hive/hive.pid`',
                              not_if = '! (ls /var/run/hive/hive.pid >/dev/null 2>&1 && ps -p `cat /var/run/hive/hive.pid` >/dev/null 2>&1)',
                              )
    self.assertResourceCalled('Execute', 'sudo kill -9 `cat /var/run/hive/hive.pid`',
                              not_if = '! (ls /var/run/hive/hive.pid >/dev/null 2>&1 && ps -p `cat /var/run/hive/hive.pid` >/dev/null 2>&1) || ( sleep 5 && ! (ls /var/run/hive/hive.pid >/dev/null 2>&1 && ps -p `cat /var/run/hive/hive.pid` >/dev/null 2>&1) )',
                              )
    self.assertResourceCalled('Execute', '! (ls /var/run/hive/hive.pid >/dev/null 2>&1 && ps -p `cat /var/run/hive/hive.pid` >/dev/null 2>&1)',
      tries = 20,
      try_sleep = 3,
    )
    self.assertResourceCalled('File', '/var/run/hive/hive.pid',
                              action = ['delete'],
                              )
    self.assertNoMoreResources()

  def test_configure_secured(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hive_metastore.py",
                       classname = "HiveMetastore",
                       command = "configure",
                       config_file="../../2.1/configs/secured.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assert_configure_secured()
    self.assertNoMoreResources()

  def test_start_secured(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hive_metastore.py",
                       classname = "HiveMetastore",
                       command = "start",
                       config_file="../../2.1/configs/secured.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )

    self.assert_configure_secured()
    self.assertResourceCalled('Execute', '/usr/bin/kinit -kt /etc/security/keytabs/hive.service.keytab hive/c6401.ambari.apache.org@EXAMPLE.COM; ',
                              user = 'hive',
                              )
    self.assertResourceCalled('Execute', 'env HADOOP_HOME=/usr JAVA_HOME=/usr/jdk64/jdk1.7.0_45 /tmp/start_metastore_script /var/log/hive/hive.out /var/log/hive/hive.log /var/run/hive/hive.pid /etc/hive/conf.server /var/log/hive',
                              not_if = 'ls /var/run/hive/hive.pid >/dev/null 2>&1 && ps -p `cat /var/run/hive/hive.pid` >/dev/null 2>&1',
                              environment = {'HADOOP_HOME' : '/usr'},
                              path = ["/bin:/usr/lib/hive/bin:/usr/bin"],
                              user = 'hive'
    )

    self.assertResourceCalled('Execute', '/usr/jdk64/jdk1.7.0_45/bin/java -cp /usr/lib/ambari-agent/DBConnectionVerification.jar:/usr/lib/hive/lib//mysql-connector-java.jar org.apache.ambari.server.DBConnectionVerification \'jdbc:mysql://c6402.ambari.apache.org/hive?createDatabaseIfNotExist=true\' hive asd com.mysql.jdbc.Driver',
                              path=['/usr/sbin:/sbin:/usr/local/bin:/bin:/usr/bin'], tries=5, try_sleep=10
    )

    self.assertNoMoreResources()

  def test_stop_secured(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hive_metastore.py",
                       classname = "HiveMetastore",
                       command = "stop",
                       config_file="../../2.1/configs/secured.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )

    self.assertResourceCalled('Execute', 'sudo kill `cat /var/run/hive/hive.pid`',
      not_if = '! (ls /var/run/hive/hive.pid >/dev/null 2>&1 && ps -p `cat /var/run/hive/hive.pid` >/dev/null 2>&1)',
    )
    self.assertResourceCalled('Execute', 'sudo kill -9 `cat /var/run/hive/hive.pid`',
      not_if = '! (ls /var/run/hive/hive.pid >/dev/null 2>&1 && ps -p `cat /var/run/hive/hive.pid` >/dev/null 2>&1) || ( sleep 5 && ! (ls /var/run/hive/hive.pid >/dev/null 2>&1 && ps -p `cat /var/run/hive/hive.pid` >/dev/null 2>&1) )',
    )
    self.assertResourceCalled('Execute', '! (ls /var/run/hive/hive.pid >/dev/null 2>&1 && ps -p `cat /var/run/hive/hive.pid` >/dev/null 2>&1)',
      tries = 20,
      try_sleep = 3,
    )
    self.assertResourceCalled('File', '/var/run/hive/hive.pid',
      action = ['delete'],
    )
    self.assertNoMoreResources()

  def assert_configure_default(self):
    self.assertResourceCalled('Directory', '/etc/hive',
                              mode = 0755,
                              )
    self.assertResourceCalled('Directory', '/etc/hive/conf',
                              owner = 'hive',
                              group = 'hadoop',
                              recursive = True,
                              )
    self.assertResourceCalled('XmlConfig', 'mapred-site.xml',
                              group = 'hadoop',
                              conf_dir = '/etc/hive/conf',
                              mode = 0644,
                              configuration_attributes = {u'final': {u'mapred.healthChecker.script.path': u'true',
                                                                     u'mapreduce.jobtracker.staging.root.dir': u'true'}},
                              owner = 'hive',
                              configurations = self.getConfig()['configurations']['mapred-site'],
                              )
    self.assertResourceCalled('File', '/etc/hive/conf/hive-default.xml.template',
                              owner = 'hive',
                              group = 'hadoop',
                              )
    self.assertResourceCalled('File', '/etc/hive/conf/hive-env.sh.template',
                              owner = 'hive',
                              group = 'hadoop',
                              )
    self.assertResourceCalled('XmlConfig', 'hive-site.xml',
                              group = 'hadoop',
                              conf_dir = '/etc/hive/conf.server',
                              mode = 0644,
                              configuration_attributes = {u'final': {u'hive.optimize.bucketmapjoin.sortedmerge': u'true',
                                                                     u'javax.jdo.option.ConnectionDriverName': u'true',
                                                                     u'javax.jdo.option.ConnectionPassword': u'true'}},
                              owner = 'hive',
                              configurations = self.getConfig()['configurations']['hive-site'],
                              )
    self.assertResourceCalled('File', '/etc/hive/conf.server/hive-env.sh',
                              content = InlineTemplate(self.getConfig()['configurations']['hive-env']['content']),
                              owner = 'hive',
                              group = 'hadoop',
                              )
    self.assertResourceCalled('Execute', ('cp',
                                          '--remove-destination',
                                          '/usr/share/java/mysql-connector-java.jar',
                                          '/usr/lib/hive/lib//mysql-connector-java.jar'),
                              path = ['/bin', '/usr/bin/'],
                              sudo = True,
                              )
    self.assertResourceCalled('File', '/usr/lib/ambari-agent/DBConnectionVerification.jar',
        content = DownloadSource('http://c6401.ambari.apache.org:8080/resources/DBConnectionVerification.jar'),
    )
    self.assertResourceCalled('File', '/tmp/start_metastore_script',
                              content = StaticFile('startMetastore.sh'),
                              mode = 0755,
                              )
    self.assertResourceCalled('Execute', 'export HIVE_CONF_DIR=/etc/hive/conf.server ; /usr/lib/hive/bin/schematool -initSchema -dbType mysql -userName hive -passWord aaa',
                              not_if = 'export HIVE_CONF_DIR=/etc/hive/conf.server ; /usr/lib/hive/bin/schematool -info -dbType mysql -userName hive -passWord aaa',
                              )
    self.assertResourceCalled('Directory', '/var/run/hive',
                              owner = 'hive',
                              group = 'hadoop',
                              mode = 0755,
                              recursive = True,
                              )
    self.assertResourceCalled('Directory', '/var/log/hive',
                              owner = 'hive',
                              group = 'hadoop',
                              mode = 0755,
                              recursive = True,
                              )
    self.assertResourceCalled('Directory', '/var/lib/hive',
                              owner = 'hive',
                              group = 'hadoop',
                              mode = 0755,
                              recursive = True,
                              )

  def assert_configure_secured(self):
    self.assertResourceCalled('Directory', '/etc/hive',
                              mode = 0755,
                              )
    self.assertResourceCalled('Directory', '/etc/hive/conf',
                              owner = 'hive',
                              group = 'hadoop',
                              recursive = True,
                              )
    self.assertResourceCalled('XmlConfig', 'mapred-site.xml',
                              group = 'hadoop',
                              conf_dir = '/etc/hive/conf',
                              mode = 0644,
                              configuration_attributes = {u'final': {u'mapred.healthChecker.script.path': u'true',
                                                                     u'mapreduce.jobtracker.staging.root.dir': u'true'}},
                              owner = 'hive',
                              configurations = self.getConfig()['configurations']['mapred-site'],
                              )
    self.assertResourceCalled('File', '/etc/hive/conf/hive-default.xml.template',
                              owner = 'hive',
                              group = 'hadoop',
                              )
    self.assertResourceCalled('File', '/etc/hive/conf/hive-env.sh.template',
                              owner = 'hive',
                              group = 'hadoop',
                              )
    self.assertResourceCalled('XmlConfig', 'hive-site.xml',
                              group = 'hadoop',
                              conf_dir = '/etc/hive/conf.server',
                              mode = 0644,
                              configuration_attributes = {u'final': {u'hive.optimize.bucketmapjoin.sortedmerge': u'true',
                                                                     u'javax.jdo.option.ConnectionDriverName': u'true',
                                                                     u'javax.jdo.option.ConnectionPassword': u'true'}},
                              owner = 'hive',
                              configurations = self.getConfig()['configurations']['hive-site'],
                              )
    self.assertResourceCalled('File', '/etc/hive/conf.server/hive-env.sh',
                              content = InlineTemplate(self.getConfig()['configurations']['hive-env']['content']),
                              owner = 'hive',
                              group = 'hadoop',
                              )
    self.assertResourceCalled('Execute', ('cp',
                                          '--remove-destination',
                                          '/usr/share/java/mysql-connector-java.jar',
                                          '/usr/lib/hive/lib//mysql-connector-java.jar'),
                              path = ['/bin', '/usr/bin/'],
                              sudo = True,
                              )
    self.assertResourceCalled('File', '/usr/lib/ambari-agent/DBConnectionVerification.jar',
        content = DownloadSource('http://c6401.ambari.apache.org:8080/resources/DBConnectionVerification.jar'),
    )
    self.assertResourceCalled('File', '/tmp/start_metastore_script',
                              content = StaticFile('startMetastore.sh'),
                              mode = 0755,
                              )
    self.assertResourceCalled('Execute', 'export HIVE_CONF_DIR=/etc/hive/conf.server ; /usr/lib/hive/bin/schematool -initSchema -dbType mysql -userName hive -passWord asd',
                              not_if = 'export HIVE_CONF_DIR=/etc/hive/conf.server ; /usr/lib/hive/bin/schematool -info -dbType mysql -userName hive -passWord asd',
                              )
    self.assertResourceCalled('Directory', '/var/run/hive',
                              owner = 'hive',
                              group = 'hadoop',
                              mode = 0755,
                              recursive = True,
                              )
    self.assertResourceCalled('Directory', '/var/log/hive',
                              owner = 'hive',
                              group = 'hadoop',
                              mode = 0755,
                              recursive = True,
                              )
    self.assertResourceCalled('Directory', '/var/lib/hive',
                              owner = 'hive',
                              group = 'hadoop',
                              mode = 0755,
                              recursive = True,
                              )

  @patch("resource_management.libraries.functions.security_commons.build_expectations")
  @patch("resource_management.libraries.functions.security_commons.get_params_from_filesystem")
  @patch("resource_management.libraries.functions.security_commons.validate_security_config_properties")
  @patch("resource_management.libraries.functions.security_commons.cached_kinit_executor")
  @patch("resource_management.libraries.script.Script.put_structured_out")
  def test_security_status(self, put_structured_out_mock, cached_kinit_executor_mock, validate_security_config_mock, get_params_mock, build_exp_mock):
    # Test that function works when is called with correct parameters
    import status_params

    security_params = {
      'hive-site': {
        'hive.server2.authentication': "KERBEROS",
        'hive.metastore.sasl.enabled': "true",
        'hive.security.authorization.enabled': 'true',
        'hive.metastore.kerberos.keytab.file': 'path/to/keytab',
        'hive.metastore.kerberos.principal': 'principal'
      }
    }
    result_issues = []
    props_value_check = {
      'hive.server2.authentication': "KERBEROS",
      'hive.metastore.sasl.enabled': "true",
      'hive.security.authorization.enabled': 'true'
    }
    props_empty_check = [
      'hive.metastore.kerberos.keytab.file',
      'hive.metastore.kerberos.principal'
    ]
    props_read_check = [
      'hive.metastore.kerberos.keytab.file'
    ]

    get_params_mock.return_value = security_params
    validate_security_config_mock.return_value = result_issues

    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hive_metastore.py",
                       classname = "HiveMetastore",
                       command = "security_status",
                       config_file="../../2.1/configs/secured.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )

    get_params_mock.assert_called_with(status_params.hive_conf_dir, {'hive-site.xml': "XML"})
    build_exp_mock.assert_called_with('hive-site', props_value_check, props_empty_check, props_read_check)
    put_structured_out_mock.assert_called_with({"securityState": "SECURED_KERBEROS"})
    self.assertTrue(cached_kinit_executor_mock.call_count, 2)
    cached_kinit_executor_mock.assert_called_with(status_params.kinit_path_local,
                                                  status_params.hive_user,
                                                  security_params['hive-site']['hive.metastore.kerberos.keytab.file'],
                                                  security_params['hive-site']['hive.metastore.kerberos.principal'],
                                                  status_params.hostname,
                                                  status_params.tmp_dir)

    # Testing that the exception throw by cached_executor is caught
    cached_kinit_executor_mock.reset_mock()
    cached_kinit_executor_mock.side_effect = Exception("Invalid command")

    try:
      self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hive_metastore.py",
                         classname = "HiveMetastore",
                         command = "security_status",
                         config_file="../../2.1/configs/secured.json",
                         hdp_stack_version = self.STACK_VERSION,
                         target = RMFTestCase.TARGET_COMMON_SERVICES
      )
    except:
      self.assertTrue(True)

    # Testing with a security_params which doesn't contains startup
    empty_security_params = {}
    cached_kinit_executor_mock.reset_mock()
    get_params_mock.reset_mock()
    put_structured_out_mock.reset_mock()
    get_params_mock.return_value = empty_security_params

    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hive_metastore.py",
                       classname = "HiveMetastore",
                       command = "security_status",
                       config_file="../../2.1/configs/secured.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    put_structured_out_mock.assert_called_with({"securityIssuesFound": "Keytab file or principal are not set property."})

    # Testing with not empty result_issues
    result_issues_with_params = {}
    result_issues_with_params['hive-site']="Something bad happened"

    validate_security_config_mock.reset_mock()
    get_params_mock.reset_mock()
    validate_security_config_mock.return_value = result_issues_with_params
    get_params_mock.return_value = security_params

    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hive_metastore.py",
                       classname = "HiveMetastore",
                       command = "security_status",
                       config_file="../../2.1/configs/secured.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    put_structured_out_mock.assert_called_with({"securityState": "UNSECURED"})

    # Testing with security_enable = false
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hive_metastore.py",
                       classname = "HiveMetastore",
                       command = "security_status",
                       config_file="../../2.1/configs/default.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    put_structured_out_mock.assert_called_with({"securityState": "UNSECURED"})