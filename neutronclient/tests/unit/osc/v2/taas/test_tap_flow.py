# Copyright (c) 2018 AT&T Corporation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from neutronclient.osc.v2.taas import taas_tap_flow
from neutronclient.tests.unit.osc.v2.taas import fakes


def _get_id(client, id_or_name, resource):
    return id_or_name


class TestCreateTaasTapFlow(fakes.TestNeutronClientOSCV2):
    # The new tap_flow created
    _tap_flow = fakes.FakeTaasTapFlow.create_tap_flow()

    columns = ('Description',
               'Direction',
               'ID',
               'Name',
               'Project',
               'Source Port',
               'Tap Service Port',
               'Vlan Mirror')

    def get_data(self):
        return (
            self._tap_flow['description'],
            self._tap_flow['direction'],
            self._tap_flow['id'],
            self._tap_flow['name'],
            self._tap_flow['project_id'],
            self._tap_flow['port'],
            self._tap_flow['tap_service'],
            self._tap_flow['vlan_mirror'],
        )

    def setUp(self):
        super(TestCreateTaasTapFlow, self).setUp()
        mock.patch('neutronclient.osc.v2.taas.taas_tap_flow._get_id',
                   new=_get_id).start()
        self.neutronclient.create_tap_flow = mock.Mock(
            return_value={'tap_flow': self._tap_flow})
        self.data = self.get_data()

        # Get the command object to test
        self.cmd = taas_tap_flow.CreateTaasTapFlow(self.app, self.namespace)

    def test_create_tap_flow_default_options(self):
        arglist = [
            "--port", self._tap_flow['port'],
            "--tap-service", self._tap_flow['tap_service'],
            "--direction", self._tap_flow['direction'],
            "--vlan-mirror", self._tap_flow['vlan_mirror']
        ]
        verifylist = [
            ('source_port', self._tap_flow['port']),
            ('tap_service_id', self._tap_flow['tap_service']),
            ('direction', self._tap_flow['direction']),
            ('vlan_mirror', self._tap_flow['vlan_mirror'])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.neutronclient.create_tap_flow.assert_called_once_with({
            'tap_flow': {'source_port': self._tap_flow['port'],
                         'tap_service_id': self._tap_flow['tap_service'],
                         'direction': self._tap_flow['direction'],
                         'vlan_mirror': self._tap_flow['vlan_mirror'],
                         }
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def _test_create_tap_flow_all_options(self):
        arglist = [
            "--description", self._tap_flow['description'],
            "--port", self._tap_flow['port'],
            "--tap-service", self._tap_flow['tap_service'],
            "--direction", self._tap_flow['direction'],
            "--vlan-mirror", self._tap_flow['vlan_mirror'],
            "--name", self._tap_flow['name'],
        ]

        verifylist = [
            ('source_port', self._tap_flow['port']),
            ('tap_service_id', self._tap_flow['tap_service']),
            ('name', self._tap_flow['name']),
            ('description', self._tap_flow['description']),
            ('direction', self._tap_flow['direction']),
            ('vlan_mirror', self._tap_flow['vlan_mirror'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.neutronclient.create_tap_flow.assert_called_once_with({
            'tap_flow': {'name': self._tap_flow['name'],
                         'source_port': self._tap_flow['port'],
                         'tap_service_id': self._tap_flow['tap_service'],
                         'description': self._tap_flow['description'],
                         'direction': self._tap_flow['direction'],
                         'vlan_mirror': self._tap_flow['vlan_mirror'],
                         }
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_tap_flow_all_options(self):
        self._test_create_tap_flow_all_options()

    def test_create_tap_flow_all_options_mpls(self):
        self._test_create_tap_flow_all_options()


class TestDeleteTaasTapFlow(fakes.TestNeutronClientOSCV2):

    _tap_flow = fakes.FakeTaasTapFlow.create_tap_flows(count=1)

    def setUp(self):
        super(TestDeleteTaasTapFlow, self).setUp()
        mock.patch('neutronclient.osc.v2.taas.taas_tap_flow._get_id',
                   new=_get_id).start()
        self.neutronclient.delete_tap_flow = mock.Mock(return_value=None)
        self.cmd = taas_tap_flow.DeleteTaasTapFlow(self.app, self.namespace)

    def test_delete_tap_flow(self):
        client = self.app.client_manager.neutronclient
        mock_tap_flow_delete = client.delete_tap_flow
        arglist = [
            self._tap_flow[0]['id'],
        ]
        verifylist = [
            ('tap_flow', self._tap_flow[0]['id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        mock_tap_flow_delete.assert_called_once_with(
            self._tap_flow[0]['id'])
        self.assertIsNone(result)


class TestListTaasTapFlow(fakes.TestNeutronClientOSCV2):
    _tap_flows = fakes.FakeTaasTapFlow.create_tap_flows()
    columns = ['ID', 'Name', 'Status', 'Source Port', 'Tap Service Port',
               'Direction', 'Vlan Mirror']
    columns_long = ['ID', 'Name', 'Status', 'Source Port',
                    'Tap Service Port', 'Direction', 'Vlan Mirror',
                    'Description', 'Project']
    _tap_flow = _tap_flows[0]
    data = [
        _tap_flow['id'],
        _tap_flow['name'],
        _tap_flow['port'],
        _tap_flow['tap_service'],
        _tap_flow['direction'],
        _tap_flow['vlan_mirror']
    ]
    data_long = [
        _tap_flow['id'],
        _tap_flow['name'],
        _tap_flow['port'],
        _tap_flow['tap_service'],
        _tap_flow['direction'],
        _tap_flow['vlan_mirror'],
        _tap_flow['description']
    ]
    _tap_flow1 = {'tap_flows': _tap_flow}
    _tap_flow_id = _tap_flow['id'],

    def setUp(self):
        super(TestListTaasTapFlow, self).setUp()
        mock.patch('neutronclient.osc.v2.taas.taas_tap_flow._get_id',
                   new=_get_id).start()
        self.neutronclient.list_tap_flows = mock.Mock(
            return_value={'tap_flows': self._tap_flows}
        )
        # Get the command object to test
        self.cmd = taas_tap_flow.ListTaasTapFlow(self.app, self.namespace)

    def test_list_tap_flows(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns = self.cmd.take_action(parsed_args)[0]
        tap_flows = self.neutronclient.list_tap_flows()['tap_flows']
        tap_flow = tap_flows[0]
        data = [
            tap_flow['id'],
            tap_flow['name'],
            tap_flow['port'],
            tap_flow['tap_service'],
            tap_flow['direction'],
            tap_flow['vlan_mirror']
        ]
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        tap_flows = self.neutronclient.list_tap_flows()['tap_flows']
        tap_flow = tap_flows[0]
        data = [
            tap_flow['id'],
            tap_flow['name'],
            tap_flow['port'],
            tap_flow['tap_service'],
            tap_flow['direction'],
            tap_flow['vlan_mirror'],
            tap_flow['description']
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns_long = self.cmd.take_action(parsed_args)[0]
        self.assertEqual(self.columns_long, columns_long)
        self.assertEqual(self.data_long, data)


class TestSetTaasTapFlow(fakes.TestNeutronClientOSCV2):
    _tap_flow = fakes.FakeTaasTapFlow.create_tap_flow()
    _tap_flow_name = _tap_flow['name']
    _tap_flow_id = _tap_flow['id']

    def setUp(self):
        super(TestSetTaasTapFlow, self).setUp()
        mock.patch('neutronclient.osc.v2.taas.taas_tap_flow._get_id',
                   new=_get_id).start()
        self.neutronclient.update_tap_flow = mock.Mock(return_value=None)
        self.cmd = taas_tap_flow.SetTaasTapFlow(self.app, self.namespace)

    def test_set_tap_flow(self):
        client = self.app.client_manager.neutronclient
        mock_tap_flow_update = client.update_tap_flow
        arglist = [
            self._tap_flow_name,
            '--name', 'name_updated',
            '--description', 'desc_updated'
        ]
        verifylist = [
            ('tap_flow', self._tap_flow_name),
            ('name', 'name_updated'),
            ('description', 'desc_updated'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {'tap_flow': {
            'name': 'name_updated',
            'description': 'desc_updated'}
        }
        mock_tap_flow_update.assert_called_once_with(self._tap_flow_name,
                                                     attrs)
        self.assertIsNone(result)


class TestShowTaasTapFlow(fakes.TestNeutronClientOSCV2):

    _tf = fakes.FakeTaasTapFlow.create_tap_flow()

    data = (
        _tf['description'],
        _tf['direction'],
        _tf['vlan_mirror'],
        _tf['id'],
        _tf['name'],
        _tf['project_id'],
        _tf['port'],
        _tf['tap_service'],
    )
    _tap_flow = {'tap_flow': _tf}
    _tap_flow_id = _tf['id']
    columns = (
        'Description',
        'Direction',
        'Vlan Mirror',
        'ID',
        'Name',
        'Project',
        'Source Port',
        'Tap Service Port'
    )

    def setUp(self):
        super(TestShowTaasTapFlow, self).setUp()
        mock.patch('neutronclient.osc.v2.taas.taas_tap_flow._get_id',
                   new=_get_id).start()

        self.neutronclient.show_tap_flow = mock.Mock(
            return_value=self._tap_flow
        )

        # Get the command object to test
        self.cmd = taas_tap_flow.ShowTaasTapFlow(self.app, self.namespace)

    def test_show_tap_flow(self):
        client = self.app.client_manager.neutronclient
        mock_tap_flow_show = client.show_tap_flow
        arglist = [
            self._tap_flow_id,
        ]
        verifylist = [
            ('tap_flow', self._tap_flow_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        mock_tap_flow_show.assert_called_once_with(self._tap_flow_id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
