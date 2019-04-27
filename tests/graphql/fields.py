from graphene_django_helpers import fields, arguments


class BlogField(fields.ConnectionFieldWithArguments):
    # @TODO - Be careful, name, description and type are protected names
    #  as long as we pass them as kwargs to graphene.Field
    arguments = [
        arguments.Filter('title'),
        arguments.Filter('title_filter_with_field_name', field_name='title'),
        arguments.Filter('filter_by_description', field_name='description', lookups=['iexact', 'exact']),
    ]


class BlogPostField(fields.ConnectionFieldWithArguments):
    arguments = [
        arguments.Filter('title'),
        arguments.Filter('blog__title'),
        arguments.Filter('blog_title_filter_with_field_name', field_name='blog__title'),
        arguments.Filter('blog_title_filter_with_field_name_and_path', field_name='title', path='blog'),
    ]
