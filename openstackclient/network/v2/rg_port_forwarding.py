# Copyright (c) 2023 UnionTech
# All rights reserved
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
from osc_lib import utils
from osc_lib import exceptions
from osc_lib.command import command
from osc_lib.cli import format_columns

from openstackclient.i18n import _
from openstackclient.network import sdk_utils

LOG = logging.getLogger(__name__)

_formatters = {
    'location': format_columns.DictColumn,
}


def _get_columns(item):
    return sdk_utils.get_osc_show_columns_for_sdk_resource(
        item, dict(), invisible_columns=['name', 'location']
    )


class ListRGPortForwarding(command.Lister):
    _description = _("List router gateway port forwarding")

    def get_parser(self, prog_name):
        parser = super(ListRGPortForwarding, self).get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_("Router that the port forwarding belongs to (ID / Name)")
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            help=_("Filter the list result by the ID or name of "
                   "the internal network port")
        )
        parser.add_argument(
            '--external-protocol-port',
            metavar='<port-number>',
            dest='external_protocol_port',
            help=_("Filter the list result by the "
                   "protocol port number of the router gateway address")
        )
        parser.add_argument(
            '--protocol',
            metavar='protocol',
            help=_("Filter the list result by the port protocol")
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        columns = ('id',
                   'internal_port_id',
                   'internal_ip_address',
                   'internal_port',
                   'gw_ip_address',
                   'external_port',
                   'protocol',)
        headers = ('ID',
                   'Internal Port ID',
                   'Internal IP Address',
                   'Internal Port',
                   'Gateway IP Address',
                   'External Port',
                   'Protocol',)

        query = dict()

        if parsed_args.port:
            port = client.find_port(parsed_args.port,
                                    ignore_missing=False)
            query['internal_port_id'] = port.id
        if parsed_args.external_protocol_port is not None:
            query['external_port'] = parsed_args.external_protocol_port
        if parsed_args.protocol is not None:
            query['protocol'] = parsed_args.protocol

        obj = client.find_router(parsed_args.router, ignore_missing=False)

        data = client.router_gateway_port_forwardings(obj, **query)

        return (headers,
                (utils.get_item_properties(s, columns, formatters={}, )
                 for s in data))


class ShowRGPortForwarding(command.ShowOne):
    _description = _("Display router gateway port forwarding details")

    def get_parser(self, prog_name):
        parser = super(ShowRGPortForwarding, self).get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_("Router that the port forwarding belongs to (ID / Name)")
        )
        parser.add_argument(
            'port_forwarding_id',
            metavar="<port-forwarding-id>",
            help=_("The ID of the router gateway port forwarding")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        router = client.find_router(parsed_args.router, ignore_missing=False)
        obj = client.find_router_gateway_port_forwarding(
            router,
            parsed_args.port_forwarding_id,
            ignore_missing=False,
        )
        display_columns, columns = _get_columns(obj)
        print(display_columns, columns)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return display_columns, data


class CreateRGPortForwarding(command.ShowOne):
    _description = _("Create router gateway port forwarding")

    def get_parser(self, prog_name):
        parser = super(CreateRGPortForwarding, self).get_parser(prog_name)
        parser.add_argument(
            '--internal-ip-address',
            required=True,
            metavar='<internal-ip-address>',
            help=_("The fixed IPv4 address of the network "
                   "port associated to the router gateway port forwarding")
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            required=True,
            help=_("The name or ID of the network port associated "
                   "to the router gateway port forwarding")
        )
        parser.add_argument(
            '--internal-protocol-port',
            type=int,
            metavar='<port-number>',
            required=True,
            help=_("The protocol port number "
                   "of the network port fixed IPv4 address "
                   "associated to the router gateway port forwarding")
        )
        parser.add_argument(
            '--external-protocol-port',
            type=int,
            metavar='<port-number>',
            required=True,
            help=_("The protocol port number of "
                   "the port forwarding's router gateway address")
        )
        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            required=True,
            help=_("The protocol used in the router gateway "
                   "port forwarding, for instance: TCP, UDP")
        )
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_("Router that the port forwarding belongs to (ID / Name)")
        )
        return parser

    def take_action(self, parsed_args):
        attrs = {}
        client = self.app.client_manager.network
        router = client.find_router(parsed_args.router, ignore_missing=False)

        if parsed_args.internal_protocol_port is not None:
            if (parsed_args.internal_protocol_port <= 0 or
                    parsed_args.internal_protocol_port > 65535):
                msg = _("The port number range is <1-65535>")
                raise exceptions.CommandError(msg)
            attrs['internal_port'] = parsed_args.internal_protocol_port

        if parsed_args.external_protocol_port is not None:
            if (parsed_args.external_protocol_port <= 0 or
                    parsed_args.external_protocol_port > 65535):
                msg = _("The port number range is <1-65535>")
                raise exceptions.CommandError(msg)
            attrs['external_port'] = parsed_args.external_protocol_port

        if parsed_args.port:
            port = client.find_port(parsed_args.port, ignore_missing=False)
            attrs['internal_port_id'] = port.id
        attrs['internal_ip_address'] = parsed_args.internal_ip_address
        attrs['protocol'] = parsed_args.protocol

        obj = client.create_router_gateway_port_forwarding(router.id, **attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return display_columns, data


class DeleteRGPortForwarding(command.Command):
    _description = _("Delete router gateway port forwarding")

    def get_parser(self, prog_name):
        parser = super(DeleteRGPortForwarding, self).get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_("Router that the port forwarding belongs to (ID / Name)")
        )
        parser.add_argument(
            'port_forwarding_id',
            nargs="+",
            metavar="<port-forwarding-id>",
            help=_("The ID of the router gateway port forwarding")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        router = client.find_router(parsed_args.router, ignore_missing=False)
        result = 0

        for port_forwarding_id in parsed_args.port_forwarding_id:
            try:
                client.delete_router_gateway_port_forwarding(
                    router.id, port_forwarding_id, ignore_missing=False,
                )
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete router gateway port forwarding "
                            "'%(port_forwarding_id)s': %(e)s"),
                          {'port_forwarding_id': port_forwarding_id, 'e': e})
        if result > 0:
            total = len(parsed_args.port_forwarding_id)
            msg = (_("%(result)s of %(total)s Port forwarding failed "
                     "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class SetRGPortForwarding(command.Command):
    _description = _("Set router gateway Port Forwarding Properties")

    def get_parser(self, prog_name):
        parser = super(SetRGPortForwarding, self).get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_("Router that the port forwarding belongs to (ID / Name)")
        )
        parser.add_argument(
            'port_forwarding_id',
            metavar="<port-forwarding-id>",
            help=_("The ID of the router gateway port forwarding")
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            help=_("The ID of the network port associated to "
                   "the router gateway port forwarding")
        )
        parser.add_argument(
            '--internal-ip-address',
            metavar='<internal-ip-address>',
            help=_("The fixed IPv4 address of the network port "
                   "associated to the router gateway port forwarding")
        )
        parser.add_argument(
            '--internal-protocol-port',
            metavar='<port-number>',
            type=int,
            help=_("The TCP/UDP/other protocol port number of the "
                   "network port fixed IPv4 address associated to "
                   "the router gateway port forwarding")
        )
        parser.add_argument(
            '--external-protocol-port',
            type=int,
            metavar='<port-number>',
            help=_("The TCP/UDP/other protocol port number of the "
                   "port forwarding's router gateway address")
        )
        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            choices=['tcp', 'udp'],
            help=_("The IP protocol used in the "
                   "router gateway port forwarding")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        router = client.find_router(parsed_args.router, ignore_missing=False)

        attrs = {}
        if parsed_args.port:
            port = client.find_port(parsed_args.port, ignore_missing=False)
            attrs['internal_port_id'] = port.id

        if parsed_args.internal_ip_address:
            attrs['internal_ip_address'] = parsed_args.internal_ip_address
        if parsed_args.internal_protocol_port is not None:
            if (parsed_args.internal_protocol_port <= 0 or
                    parsed_args.internal_protocol_port > 65535):
                msg = _("The port number range is <1-65535>")
                raise exceptions.CommandError(msg)
            attrs['internal_port'] = parsed_args.internal_protocol_port

        if parsed_args.external_protocol_port is not None:
            if (parsed_args.external_protocol_port <= 0 or
                    parsed_args.external_protocol_port > 65535):
                msg = _("The port number range is <1-65535>")
                raise exceptions.CommandError(msg)
            attrs['external_port'] = parsed_args.external_protocol_port

        if parsed_args.protocol:
            attrs['protocol'] = parsed_args.protocol

        client.update_router_gateway_port_forwarding(
            router.id, parsed_args.port_forwarding_id, **attrs
        )