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

LOG = logging.getLogger(__name__)

resource = 'tap_service'


def _add_updatable_args(parser):
    parser.add_argument(
        '--name',
        help=_('Name of this Tap service.'))
    parser.add_argument(
        '--description',
        help=_('Description for this Tap service.'))


def _get_columns(item):
    return tuple(sorted(list(item.keys())))


def _update_common_attrs(parsed_args, attrs):
    if parsed_args.name:
        attrs['name'] = parsed_args.name
    if parsed_args.description:
        attrs['description'] = parsed_args.description


class CreateTapService(command.ShowOne):
    """Create a new tap service"""

    def get_parser(self, prog_name):
        parser = super(CreateTapService, self).get_parser(prog_name)
        _add_updatable_args(parser)
        parser.add_argument(
            '--port',
            help=_('Port to which the Tap service is connected (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        port_id = _get_id(client, parsed_args.port, 'port')
        attrs = {'port_id': port_id}
        _update_common_attrs(parsed_args, attrs)
        body = {resource: attrs}
        obj = client.create_ext(client.taas_tap_services_path, body)[resource]
        columns = _get_columns(obj)
        data = utils.get_dict_properties(obj, columns)
        return columns, data


class DeleteTapService(command.Command):
    """Delete tap service(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteTapService, self).get_parser(prog_name)
        parser.add_argument(
            'tap_service',
            metavar="TAP_SERVICE",
            nargs='+',
            help=_("Tap Service(s) to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        result = 0
        client = self.app.client_manager.neutronclient
        for tap_service in parsed_args.tap_service:
            try:
                id = _get_id(client, tap_service, resource)
                client.delete_ext(client.taas_tap_service_path, id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete tap service with "
                            "name or ID '%(tap_service)s': %(e)s"),
                          {'tap_service': tap_service, 'e': e})

        if result > 0:
            total = len(parsed_args.tap_service)
            msg = (_("%(result)s of %(total)s tap services were failed "
                   "to be deleted.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ShowTapService(command.ShowOne):
    """Display tap service details"""

    def get_parser(self, prog_name):
        parser = super(ShowTapService, self).get_parser(prog_name)
        parser.add_argument(
            'tap_service',
            metavar="TAP_SERVICE",
            help=_("ID or name of the Tap Service to display")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        id = _get_id(client, parsed_args.tap_service, resource)
        obj = client.show_ext(client.taas_tap_service_path, id)[resource]
        columns = _get_columns(obj)
        data = utils.get_dict_properties(obj, columns)
        return columns, data


class SetTapService(command.Command):
    """Set tap service properties"""

    def get_parser(self, prog_name):
        parser = super(SetTapService, self).get_parser(prog_name)
        _add_updatable_args(parser)
        parser.add_argument(
            'tap_service',
            metavar="TAP_SERVICE",
            help=_("ID or name of the Tap Service to be set")
        )
        return parser

    def take_action(self, parsed_args):
        attrs = {}
        client = self.app.client_manager.neutronclient
        id = _get_id(client, parsed_args.tap_service, resource)
        _update_common_attrs(parsed_args, attrs)
        body = {resource: attrs}
        try:
            client.update_ext(client.taas_tap_service_path, id, body)
        except Exception as e:
            msg = (_("Failed to update tap service '%(tap_service)s': %(e)s")
                   % {'tap_service': parsed_args.tap_service, 'e': e})
            raise exceptions.CommandError(msg)


class ListTapService(command.Lister):
    """List tap services"""

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        data = client.list_ext('tap_services',
                               client.taas_tap_services_path,
                               retrieve_all=True)
        list_columns = ['id', 'name', 'port_id', 'status']
        headers = ('ID', 'Name', 'Port', 'Status')
        return (headers, (utils.get_dict_properties(
                          s, list_columns, ) for s in data['tap_services']))


def _get_id(client, id_or_name, resource):
    return client.find_resource(resource, id_or_name)['id']
