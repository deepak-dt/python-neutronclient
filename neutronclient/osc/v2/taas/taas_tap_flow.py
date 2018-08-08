# Copyright (c) 2018 AT&T Corporation.
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
from neutronclient.common import utils as neutronclient_utils
from neutronclient.osc import utils as column_util

LOG = logging.getLogger(__name__)

resource = 'tap_flow'

_attr_map = (
    ('id', 'ID', column_util.LIST_BOTH),
    ('name', 'Name', column_util.LIST_BOTH),
    ('status', 'Status', column_util.LIST_BOTH),
    ('port', 'Source Port', column_util.LIST_BOTH),
    ('tap_service', 'Tap Service Port', column_util.LIST_BOTH),
    ('direction', 'Direction', column_util.LIST_BOTH),
    ('description', 'Description', column_util.LIST_LONG_ONLY),
    ('project_id', 'Project', column_util.LIST_LONG_ONLY),
)


class CreateTaasTapFlow(command.ShowOne):
    _description = _("Create a Tap Flow")

    def get_parser(self, prog_name):
        parser = super(CreateTaasTapFlow, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of the tap flow'))
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description for the tap flow'))
        parser.add_argument(
            '--port',
            dest='source_port',
            required=True,
            metavar='<port>',
            help=_('Source port to which the Tap Flow is connected.'))
        parser.add_argument(
            '--tap-service',
            dest='tap_service_id',
            required=True,
            metavar='<tap_service>',
            help=_('Tap Service to which the Tap Flow belongs.'))
        parser.add_argument(
            '--direction',
            required=True,
            metavar='<direction>',
            choices=['IN', 'OUT', 'BOTH'],
            type=neutronclient_utils.convert_to_uppercase,
            help=_('Direction of the Tap flow.'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        attrs = _get_common_attrs(self.app.client_manager, parsed_args)
        body = {resource: attrs}
        obj = client.create_taas_tap_flow(body)[resource]
        columns, display_columns = column_util.get_columns(obj, _attr_map)
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteTaasTapFlow(command.Command):
    _description = _("Delete a given tap flow")

    def get_parser(self, prog_name):
        parser = super(DeleteTaasTapFlow, self).get_parser(prog_name)
        parser.add_argument(
            'tap_flow',
            metavar="<tap-flow>",
            help=_("tap flow to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        # TODO(deepak): Add support for deleting multiple resources.
        client = self.app.client_manager.neutronclient
        tap_flow_id = _get_id(client, parsed_args.tap_flow, resource)
        try:
            client.delete_taas_tap_flow(tap_flow_id)
        except Exception as e:
            msg = (_("Failed to delete tap flow with name "
                     "or ID '%(tap_flow)s': %(e)s")
                   % {'tap_flow': parsed_args.tap_flow, 'e': e})
            raise exceptions.CommandError(msg)


class ListTaasTapFlow(command.Lister):
    _description = _("List tap flows")

    def get_parser(self, prog_name):
        parser = super(ListTaasTapFlow, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        data = client.list_taas_tap_flows()
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=parsed_args.long)
        return (headers,
                (utils.get_dict_properties(
                    s, columns,
                ) for s in data['tap_flows']))


class SetTaasTapFlow(command.Command):
    _description = _("Set tap flow properties")

    def get_parser(self, prog_name):
        parser = super(SetTaasTapFlow, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of the tap flow'))
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description for the tap flow'))
        parser.add_argument(
            'tap_flow',
            metavar='<tap-flow>',
            help=_("tap flow to modify (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        tap_flow_id = _get_id(client, parsed_args.tap_flow, resource)
        attrs = _get_common_attrs(self.app.client_manager, parsed_args,
                                  is_create=False)
        body = {resource: attrs}
        try:
            client.update_taas_tap_flow(tap_flow_id, body)
        except Exception as e:
            msg = (_("Failed to update tap flow '%(tap_flow)s': %(e)s")
                   % {'tap_flow': parsed_args.tap_flow, 'e': e})
            raise exceptions.CommandError(msg)


class ShowTaasTapFlow(command.ShowOne):
    _description = _("Display tap flow details")

    def get_parser(self, prog_name):
        parser = super(ShowTaasTapFlow, self).get_parser(prog_name)
        parser.add_argument(
            'tap_flow',
            metavar='<tap-flow>',
            help=_("tap flow to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        tap_flow_id = _get_id(client, parsed_args.tap_flow, resource)
        obj = client.show_taas_tap_flow(tap_flow_id)[resource]
        columns, display_columns = column_util.get_columns(obj, _attr_map)
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


def _get_common_attrs(client_manager, parsed_args, is_create=True):
    attrs = {}
    if parsed_args.name is not None:
        attrs['name'] = parsed_args.name
    if parsed_args.description is not None:
        attrs['description'] = parsed_args.description
    if is_create:
        _get_attrs(client_manager, attrs, parsed_args)
    return attrs


def _get_attrs(client_manager, attrs, parsed_args):
    if parsed_args.source_port is not None:
        attrs['source_port'] = _get_id(client_manager.neutronclient,
                                       parsed_args.source_port, 'port')
    if parsed_args.tap_service_id is not None:
        attrs['tap_service_id'] = _get_id(client_manager.neutronclient,
                                          parsed_args.tap_service_id,
                                          'tap_service')
    if parsed_args.direction is not None:
        attrs['direction'] = parsed_args.direction


def _get_id(client, id_or_name, resource):
    return client.find_resource(resource, id_or_name)['id']
