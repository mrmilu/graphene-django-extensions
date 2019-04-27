import graphene

from tests.graphql.types import BlogType, BlogPostType


class BlogConnection(graphene.Connection):
    class Meta:
        node = BlogType


class BlogPostConnection(graphene.Connection):
    class Meta:
        node = BlogPostType
