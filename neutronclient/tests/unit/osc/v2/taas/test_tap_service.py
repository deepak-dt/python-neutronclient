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

from neutronclient.osc.v2.taas import taas_tap_service
from neutronclient.tests.unit.osc.v2.taas import fakes


def _get_id(client, id_or_name, resource):
    return id_or_name


class TestCreateTaasTapService(fakes.TestNeutronClientOSCV2):
    # The new tap_service created
    _tap_service = fakes.FakeTaasTapService.create_tap_service()

    columns = ('Description',
               'ID',
               'Name',
               'Project',
               'Tap Service Port')

    def get_data(self):
        return (
            self._tap_service['description'],
            self._tap_service['id'],
            self._tap_service['name'],
            self._tap_service['project_id'],
            self._tap_service['port']
        )

    def setUp(self):
        super(TestCreateTaasTapService, self).setUp()
        mock.patch('neutronclient.osc.v2.taas.taas_tap_service._get_id',
                   new=_get_id).start()
        self.neutronclient.create_taas_tap_service = mock.Mock(
            return_value={'tap_service': self._tap_service})
        self.data = self.get_data()

        # Get the command object to test
        self.cmd = taas_tap_service.CreateTaasTapService(self.app,
                                                         self.namespace)

    def test_create_tap_service_default_options(self):
        arglist = [
            "--port", self._tap_service['port'],
            "--name", self._tap_service['name'],
        ]
        verifylist = [
            ('port_id', self._tap_service['port']),
            ('name', self._tap_service['name'])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))
        self.neutronclient.create_taas_tap_service.assert_called_once_with({
            'tap_service': {'name': self._tap_service['name'],
                            'port_id': self._tap_service['port'],
                            }
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def _test_create_tap_service_all_options(self):
        arglist = [
            "--description", self._tap_service['description'],
            "--port", self._tap_service['port'],
            "--name", self._tap_service['name'],
        ]

        verifylist = [
            ('port_id', self._tap_service['port']),
            ('name', self._tap_service['name']),
            ('description', self._tap_service['description'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.neutronclient.create_taas_tap_service.assert_called_once_with({
            'tap_service': {'name': self._tap_service['name'],
                            'port_id': self._tap_service['port'],
                            'description': self._tap_service['description'],
                            }
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_tap_service_all_options(self):
        self._test_create_tap_service_all_options()

    def test_create_tap_service_all_options_mpls(self):
        self._test_create_tap_service_all_options()


class TestDeleteTaasTapService(fakes.TestNeutronClientOSCV2):

    _tap_service = fakes.FakeTaasTapService.create_tap_services(count=1)

    def setUp(self):
        super(TestDeleteTaasTapService, self).setUp()
        mock.patch('neutronclient.osc.v2.taas.taas_tap_service._get_id',
                   new=_get_id).start()
        self.neutronclient.delete_taas_tap_service = mock.Mock(
            return_value=None)
        self.cmd = taas_tap_service.DeleteTaasTapService(self.app,
                                                         self.namespace)

    def test_delete_tap_service(self):
        client = self.app.client_manager.neutronclient
        mock_tap_service_delete = client.delete_taas_tap_service
        arglist = [
            self._tap_service[0]['id'],
        ]
        verifylist = [
            ('tap_service', self._tap_service[0]['id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        mock_tap_service_delete.assert_called_once_with(
            self._tap_service[0]['id'])
        self.assertIsNone(result)


class TestListTaasTapService(fakes.TestNeutronClientOSCV2):
    _tap_services = fakes.FakeTaasTapService.create_tap_services()
    columns = ('ID', 'Name', 'Status', 'Tap Service Port')
    columns_long = ('ID', 'Name', 'Status', 'Tap Service Port',
                    'Description', 'Project')
    _tap_service = _tap_services[0]
    data = [
        _tap_service['id'],
        _tap_service['name'],
        _tap_service['port']
    ]
    data_long = [
        _tap_service['id'],
        _tap_service['name'],
        _tap_service['port'],
        _tap_service['description']
    ]
    _tap_service1 = {'tap_services': _tap_service}
    _tap_service_id = _tap_service['id'],

    def setUp(self):
        super(TestListTaasTapService, self).setUp()
        mock.patch('neutronclient.osc.v2.taas.taas_tap_service._get_id',
                   new=_get_id).start()
        self.neutronclient.list_taas_tap_services = mock.Mock(
            return_value={'tap_services': self._tap_services}
        )
        # Get the command object to test
        self.cmd = taas_tap_service.ListTaasTapService(self.app,
                                                       self.namespace)

    def test_list_tap_services(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns = self.cmd.take_action(parsed_args)[0]
        tap_services = \
            self.neutronclient.list_taas_tap_services()['tap_services']
        tap_service = tap_services[0]
        data = [
            tap_service['id'],
            tap_service['name'],
            tap_service['port']
        ]
        self.assertEqual(list(self.columns), columns)
        self.assertEqual(self.data, data)

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        tap_services = \
            self.neutronclient.list_taas_tap_services()['tap_services']
        tap_service = tap_services[0]
        data = [
            tap_service['id'],
            tap_service['name'],
            tap_service['port'],
            tap_service['description']
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns_long = self.cmd.take_action(parsed_args)[0]
        self.assertEqual(list(self.columns_long), columns_long)
        self.assertEqual(self.data_long, data)


class TestSetTaasTapService(fakes.TestNeutronClientOSCV2):
    _tap_service = fakes.FakeTaasTapService.create_tap_service()
    _tap_service_name = _tap_service['name']
    _tap_service_id = _tap_service['id']

    def setUp(self):
        super(TestSetTaasTapService, self).setUp()
        mock.patch('neutronclient.osc.v2.taas.taas_tap_service._get_id',
                   new=_get_id).start()
        self.neutronclient.update_taas_tap_service = mock.Mock(
            return_value=None)
        self.cmd = taas_tap_service.SetTaasTapService(self.app, self.namespace)

    def test_set_tap_service(self):
        client = self.app.client_manager.neutronclient
        mock_tap_service_update = client.update_taas_tap_service
        arglist = [
            self._tap_service_name,
            '--name', 'name_updated',
            '--description', 'desc_updated'
        ]
        verifylist = [
            ('tap_service', self._tap_service_name),
            ('name', 'name_updated'),
            ('description', 'desc_updated'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {'tap_service': {
            'name': 'name_updated',
            'description': 'desc_updated'}
        }
        mock_tap_service_update.assert_called_once_with(self._tap_service_name,
                                                        attrs)
        self.assertIsNone(result)


class TestShowTaasTapService(fakes.TestNeutronClientOSCV2):

    _ts = fakes.FakeTaasTapService.create_tap_service()

    data = (
        _ts['description'],
        _ts['id'],
        _ts['name'],
        _ts['project_id'],
        _ts['port'],
    )
    _tap_service = {'tap_service': _ts}
    _tap_service_id = _ts['id']
    columns = (
        'Description',
        'ID',
        'Name',
        'Project',
        'Tap Service Port',
    )

    def setUp(self):
        super(TestShowTaasTapService, self).setUp()
        mock.patch('neutronclient.osc.v2.taas.taas_tap_service._get_id',
                   new=_get_id).start()

        self.neutronclient.show_taas_tap_service = mock.Mock(
            return_value=self._tap_service
        )

        # Get the command object to test
        self.cmd = taas_tap_service.ShowTaasTapService(self.app,
                                                       self.namespace)

    def test_show_tap_service(self):
        client = self.app.client_manager.neutronclient
        mock_tap_service_show = client.show_taas_tap_service
        arglist = [
            self._tap_service_id,
        ]
        verifylist = [
            ('tap_service', self._tap_service_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        mock_tap_service_show.assert_called_once_with(self._tap_service_id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
