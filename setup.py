import os

from setuptools import setup


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


setup(
    name='graphene-django-helpers',
    version='0.0.1',
    description='graphene-django helpers: arguments, filter arguments, etc',
    url='https://github.com/mrmilu/graphene-django-helpers',
    author='Jaime Herencia',
    author_email='jherencia@mrmilu.com',
    license='MIT',
    packages=get_packages('graphene_django_helpers'),
    install_requires=[
        'django',
        'graphene_django',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
    python_requires='>=3.6',
    zip_safe=False
)
