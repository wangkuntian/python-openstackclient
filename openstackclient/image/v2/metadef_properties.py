# Copyright 2023 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


def _format_property(prop):
    prop = prop.to_dict(ignore_none=True, original_names=True)
    return {
        key: prop[key]
        for key in [
            'namespace_name',
            'name',
            'type',
            'title',
            'description',
            'operators',
            'default',
            'is_readonly',
            'minimum',
            'maximum',
            'enum',
            'pattern',
            'min_length',
            'max_length',
            'items',
            'require_unique_items',
            'min_items',
            'max_items',
            'allow_additional_items',
        ]
        if key in prop
    }


class CreateMetadefProperty(command.ShowOne):
    _description = _("Create a metadef property")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--name",
            required=True,
            help=_("Internal name of the property"),
        )
        parser.add_argument(
            "--title",
            required=True,
            help=_("Property name displayed to the user"),
        )
        parser.add_argument(
            "--type",
            required=True,
            help=_("Property type"),
        )
        parser.add_argument(
            "--schema",
            required=True,
            help=_("Valid JSON schema of the property"),
        )
        parser.add_argument(
            "namespace_name",
            help=_("Name of namespace the property will belong."),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        kwargs = {
            'name': parsed_args.name,
            'title': parsed_args.title,
            'type': parsed_args.type,
        }
        try:
            kwargs.update(json.loads(parsed_args.schema))
        except json.JSONDecodeError as e:
            raise exceptions.CommandError(
                _("Failed to load JSON schema: %(e)s")
                % {
                    'e': e,
                }
            )

        data = image_client.create_metadef_property(
            parsed_args.namespace_name, **kwargs
        )
        info = _format_property(data)

        return zip(*sorted(info.items()))


class DeleteMetadefProperty(command.Command):
    _description = _("Delete a metadef property")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace_name",
            help=_("An identifier (a name) for the namespace"),
        )
        parser.add_argument(
            "property_name",
            help=_("Property to delete"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        try:
            image_client.delete_metadef_property(
                parsed_args.property_name,
                parsed_args.namespace_name,
                ignore_missing=False,
            )
        except Exception as e:
            raise exceptions.CommandError(
                _(
                    "Failed to delete property with name or "
                    "ID '%(property)s' from namespace '%(namespace)s': %(e)s"
                )
                % {
                    'property': parsed_args.property_name,
                    'namespace': parsed_args.namespace_name,
                    'e': e,
                }
            )


class ListMetadefProperties(command.Lister):
    _description = _("List metadef properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace_name",
            metavar="<namespace_name>",
            help=_("An identifier (a name) for the namespace"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        props = image_client.metadef_properties(parsed_args.namespace_name)
        columns = ['name', 'title', 'type']
        return (
            columns,
            (
                utils.get_item_properties(
                    prop,
                    columns,
                )
                for prop in props
            ),
        )


class SetMetadefProperty(command.Command):
    _description = _("Update metadef namespace property")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--name",
            help=_("Internal name of the property"),
        )
        parser.add_argument(
            "--title",
            help=_("Property name displayed to the user"),
        )
        parser.add_argument(
            "--type",
            help=_("Property type"),
        )
        parser.add_argument(
            "--schema",
            help=_("Valid JSON schema of the property"),
        )
        parser.add_argument(
            "namespace_name",
            help=_("Namespace of the namespace to which the property belongs"),
        )
        parser.add_argument(
            "property_name",
            help=_("Property to update"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        # We need to pass the values for *all* attributes as kwargs to
        # update_metadef_property(), otherwise the attributes that are not
        # listed will be reset.
        data = image_client.get_metadef_property(
            parsed_args.property_name, parsed_args.namespace_name
        )
        kwargs = _format_property(data)
        for key in ['name', 'title', 'type']:
            argument = getattr(parsed_args, key, None)
            if argument is not None:
                kwargs[key] = argument

        if parsed_args.schema:
            try:
                kwargs.update(json.loads(parsed_args.schema))
            except json.JSONDecodeError as e:
                raise exceptions.CommandError(
                    _("Failed to load JSON schema: %(e)s")
                    % {
                        'e': e,
                    }
                )

        image_client.update_metadef_property(
            parsed_args.property_name, parsed_args.namespace_name, **kwargs
        )


class ShowMetadefProperty(command.ShowOne):
    _description = _("Describe a specific property from a namespace")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace_name",
            metavar="<namespace_name>",
            help=_("Namespace (name) for the namespace"),
        )
        parser.add_argument(
            "property_name",
            metavar="<property_name>",
            help=_("Property to show"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        data = image_client.get_metadef_property(
            parsed_args.property_name, parsed_args.namespace_name
        )
        info = _format_property(data)

        return zip(*sorted(info.items()))
