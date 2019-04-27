from django.db.models import Q

import graphene


class Argument(object):
    name = None
    of_type = graphene.String()

    def __init__(self, name, of_type=None) -> None:
        super().__init__()
        self.name = name or self.name
        self.of_type = of_type or self.of_type

    def alter_queryset_before(self, queryset, name, value, info):
        return queryset

    def alter_queryset_after(self, queryset, name, value, info):
        return queryset

    def alter_filter_conditions(self, conditions, name, value, info):
        return conditions

    def get_value(self, name, value, info):
        return value

    def get_mapping(self):
        d = {}
        d[self.name] = self
        return d


class Filter(Argument):
    field_name = None
    path = None
    lookups = None

    def __init__(self, name, field_name=None, lookups=None, path=None, of_type=None) -> None:
        super().__init__(name, of_type=of_type)
        self.field_name = field_name or self.field_name
        self.path = path or self.path
        self.lookups = lookups or self.lookups

    def get_field_lookup(self, name, value, info):
        field_lookup = self.field_name or name
        if self.path:
            field_lookup = '{}__{}'.format(self.path, field_lookup)
        return field_lookup

    def alter_filter_conditions(self, conditions, name, value, info):
        field_lookup = self.get_field_lookup(name, value, info)
        condition = {}
        condition[field_lookup] = value
        q = Q(**condition)
        if conditions is None:
            return q
        return conditions & q
