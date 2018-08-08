# Copyright (c) 2018 AT&T Corporation
# All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import argparse
import copy

import mock

from osc_lib.tests import utils
from oslo_utils import uuidutils


class TestNeutronClientOSCV2(utils.TestCommand):

    def setUp(self):
        super(TestNeutronClientOSCV2, self).setUp()
        self.namespace = argparse.Namespace()
        self.app.client_manager.session = mock.Mock()
        self.app.client_manager.neutronclient = mock.Mock()
        self.neutronclient = self.app.client_manager.neutronclient
        self.neutronclient.find_resource = mock.Mock(
            side_effect=lambda resource, name_or_id, project_id=None,
            cmd_resource=None, parent_id=None, fields=None:
            {'id': name_or_id})


class FakeTaasTapService(object):
    """Fake tap service attributes."""

    @staticmethod
    def create_tap_service(attrs=None):
        """Create a fake tap service.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A Dictionary with id, name, description, port, project_id
        """
        attrs = attrs or {}

        # Set default attributes.
        tap_service_attrs = {
            'description': 'description',
            'id': uuidutils.generate_uuid(),
            'port': uuidutils.generate_uuid(),
            'name': 'tap-service-name',
            'project_id': uuidutils.generate_uuid(),
        }

        # Overwrite default attributes.
        tap_service_attrs.update(attrs)
        return copy.deepcopy(tap_service_attrs)

    @staticmethod
    def create_tap_services(attrs=None, count=1):
        """Create multiple tap_services.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of tap_services to fake
        :return:
            A list of dictionaries faking the tap_services
        """
        tap_services = []
        for _ in range(count):
            tap_services.append(FakeTaasTapService.create_tap_service(attrs))

        return tap_services


class FakeTaasTapFlow(object):
    """Fake tap flow attributes."""

    @staticmethod
    def create_tap_flow(attrs=None):
        """Create a fake tap flow.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A Dictionary with id, name, description, port, tap_service,
            direction, project_id
        """
        attrs = attrs or {}

        # Set default attributes.
        tap_flow_attrs = {
            'id': uuidutils.generate_uuid(),
            'name': 'tap-flow-name',
            'description': 'description',
            'tap_service': uuidutils.generate_uuid(),
            'port': uuidutils.generate_uuid(),
            'direction': 'BOTH',
            'project_id': uuidutils.generate_uuid()
        }

        # tap_flow_attrs default attributes.
        tap_flow_attrs.update(attrs)
        return copy.deepcopy(tap_flow_attrs)

    @staticmethod
    def create_tap_flows(attrs=None, count=1):
        """Create multiple tap flows.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of tap_flows to fake
        :return:
            A list of dictionaries faking the tap flows
        """
        tap_flows = []
        for _ in range(count):
            tap_flows.append(
                FakeTaasTapFlow.create_tap_flow(attrs))

        return tap_flows
