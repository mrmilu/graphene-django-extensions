import json

from django.test import TestCase

from graphql_relay import to_global_id

from tests.models import Blog, BlogPost


class ArgumentTests(TestCase):
    def setUp(self):
        self.blog1 = Blog.objects.create(title='Blog 1', description='Description 1', enabled=False)
        self.blog2 = Blog.objects.create(title='Blog 2', description='Description 2')
        self.blog3 = Blog.objects.create(title='Blog 3', description='Description 3')

        self.blog1_post1 = BlogPost.objects.create(title='Blog 1 - Post 1', body='Body 1 - 1', blog=self.blog1)
        self.blog1_post2 = BlogPost.objects.create(title='Blog 1 - Post 2', body='Body 1 - 2', blog=self.blog1)
        self.blog2_post1 = BlogPost.objects.create(title='Blog 2 - Post 1', body='Body 2 - 1', blog=self.blog2)
        self.blog2_post2 = BlogPost.objects.create(title='Blog 2 - Post 2', body='Body 2 - 2', blog=self.blog2)

    def run_gql(self, query, variables=None):
        data = {
            'query': query,
        }
        if variables:
            data['variables'] = json.dumps(variables)
        return self.client.post('/graphql/', data)

    def print_json(self, data):
        print(json.dumps(data, indent=4))
        self.assertTrue(False)

    def test_setUp(self):
        self.assertEqual(Blog.objects.all().count(), 3)
        self.assertEqual(BlogPost.objects.all().count(), 4)
        self.assertEqual(BlogPost.objects.filter(blog=self.blog1).count(), 2)
        self.assertEqual(BlogPost.objects.filter(blog=self.blog2).count(), 2)
        self.assertEqual(BlogPost.objects.filter(blog=self.blog3).count(), 0)

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
        # self.print_json(response.json())

    def test_int_argument(self):
        query = '''
        query ($myArgument: Int) {
            allBlogs(myArgument: $myArgument) {
                edges {
                    node {
                        id
                        title
                    }
                }
            }
        }
        '''
        response = self.run_gql(query, {
            "myArgument": 1,
        })
        self.assertEqual(response.status_code, 200)

        response = self.run_gql(query, {
            "myArgument": 'test',
        })
        self.assertEqual(response.status_code, 400)

    def test_string_filter_simple(self):
        query = '''
        {{
            allBlogs(title: "{0}") {{
                edges {{
                    node {{
                        id
                        title
                    }}
                }}
            }}
        }}
        '''
        response = self.run_gql(query.format('Blog 1'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog1.pk))

        response = self.run_gql(query.format('Blog 2'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog2.pk))

        response = self.run_gql(query.format('Blog 3'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog3.pk))

        response = self.run_gql(query.format('Blog 4'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 0)

    def test_string_filter_with_field_title(self):
        query = '''
        {{
            allBlogs(titleFilterWithFieldName: "{0}") {{
                edges {{
                    node {{
                        id
                        title
                    }}
                }}
            }}
        }}
        '''
        response = self.run_gql(query.format('Blog 1'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog1.pk))

        response = self.run_gql(query.format('Blog 2'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog2.pk))

        response = self.run_gql(query.format('Blog 4'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 0)

    def test_string_filter_when_exact_is_always_the_first(self):
        query = '''
        {{
            allBlogs(filterByDescription: "{0}") {{
                edges {{
                    node {{
                        id
                        title
                    }}
                }}
            }}
        }}
        '''
        response = self.run_gql(query.format('Description 1'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog1.pk))

        response = self.run_gql(query.format('description 1'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 0)

        response = self.run_gql(query.format('Description 2'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog2.pk))

        response = self.run_gql(query.format('description 2'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 0)

        response = self.run_gql(query.format('Description 4'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 0)

        query = '''
        {{
            allBlogs(filterByDescription_Iexact: "{0}") {{
                edges {{
                    node {{
                        id
                        title
                    }}
                }}
            }}
        }}
        '''
        response = self.run_gql(query.format('description 1'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog1.pk))

        response = self.run_gql(query.format('DESCRiption 2'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog2.pk))

        response = self.run_gql(query.format('description 4'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 0)

    def test_string_filter_relation(self):
        query = '''
        {{
            allBlogPosts(blog_Title: "{0}") {{
                edges {{
                    node {{
                        id
                        title
                    }}
                }}
            }}
        }}
        '''
        response = self.run_gql(query.format('Blog 1'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogPosts']['edges']), 2)
        self.assertEqual(data['data']['allBlogPosts']['edges'][0]['node']['id'], to_global_id('BlogPostType', self.blog1_post1.pk))
        self.assertEqual(data['data']['allBlogPosts']['edges'][1]['node']['id'], to_global_id('BlogPostType', self.blog1_post2.pk))

        response = self.run_gql(query.format('Blog 2'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogPosts']['edges']), 2)
        self.assertEqual(data['data']['allBlogPosts']['edges'][0]['node']['id'], to_global_id('BlogPostType', self.blog2_post1.pk))
        self.assertEqual(data['data']['allBlogPosts']['edges'][1]['node']['id'], to_global_id('BlogPostType', self.blog2_post2.pk))

        response = self.run_gql(query.format('Blog 3'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogPosts']['edges']), 0)

    def test_string_filter_relation_with_field_title_and_path(self):
        query = '''
        {{
            allBlogPosts(blogTitleFilterWithFieldNameAndPath: "{0}") {{
                edges {{
                    node {{
                        id
                        title
                    }}
                }}
            }}
        }}
        '''
        response = self.run_gql(query.format('Blog 1'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogPosts']['edges']), 2)
        self.assertEqual(data['data']['allBlogPosts']['edges'][0]['node']['id'], to_global_id('BlogPostType', self.blog1_post1.pk))
        self.assertEqual(data['data']['allBlogPosts']['edges'][1]['node']['id'], to_global_id('BlogPostType', self.blog1_post2.pk))

        response = self.run_gql(query.format('Blog 2'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogPosts']['edges']), 2)
        self.assertEqual(data['data']['allBlogPosts']['edges'][0]['node']['id'], to_global_id('BlogPostType', self.blog2_post1.pk))
        self.assertEqual(data['data']['allBlogPosts']['edges'][1]['node']['id'], to_global_id('BlogPostType', self.blog2_post2.pk))

        response = self.run_gql(query.format('Blog 3'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogPosts']['edges']), 0)

    def test_string_filter_relation_with_field_title(self):
        query = '''
        {{
            allBlogPosts(blogTitleFilterWithFieldName: "{0}") {{
                edges {{
                    node {{
                        id
                        title
                    }}
                }}
            }}
        }}
        '''
        response = self.run_gql(query.format('Blog 1'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogPosts']['edges']), 2)
        self.assertEqual(data['data']['allBlogPosts']['edges'][0]['node']['id'], to_global_id('BlogPostType', self.blog1_post1.pk))
        self.assertEqual(data['data']['allBlogPosts']['edges'][1]['node']['id'], to_global_id('BlogPostType', self.blog1_post2.pk))

        response = self.run_gql(query.format('Blog 2'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogPosts']['edges']), 2)
        self.assertEqual(data['data']['allBlogPosts']['edges'][0]['node']['id'], to_global_id('BlogPostType', self.blog2_post1.pk))
        self.assertEqual(data['data']['allBlogPosts']['edges'][1]['node']['id'], to_global_id('BlogPostType', self.blog2_post2.pk))

        response = self.run_gql(query.format('Blog 3'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogPosts']['edges']), 0)

    def test_filter_with_of_type(self):
        query = '''
        {{
            allBlogs(enabled: {0}) {{
                edges {{
                    node {{
                        id
                        title
                    }}
                }}
            }}
        }}
        '''
        response = self.run_gql(query.format('true'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 2)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog2.pk))
        self.assertEqual(data['data']['allBlogs']['edges'][1]['node']['id'], to_global_id('BlogType', self.blog3.pk))

        response = self.run_gql(query.format('false'))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog1.pk))

    def test_filter_method(self):
        query = '''
        {{
            allBlogs(count: {0}) {{
                edges {{
                    node {{
                        id
                        title
                    }}
                }}
            }}
        }}
        '''
        response = self.run_gql(query.format(0))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog3.pk))

        response = self.run_gql(query.format(2))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 2)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog1.pk))
        self.assertEqual(data['data']['allBlogs']['edges'][1]['node']['id'], to_global_id('BlogType', self.blog2.pk))

    def test_filter_subclass(self):
        query = '''
        {{
            allBlogs(filterByCount: {0}) {{
                edges {{
                    node {{
                        id
                        title
                    }}
                }}
            }}
        }}
        '''
        response = self.run_gql(query.format(0))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog3.pk))

        response = self.run_gql(query.format(2))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 2)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog1.pk))
        self.assertEqual(data['data']['allBlogs']['edges'][1]['node']['id'], to_global_id('BlogType', self.blog2.pk))

    def test_filter_method_and_lookup(self):
        query = '''
        {{
            allBlogs(count_Gte: {0}) {{
                edges {{
                    node {{
                        id
                        title
                    }}
                }}
            }}
        }}
        '''
        response = self.run_gql(query.format(0))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 3)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog1.pk))
        self.assertEqual(data['data']['allBlogs']['edges'][1]['node']['id'], to_global_id('BlogType', self.blog2.pk))
        self.assertEqual(data['data']['allBlogs']['edges'][2]['node']['id'], to_global_id('BlogType', self.blog3.pk))

        response = self.run_gql(query.format(1))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 2)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog1.pk))
        self.assertEqual(data['data']['allBlogs']['edges'][1]['node']['id'], to_global_id('BlogType', self.blog2.pk))

        response = self.run_gql(query.format(2))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 2)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog1.pk))
        self.assertEqual(data['data']['allBlogs']['edges'][1]['node']['id'], to_global_id('BlogType', self.blog2.pk))

        response = self.run_gql(query.format(3))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 0)

    def test_filter_subclass_with_lookup(self):
        query = '''
        {{
            allBlogs(filterByCount_Gte: {0}) {{
                edges {{
                    node {{
                        id
                        title
                    }}
                }}
            }}
        }}
        '''
        response = self.run_gql(query.format(0))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 3)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog1.pk))
        self.assertEqual(data['data']['allBlogs']['edges'][1]['node']['id'], to_global_id('BlogType', self.blog2.pk))
        self.assertEqual(data['data']['allBlogs']['edges'][2]['node']['id'], to_global_id('BlogType', self.blog3.pk))

        response = self.run_gql(query.format(1))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 2)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog1.pk))
        self.assertEqual(data['data']['allBlogs']['edges'][1]['node']['id'], to_global_id('BlogType', self.blog2.pk))

        response = self.run_gql(query.format(2))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 2)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog1.pk))
        self.assertEqual(data['data']['allBlogs']['edges'][1]['node']['id'], to_global_id('BlogType', self.blog2.pk))

        response = self.run_gql(query.format(3))
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 0)

    def test_multiple_filters(self):
        query = '''
        query ($enabled: Boolean, $title: String) {
            allBlogs(enabled: $enabled, title: $title) {
                edges {
                    node {
                        id
                        title
                    }
                }
            }
        }
        '''
        response = self.run_gql(query, {
            'enabled': False,
            'title': 'Blog 1',
        })
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog1.pk))

        response = self.run_gql(query, {
            'enabled': True,
            'title': 'Blog 2',
        })
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog2.pk))

        response = self.run_gql(query, {
            'enabled': True,
            'title': 'Blog 3',
        })
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 1)
        self.assertEqual(data['data']['allBlogs']['edges'][0]['node']['id'], to_global_id('BlogType', self.blog3.pk))

        response = self.run_gql(query, {
            'enabled': True,
            'title': 'Blog 1',
        })
        data = response.json()
        self.assertEqual(len(data['data']['allBlogs']['edges']), 0)
