import json

from django.test import TestCase

from tests.models import Blog, BlogPost


class ArgumentTests(TestCase):
    def setUp(self):
        self.blog1 = Blog.objects.create(name='Blog 1', description='Description 1')
        self.blog2 = Blog.objects.create(name='Blog 2', description='Description 2')

        self.blog1_post1 = BlogPost.objects.create(name='Blog 1 - Post 1', body='Body 1 - 1', blog=self.blog1)
        self.blog1_post2 = BlogPost.objects.create(name='Blog 1 - Post 2', body='Body 1 - 2', blog=self.blog1)
        self.blog2_post1 = BlogPost.objects.create(name='Blog 2 - Post 1', body='Body 2 - 1', blog=self.blog2)
        self.blog2_post2 = BlogPost.objects.create(name='Blog 2 - Post 2', body='Body 2 - 2', blog=self.blog2)

    def run_gql(self, query, variables=None):
        data = {
            'query': query,
        }
        if variables:
            data['variables'] = variables
        return self.client.post('/graphql/', data)

    def print_json(self, data):
        print(json.dumps(data, indent=4))
        self.assertTrue(False)

    def test_setUp(self):
        self.assertEqual(Blog.objects.all().count(), 2)
        self.assertEqual(BlogPost.objects.all().count(), 4)
        self.assertEqual(BlogPost.objects.filter(blog=self.blog1).count(), 2)
        self.assertEqual(BlogPost.objects.filter(blog=self.blog2).count(), 2)

    def test_schema(self):
        query = '''
        query IntrospectionQuery {
            __schema {
                queryType { name }
                mutationType { name }
                subscriptionType { name }
                types {
                    ...FullType
                }
                directives {
                    name
                    description
                    locations
                    args {
                        ...InputValue
                    }
                }
            }
        }
        fragment FullType on __Type {
            kind
            name
            description
            fields(includeDeprecated: true) {
                name
                description
                args {
                    ...InputValue
                }
                type {
                    ...TypeRef
                }
                isDeprecated
                deprecationReason
            }
            inputFields {
                ...InputValue
            }
            interfaces {
                ...TypeRef
            }
            enumValues(includeDeprecated: true) {
                name
                description
                isDeprecated
                deprecationReason
            }
            possibleTypes {
                ...TypeRef
            }
        }
        fragment InputValue on __InputValue {
            name
            description
            type {
                ...TypeRef
            }
            defaultValue
        }
        fragment TypeRef on __Type {
            kind
            name
            ofType {
                kind
                name
                ofType {
                    kind
                    name
                    ofType {
                        kind
                        name
                        ofType {
                            kind
                            name
                            ofType {
                                kind
                                name
                                ofType {
                                    kind
                                    name
                                    ofType {
                                        kind
                                        name
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        '''
        response = self.run_gql(query)
        self.assertEqual(response.status_code, 200)

    def test_text_filter_simple(self):
        query = '''
        {{
            allBlogs(name: "{0}") {{
                edges {{
                    cursor
                    node {{
                        name
                    }}
                }}
            }}
        }}
        '''
        response = self.run_gql(query.format('Blog 1'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)

        response = self.run_gql(query.format('Blog 2'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)

        response = self.run_gql(query.format('Blog 3'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 0)

    def test_text_filter_with_field_name(self):
        query = '''
        {{
            allBlogs(nameFilterWithFieldName: "{0}") {{
                edges {{
                    cursor
                    node {{
                        name
                    }}
                }}
            }}
        }}
        '''
        response = self.run_gql(query.format('Blog 1'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)

        response = self.run_gql(query.format('Blog 2'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)

        response = self.run_gql(query.format('Blog 3'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 0)

    def test_text_filter_relation_with_field_name_and_path(self):
        query = '''
        {{
            allBlogPosts(blogNameFilterWithFieldNameAndPath: "{0}") {{
                edges {{
                    cursor
                    node {{
                        name
                    }}
                }}
            }}
        }}
        '''
        response = self.run_gql(query.format('Blog 1'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogPosts']['edges']), 2)

        response = self.run_gql(query.format('Blog 2'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogPosts']['edges']), 2)

        response = self.run_gql(query.format('Blog 3'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogPosts']['edges']), 0)

    def test_text_filter_relation_with_field_name(self):
        query = '''
        {{
            allBlogPosts(blogNameFilterWithFieldName: "{0}") {{
                edges {{
                    cursor
                    node {{
                        name
                    }}
                }}
            }}
        }}
        '''
        response = self.run_gql(query.format('Blog 1'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogPosts']['edges']), 2)

        response = self.run_gql(query.format('Blog 2'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogPosts']['edges']), 2)

        response = self.run_gql(query.format('Blog 3'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogPosts']['edges']), 0)
