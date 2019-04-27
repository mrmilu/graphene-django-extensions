from graphene_django_helpers import fields

from graphene_django_helpers import arguments


class BlogField(fields.ConnectionFieldWithArguments):
    arguments = [
        arguments.Filter('name'),
        arguments.Filter('name_filter_with_field_name', field_name='name'),
    ]


class BlogPostField(fields.ConnectionFieldWithArguments):
    arguments = [
        arguments.Filter('name'),
        arguments.Filter('blog__name'),
        arguments.Filter('blog_name_filter_with_field_name', field_name='blog__name'),
        arguments.Filter('blog_name_filter_with_field_name_and_path', field_name='name', path='blog'),
        # arguments.Filter('name', lookups=['exact']),
    ]
