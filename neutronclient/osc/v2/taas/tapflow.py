# Copyright (c) 2018 AT&T Corporation.
# Copyright (c) 2016 NEC Technologies India Pvt.Limited.
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

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from neutronclient._i18n import _
from neutronclient.common import utils as n_utils

LOG = logging.getLogger(__name__)

resource = 'tap_flow'


def _add_updatable_args(parser):
    parser.add_argument(
        '--name',
        help=_('Name of the Tap flow.'))
    parser.add_argument(
        '--description',
        help=_('Description for the Tap flow.'))


def _get_columns(item):
    return tuple(sorted(list(item.keys())))


def _update_common_attrs(parsed_args, attrs):
    if parsed_args.name:
        attrs['name'] = parsed_args.name
    if parsed_args.description:
        attrs['description'] = parsed_args.description


class CreateTapFlow(command.ShowOne):
    """Create a new tap flow"""

    def get_parser(self, prog_name):
        parser = super(CreateTapFlow, self).get_parser(prog_name)
        _add_updatable_args(parser)
        parser.add_argument(
            '--port',
            help=_('Source port to which the Tap Flow is connected '
                   '(name or ID)'))
        parser.add_argument(
            '--tap-service',
            help=_('Tap Service with which the tap flow is associated '
                   '(name or ID)'))
        parser.add_argument(
            '--direction',
            required=True,
            choices=['IN', 'OUT', 'BOTH'],
            type=n_utils.convert_to_uppercase,
            help=_('Direction of the packet flow which needs to be mirrored '
                   'by the tapflow'))
        parser.add_argument(
            '--vlan-filter',
            required=False,
            metavar='<vlan_filter>',
            type=n_utils.convert_to_uppercase,
            help=_('VLAN Ids to be mirrored in the form of range string.'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        source_port = _get_id(client, parsed_args.port, 'port')
        tap_service_id = _get_id(client, parsed_args.tap_service,
                                 'tap_service')
        attrs = {'source_port': source_port,
                 'tap_service_id': tap_service_id}
        _update_common_attrs(parsed_args, attrs)
        if parsed_args.direction:
            attrs['direction'] = parsed_args.direction
        if parsed_args.vlan_filter:
            attrs['vlan_filter'] = parsed_args.vlan_filter
        body = {resource: attrs}
        obj = client.create_ext(client.taas_tap_flows_path, body)[resource]
        columns = _get_columns(obj)
        data = utils.get_dict_properties(obj, columns)
        return columns, data


class DeleteTapFlow(command.Command):
    """Delete tap flow(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteTapFlow, self).get_parser(prog_name)
        parser.add_argument(
            'tap_flow',
            nargs='+',
            help=_("Tap Flow to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        result = 0
        client = self.app.client_manager.neutronclient
        for tap_flow in parsed_args.tap_flow:
            try:
                id = _get_id(client, tap_flow, resource)
                client.delete_ext(client.taas_tap_flow_path, id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete tap flow with "
                            "name or ID '%(tap_flow)s': %(e)s"),
                          {'tap_flow': tap_flow, 'e': e})

        if result > 0:
            total = len(parsed_args.tap_flow)
            msg = (_("%(result)s of %(total)s tap flows were failed "
                   "to be deleted.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ShowTapFlow(command.ShowOne):
    """Display tap flow details"""

    def get_parser(self, prog_name):
        parser = super(ShowTapFlow, self).get_parser(prog_name)
        parser.add_argument(
            'tap_flow',
            help=_("ID or name of the Tap Flow to display")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        id = _get_id(client, parsed_args.tap_flow, resource)
        obj = client.show_ext(client.taas_tap_flow_path, id)[resource]
        columns = _get_columns(obj)
        data = utils.get_dict_properties(obj, columns)
        return columns, data


class SetTapFlow(command.Command):
    """Set tap flow properties"""

    def get_parser(self, prog_name):
        parser = super(SetTapFlow, self).get_parser(prog_name)
        _add_updatable_args(parser)
        parser.add_argument(
            'tap_flow',
            help=_("Tap Flow to modify (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        attrs = {}
        client = self.app.client_manager.neutronclient
        id = _get_id(client, parsed_args.tap_flow, resource)
        _update_common_attrs(parsed_args, attrs)
        body = {resource: attrs}
        try:
            client.update_ext(client.taas_tap_flow_path, id, body)
        except Exception as e:
            msg = (_("Failed to update tap flow '%(tap_flow)s': %(e)s")
                   % {'tap_flow': parsed_args.tap_flow, 'e': e})
            raise exceptions.CommandError(msg)


class ListTapFlow(command.Lister):
    """List tap flows"""

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        data = client.list_ext('tap_flows',
                               client.taas_tap_flows_path,
                               retrieve_all=True)
        columns = ['id', 'name', 'source_port', 'status', 'tap_service_id',
                   'vlan_filter']
        headers = ('ID', 'Name', 'Source Port', 'Status', 'Tap Service',
                   'VLAN Filter')
        return (headers, (utils.get_dict_properties(
                          s, columns, ) for s in data['tap_flows']))


def _get_id(client, id_or_name, resource):
    return client.find_resource(resource, id_or_name)['id']