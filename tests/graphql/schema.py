import graphene

from tests.graphql.connections import BlogConnection, BlogPostConnection
from tests.graphql.fields import BlogField, BlogPostField
from tests.graphql.types import BlogType, BlogPostType
from tests.models import Blog, BlogPost


class BlogQuery(graphene.ObjectType):
    all_blogs = BlogField(BlogConnection)
    all_blog_posts = BlogPostField(BlogPostConnection)

    def resolve_all_blogs(self, info, **kwargs):
        return Blog.objects.all()

    def resolve_all_blog_posts(self, info, **kwargs):
        return BlogPost.objects.all()


class Query(
    BlogQuery,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, types=[
    BlogType,
    BlogPostType,
])
