#   Copyright 2012-2013 OpenStack Foundation
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


from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


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