import graphene
from graphene_django import DjangoObjectType

from tests.models import Blog, BlogPost


class BlogType(DjangoObjectType):
    class Meta:
        model = Blog
        interfaces = [graphene.Node]
        only_fields = (
            'title',
            'description',
            'posts',
        )


class BlogPostType(DjangoObjectType):
    class Meta:
        model = BlogPost
        interfaces = [graphene.Node]
        only_fields = (
            'title',
            'body',
            'blog',
        )
