#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from distutils.core import setup

# ref： http://docs.python.org/2/distutils/examples.html
setup(
    name='scrapydemo',
    version='1.2.0',
    # py_modules   = ['nester'],
    # package_dir  = {'': ''},
    packages=['scrapydemo'],
    author='hfpython',
    author_email='hfpython@headfirstlabs.com',
    url='http://www.headfirstlibs.com',
    description='A simple spider',
    requires=['scrapy', 'sqlalchemy', 'redis', 'psycopg2', 'MySQL-python', 'Pillow']
)