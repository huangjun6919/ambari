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

from mock.mock import MagicMock, call, patch
from stacks.utils.RMFTestCase import *
import  resource_management.core.source
from test_storm_base import TestStormBase

class TestStormSupervisor(TestStormBase):

  def test_configure_default(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/supervisor.py",
                       classname = "Supervisor",
                       command = "configure",
                       config_file="default.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assert_configure_default()
    self.assertNoMoreResources()

  def test_start_default(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/supervisor.py",
                       classname = "Supervisor",
                       command = "start",
                       config_file="default.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )

    self.assert_configure_default()

    self.assertResourceCalled('Execute', 'env JAVA_HOME=/usr/jdk64/jdk1.7.0_45 PATH=$PATH:/usr/jdk64/jdk1.7.0_45/bin storm supervisor > /var/log/storm/supervisor.out 2>&1',
      wait_for_finish = False,
      not_if = 'ls /var/run/storm/supervisor.pid >/dev/null 2>&1 && ps -p `cat /var/run/storm/supervisor.pid` >/dev/null 2>&1',
      path = ['/usr/bin'],
      user = 'storm',
    )
    self.assertResourceCalled('Execute', "/usr/jdk64/jdk1.7.0_45/bin/jps -l  | grep storm.daemon.supervisor$ && /usr/jdk64/jdk1.7.0_45/bin/jps -l  | grep storm.daemon.supervisor$ | awk {'print $1'} > /var/run/storm/supervisor.pid",
        logoutput = True,
        path = ['/usr/bin'],
        tries = 6,
        user = 'storm',
        try_sleep = 10,
    )
    self.assertResourceCalled('Execute', 'env JAVA_HOME=/usr/jdk64/jdk1.7.0_45 PATH=$PATH:/usr/jdk64/jdk1.7.0_45/bin storm logviewer > /var/log/storm/logviewer.out 2>&1',
        wait_for_finish = False,
        path = ['/usr/bin'],
        user = 'storm',
        not_if = 'ls /var/run/storm/logviewer.pid >/dev/null 2>&1 && ps -p `cat /var/run/storm/logviewer.pid` >/dev/null 2>&1',
    )
    self.assertResourceCalled('Execute', "/usr/jdk64/jdk1.7.0_45/bin/jps -l  | grep storm.daemon.logviewer$ && /usr/jdk64/jdk1.7.0_45/bin/jps -l  | grep storm.daemon.logviewer$ | awk {'print $1'} > /var/run/storm/logviewer.pid",
        logoutput = True,
        path = ['/usr/bin'],
        tries = 12,
        user = 'storm',
        try_sleep = 10,
    )
    self.assertNoMoreResources()

  def test_stop_default(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/supervisor.py",
                       classname = "Supervisor",
                       command = "stop",
                       config_file="default.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assertResourceCalled('Execute', 'sudo kill `cat /var/run/storm/supervisor.pid`',
        not_if = '! (ls /var/run/storm/supervisor.pid >/dev/null 2>&1 && ps -p `cat /var/run/storm/supervisor.pid` >/dev/null 2>&1)',
    )
    self.assertResourceCalled('Execute', 'sudo kill -9 `cat /var/run/storm/supervisor.pid`',
        not_if = 'sleep 2; ! (ls /var/run/storm/supervisor.pid >/dev/null 2>&1 && ps -p `cat /var/run/storm/supervisor.pid` >/dev/null 2>&1) || sleep 20; ! (ls /var/run/storm/supervisor.pid >/dev/null 2>&1 && ps -p `cat /var/run/storm/supervisor.pid` >/dev/null 2>&1)',
        ignore_failures = True,
    )
    self.assertResourceCalled('File', '/var/run/storm/supervisor.pid',
        action = ['delete'],
    )
    self.assertResourceCalled('Execute', 'sudo kill `cat /var/run/storm/logviewer.pid`',
        not_if = '! (ls /var/run/storm/logviewer.pid >/dev/null 2>&1 && ps -p `cat /var/run/storm/logviewer.pid` >/dev/null 2>&1)',
    )
    self.assertResourceCalled('Execute', 'sudo kill -9 `cat /var/run/storm/logviewer.pid`',
        not_if = 'sleep 2; ! (ls /var/run/storm/logviewer.pid >/dev/null 2>&1 && ps -p `cat /var/run/storm/logviewer.pid` >/dev/null 2>&1) || sleep 20; ! (ls /var/run/storm/logviewer.pid >/dev/null 2>&1 && ps -p `cat /var/run/storm/logviewer.pid` >/dev/null 2>&1)',
        ignore_failures = True,
    )
    self.assertResourceCalled('File', '/var/run/storm/logviewer.pid',
        action = ['delete'],
    )
    self.assertNoMoreResources()

  def test_configure_secured(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/supervisor.py",
                       classname = "Supervisor",
                       command = "configure",
                       config_file="secured.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assert_configure_secured()
    self.assertNoMoreResources()

  def test_start_secured(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/supervisor.py",
                       classname = "Supervisor",
                       command = "start",
                       config_file="secured.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )

    self.assert_configure_secured()

    self.assertResourceCalled('Execute', 'env JAVA_HOME=/usr/jdk64/jdk1.7.0_45 PATH=$PATH:/usr/jdk64/jdk1.7.0_45/bin storm supervisor > /var/log/storm/supervisor.out 2>&1',
      wait_for_finish = False,
      not_if = 'ls /var/run/storm/supervisor.pid >/dev/null 2>&1 && ps -p `cat /var/run/storm/supervisor.pid` >/dev/null 2>&1',
      path = ['/usr/bin'],
      user = 'storm',
    )

    self.assertResourceCalled('Execute', "/usr/jdk64/jdk1.7.0_45/bin/jps -l  | grep storm.daemon.supervisor$ && /usr/jdk64/jdk1.7.0_45/bin/jps -l  | grep storm.daemon.supervisor$ | awk {'print $1'} > /var/run/storm/supervisor.pid",
        logoutput = True,
        path = ['/usr/bin'],
        tries = 6,
        user = 'storm',
        try_sleep = 10,
    )
    self.assertResourceCalled('Execute', 'env JAVA_HOME=/usr/jdk64/jdk1.7.0_45 PATH=$PATH:/usr/jdk64/jdk1.7.0_45/bin storm logviewer > /var/log/storm/logviewer.out 2>&1',
        wait_for_finish = False,
        path = ['/usr/bin'],
        user = 'storm',
        not_if = 'ls /var/run/storm/logviewer.pid >/dev/null 2>&1 && ps -p `cat /var/run/storm/logviewer.pid` >/dev/null 2>&1',
    )
    self.assertResourceCalled('Execute', "/usr/jdk64/jdk1.7.0_45/bin/jps -l  | grep storm.daemon.logviewer$ && /usr/jdk64/jdk1.7.0_45/bin/jps -l  | grep storm.daemon.logviewer$ | awk {'print $1'} > /var/run/storm/logviewer.pid",
        logoutput = True,
        path = ['/usr/bin'],
        tries = 12,
        user = 'storm',
        try_sleep = 10,
    )
    self.assertNoMoreResources()

  def test_stop_secured(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/supervisor.py",
                       classname = "Supervisor",
                       command = "stop",
                       config_file="secured.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assertResourceCalled('Execute', 'sudo kill `cat /var/run/storm/supervisor.pid`',
        not_if = '! (ls /var/run/storm/supervisor.pid >/dev/null 2>&1 && ps -p `cat /var/run/storm/supervisor.pid` >/dev/null 2>&1)',
    )
    self.assertResourceCalled('Execute', 'sudo kill -9 `cat /var/run/storm/supervisor.pid`',
        not_if = 'sleep 2; ! (ls /var/run/storm/supervisor.pid >/dev/null 2>&1 && ps -p `cat /var/run/storm/supervisor.pid` >/dev/null 2>&1) || sleep 20; ! (ls /var/run/storm/supervisor.pid >/dev/null 2>&1 && ps -p `cat /var/run/storm/supervisor.pid` >/dev/null 2>&1)',
        ignore_failures = True,
    )
    self.assertResourceCalled('File', '/var/run/storm/supervisor.pid',
        action = ['delete'],
    )
    self.assertResourceCalled('Execute', 'sudo kill `cat /var/run/storm/logviewer.pid`',
        not_if = '! (ls /var/run/storm/logviewer.pid >/dev/null 2>&1 && ps -p `cat /var/run/storm/logviewer.pid` >/dev/null 2>&1)',
    )
    self.assertResourceCalled('Execute', 'sudo kill -9 `cat /var/run/storm/logviewer.pid`',
        not_if = 'sleep 2; ! (ls /var/run/storm/logviewer.pid >/dev/null 2>&1 && ps -p `cat /var/run/storm/logviewer.pid` >/dev/null 2>&1) || sleep 20; ! (ls /var/run/storm/logviewer.pid >/dev/null 2>&1 && ps -p `cat /var/run/storm/logviewer.pid` >/dev/null 2>&1)',
        ignore_failures = True,
    )
    self.assertResourceCalled('File', '/var/run/storm/logviewer.pid',
        action = ['delete'],
    )
    self.assertNoMoreResources()

  def test_pre_rolling_restart(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/supervisor.py",
                       classname = "Supervisor",
                       command = "pre_rolling_restart",
                       config_file="default.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES)

    self.assertResourceCalled("Execute", "hdp-select set storm-supervisor 2.2.1.0-2067")
