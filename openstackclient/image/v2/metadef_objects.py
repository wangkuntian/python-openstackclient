#   Copyright 2023 Red Hat
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
#

"""Image V2 Action Implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


def _format_object(md_object):
    fields_to_show = (
        'created_at',
        'description',
        'name',
        'namespace_name',
        'properties',
        'required',
        'updated_at',
    )

    return (
        fields_to_show,
        utils.get_item_properties(
            md_object,
            fields_to_show,
        ),
    )


class CreateMetadefObjects(command.ShowOne):
    _description = _("Create a metadef object")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--namespace",
            metavar="<namespace>",
            help=_("Metadef namespace to create the metadef object in (name)"),
        )
        parser.add_argument(
            "name",
            metavar='<metadef-object-name>',
            help=_('New metadef object name'),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        namespace = image_client.get_metadef_namespace(
            parsed_args.namespace,
        )
        data = image_client.create_metadef_object(
            namespace=namespace.namespace,
            name=parsed_args.name,
        )

        fields, value = _format_object(data)

        return fields, value


class ShowMetadefObjects(command.ShowOne):
    _description = _(
        "Describe a specific metadata definitions object inside a namespace"
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace_name",
            metavar="<namespace_name>",
            help=_("Namespace (name) for the namespace"),
        )
        parser.add_argument(
            "object_name",
            metavar="<object_name>",
            help=_("Name of an object."),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        namespace_name = parsed_args.namespace_name
        object_name = parsed_args.object_name

        data = image_client.get_metadef_object(object_name, namespace_name)

        fields, value = _format_object(data)

        return fields, value


class DeleteMetadefObject(command.Command):
    _description = _(
        "Delete a specific metadata definitions object inside a namespace"
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace_name",
            metavar="<namespace_name>",
            help=_("Namespace (name) for the namespace"),
        )
        parser.add_argument(
            "object_name",
            metavar="<object_name>",
            nargs="+",
            help=_("Name of an object."),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        namespace_name = parsed_args.namespace_name

        result = 0
        for i in parsed_args.object_name:
            try:
                object = image_client.get_metadef_object(i, namespace_name)
                image_client.delete_metadef_object(object, namespace_name)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete object with name or "
                        "ID '%(object)s': %(e)s"
                    ),
                    {'object': i, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.namespace_name)
            msg = _("%(result)s of %(total)s object failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListMetadefObjects(command.Lister):
    _description = _("List metadef objects inside a specific namespace.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace",
            metavar="<namespace>",
            help=_("Namespace (name) for the namespace"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        namespace_name = parsed_args.namespace
        columns = ['name', 'description']

        md_objects = list(image_client.metadef_objects(namespace_name))
        column_headers = columns
        return (
            column_headers,
            (
                utils.get_item_properties(
                    md_object,
                    columns,
                )
                for md_object in md_objects
            ),
        )
