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
#from osc_lib.utils import columns as column_util

from neutronclient._i18n import _
from neutronclient.osc import utils as column_util

LOG = logging.getLogger(__name__)

resource = 'tap_service'

_attr_map = (
    ('id', 'ID', column_util.LIST_BOTH),
    ('name', 'Name', column_util.LIST_BOTH),
    ('status', 'Status', column_util.LIST_BOTH),
    ('port', 'Tap Service Port', column_util.LIST_BOTH),
    ('description', 'Description', column_util.LIST_LONG_ONLY),
    ('project_id', 'Project', column_util.LIST_LONG_ONLY),
)


class CreateTaasTapService(command.ShowOne):
    _description = _("Create a Tap Service")

    def get_parser(self, prog_name):
        parser = super(CreateTaasTapService, self).get_parser(prog_name)
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
            dest='port_id',
            required=True,
            metavar='<port>',
            help=_('Port to which the Tap service is connected.'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        attrs = _get_common_attrs(self.app.client_manager, parsed_args)
        body = {resource: attrs}
        obj = client.create_tap_service(body)[resource]
        columns, display_columns = column_util.get_columns(obj, _attr_map)
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteTaasTapService(command.Command):
    _description = _("Delete a given tap service")

    def get_parser(self, prog_name):
        parser = super(DeleteTaasTapService, self).get_parser(prog_name)
        parser.add_argument(
            'tap_service',
            metavar="<tap-service>",
            help=_("tap service to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        # TODO(deepak): Add support for deleting multiple resources.
        client = self.app.client_manager.neutronclient
        tap_service_id = _get_id(client, parsed_args.tap_service, resource)
        try:
            client.delete_tap_service(tap_service_id)
        except Exception as e:
            msg = (_("Failed to delete tap service with name "
                     "or ID '%(tap_service)s': %(e)s")
                   % {'tap_service': parsed_args.tap_service, 'e': e})
            raise exceptions.CommandError(msg)


class ListTaasTapService(command.Lister):
    _description = _("List tap services")

    def get_parser(self, prog_name):
        parser = super(ListTaasTapService, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        data = client.list_tap_services()
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=parsed_args.long)
        return (headers,
                (utils.get_dict_properties(
                    s, columns,
                ) for s in data['tap_services']))


class SetTaasTapService(command.Command):
    _description = _("Set tap service properties")

    def get_parser(self, prog_name):
        parser = super(SetTaasTapService, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of the tap service'))
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description for the tap service'))
        parser.add_argument(
            'tap_service',
            metavar='<tap-service>',
            help=_("tap service to modify (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        tap_service_id = _get_id(client, parsed_args.tap_service, resource)
        attrs = _get_common_attrs(self.app.client_manager, parsed_args,
                                  is_create=False)
        body = {resource: attrs}
        try:
            client.update_tap_service(tap_service_id, body)
        except Exception as e:
            msg = (_("Failed to update tap service '%(tap_service)s': %(e)s")
                   % {'tap_service': parsed_args.tap_service, 'e': e})
            raise exceptions.CommandError(msg)


class ShowTaasTapService(command.ShowOne):
    _description = _("Display tap service details")

    def get_parser(self, prog_name):
        parser = super(ShowTaasTapService, self).get_parser(prog_name)
        parser.add_argument(
            'tap_service',
            metavar='<tap-service>',
            help=_("tap service to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        tap_service_id = _get_id(client, parsed_args.tap_service, resource)
        obj = client.show_tap_service(tap_service_id)[resource]
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
    if parsed_args.port_id is not None:
        attrs['port_id'] = _get_id(client_manager.neutronclient,
                                   parsed_args.port_id, 'port')


def _get_id(client, id_or_name, resource):
    return client.find_resource(resource, id_or_name)['id']
