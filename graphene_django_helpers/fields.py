from functools import partial

from django.db.models import QuerySet

import graphene
from graphene import Field


class FieldWithArgumentsMixin(object):
    arguments = []

    def __init__(self, *args, **kwargs):
        self.argument_map = self.build_argument_map()
        for key, instance in self.argument_map.items():
            kwargs.setdefault(key, instance.of_type)
        super().__init__(*args, **kwargs)

    def build_argument_map(self):
        argument_map = {}
        for argument in self.arguments:
            argument_item_mapping = argument.get_mapping()
            if argument_item_mapping:
                argument_map.update(argument_item_mapping)

        return argument_map

    def get_argument_instances(self, **args):
        for key in args:
            argument_instance = self.argument_map.get(key, None)
            if argument_instance:
                yield key, argument_instance

    def alter_queryset_before(self, queryset, info, **args):
        for key, argument_instance in self.get_argument_instances(**args):
            queryset = argument_instance.alter_queryset_before(queryset, key, args[key], info)
        return queryset

    def alter_queryset_after(self, queryset, info, **args):
        for key, argument_instance in self.get_argument_instances(**args):
            queryset = argument_instance.alter_queryset_before(queryset, key, args[key], info)
        return queryset

    def alter_filter_conditions(self, conditions, info, **args):
        for key, argument_instance in self.get_argument_instances(**args):
            conditions = argument_instance.alter_filter_conditions(conditions, key, args[key], info)
        return conditions

    @classmethod
    def resolve_and_process_arguments(cls, root, info, parent_resolver=None, field_instance=None, **args):
        iterable = parent_resolver(root, info, **args)
        if field_instance and isinstance(iterable, QuerySet):
            iterable = field_instance.alter_queryset_before(iterable, info, **args)
            conditions = None
            conditions = field_instance.alter_filter_conditions(conditions, info, **args)
            if conditions:
                iterable = iterable.filter(conditions)
            iterable = field_instance.alter_queryset_after(iterable, info, **args)
        return iterable

    def get_resolver(self, parent_resolver):
        resolver = partial(self.resolve_and_process_arguments, parent_resolver=parent_resolver, field_instance=self)
        return super().get_resolver(resolver)


class FieldWithArguments(FieldWithArgumentsMixin, Field):
    pass


class ConnectionFieldWithArguments(FieldWithArgumentsMixin, graphene.relay.ConnectionField):
    pass
