from django.db.models import Count

from graphene_django_helpers import arguments


class BlogPostCountFilter(arguments.IntFilter):
    field_name = 'blog_post_count'

    def alter_queryset_before(self, field, queryset, params, value, info):
        return queryset.annotate(blog_post_count=Count('posts'))
