from django.db.models import Q

import graphene


class Argument(object):
    name = None
    of_type = graphene.String()

    def __init__(self, name, of_type=None) -> None:
        super().__init__()
        self.name = name or self.name
        self.of_type = of_type or self.of_type

    def alter_queryset_before(self, field, queryset, params, value, info):
        return queryset

    def alter_queryset_after(self, field, queryset, params, value, info):
        return queryset

    def alter_filter_conditions(self, field, conditions, params, value, info):
        return conditions

    def get_mapping(self):
        d = {}
        d[self.name] = {
            'instance': self,
            'params': {
                'name': self.name,
            },
        }
        return d


class Filter(Argument):
    field_name = None
    path = None
    lookups = None

    def __init__(self, name, field_name=None, lookups=None, path=None, of_type=None, method=None) -> None:
        super().__init__(name, of_type=of_type)
        self.field_name = field_name or self.field_name
        self.path = path or self.path
        self.lookups = lookups or self.lookups
        self.method = method

    def get_field_lookup(self, field, params, value, info):
        ret = self.field_name or params['name']
        if self.path:
            ret = '{}__{}'.format(self.path, ret)
        lookup = params.get('lookup', None)
        if lookup:
            ret = '{}__{}'.format(ret, lookup)
        return ret

    def alter_filter_conditions(self, field, conditions, params, value, info):
        # This step does not run if method is provided
        if self.method:
            return conditions

        field_lookup = self.get_field_lookup(field, params, value, info)
        condition = {}
        condition[field_lookup] = value
        q = Q(**condition)
        if conditions is None:
            return q
        return conditions & q

    def get_processed_lookups(self):
        if self.lookups is None:
            return True, []

        lookups = list(self.lookups)
        exact_lookup_found = 'exact' in lookups
        if exact_lookup_found:
            lookups.remove('exact')
        return exact_lookup_found, lookups

    def alter_queryset_after(self, field, queryset, params, value, info):
        if self.method:
            queryset = getattr(field, self.method)(queryset, params, value, info)
        return queryset

    def get_mapping(self):
        d = {}

        exact_lookup_found, lookups = self.get_processed_lookups()

        d[self.name] = {
            'instance': self,
            'params': {
                'name': self.name,
                'lookup': lookups[0] if not exact_lookup_found and len(lookups) == 1 else None,
            },
        }

        if len(lookups) > 0:
            for lookup in lookups:
                key = '{}__{}'.format(self.name, lookup)
                d[key] = {
                    'instance': self,
                    'params': {
                        'name': self.name,
                        'lookup': lookup,
                    },
                }

        return d


class IntFilter(Filter):
    of_type = graphene.Int()


class FloatFilter(Filter):
    of_type = graphene.Float()


class BooleanFilter(Filter):
    of_type = graphene.Boolean()
