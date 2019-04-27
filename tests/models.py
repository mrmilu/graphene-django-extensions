from __future__ import unicode_literals

from django.db import models


class TestModel(models.Model):
    """
    Base for test models that sets app_label, so they play nicely.
    """

    class Meta:
        app_label = 'tests'
        abstract = True


class Blog(TestModel):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    enabled = models.BooleanField(default=True)


class BlogPost(TestModel):
    title = models.CharField(max_length=255)
    body = models.TextField(null=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='posts')
