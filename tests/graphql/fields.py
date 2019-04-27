import graphene
from django.db.models import Count

from graphene_django_helpers import fields, arguments


class BlogField(fields.ConnectionFieldWithArguments):
    # @TODO - Be careful, name, description and type are protected names
    #  as long as we pass them as kwargs to graphene.Field
    arguments = [
        arguments.Filter('title'),
        arguments.Filter('title_filter_with_field_name', field_name='title'),
        arguments.Filter('filter_by_description', field_name='description', lookups=['iexact', 'exact']),
        arguments.Filter('enabled', of_type=graphene.Boolean()),
        arguments.IntFilter('count', method='filter_by_count', lookups=['exact', 'gte']),
    ]

    def filter_by_count(self, queryset, params, value, info):
        conditions = {}
        key = 'count__{}'.format(params['lookup']) if params['lookup'] else 'count'
        conditions[key] = value
        return queryset.annotate(count=Count('posts')).filter(**conditions)


class BlogPostField(fields.ConnectionFieldWithArguments):
    arguments = [
        arguments.Filter('title'),
        arguments.Filter('blog__title'),
        arguments.Filter('blog_title_filter_with_field_name', field_name='blog__title'),
        arguments.Filter('blog_title_filter_with_field_name_and_path', field_name='title', path='blog'),
    ]
