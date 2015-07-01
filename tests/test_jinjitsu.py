#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_jinjitsu
----------------------------------

Tests for `jinjitsu` module.
"""

import unittest

from jinjitsu import jinjitsu
from jinja2.environment import Environment
from jinja2.loaders import PackageLoader

class TestClass(object):
    name = "tpayne"
    def __init__(self):
        self.name = "tpayne2"


class TestJinjitsu(unittest.TestCase):

    def setUp(self):
        self.jinja_env = Environment(extensions=[
                                                'jinjitsu.display.DisplayExtension',
                                                'jinja2.ext.WithExtension'
                                                ],
                                     loader=PackageLoader('tests'))
        print(self.jinja_env.list_templates())


    def test_something(self):
        template = self.jinja_env.select_template(['badtest.html', 'test2.html', 'test.html'])
        template2 = self.jinja_env.select_template(['test.html'])
        output = template2.render(testobj=TestClass())
        #self.assertEqual(output, "Hellow")
        print(template2.render(testobj=TestClass()))

    def test_list(self):
        template = self.jinja_env.from_string(
        """
        {% display listobj as table%}
        """)
        output = template.render(listobj=[1, 2], display_fields=lambda x: [{'name': 'thomas', 'formatValue': lambda y: y}])
        print(output)

    def test_list_with(self):
        template = self.jinja_env.from_string(
        """
        {% display listobj as table with "name"%}
        """)
        output = template.render(listobj=[{'name': 'thomas'}, {'name': 'bob'}])
        print(output)

    def test_getattr(self):
        template = self.jinja_env.from_string(
        """
        {% display dictobj.name %}
        """)
        output = template.render(dictobj={'name': 'thomas'})
        print(output)

    def test_getitem(self):
        template = self.jinja_env.from_string(
        """
        {% display dictobj['name'] %}
        """)
        output = template.render(dictobj={'name': 'thomas'})
        print(output)

    def test_top_level(self):
        template = self.jinja_env.from_string(
        """
        {% display dictobj %}
        """)
        output = template.render(dictobj={'name': 'thomas'})
        print(output)

    def test_literal(self):
        template = self.jinja_env.from_string(
        """
        {% display "hey" %}
        """)
        output = template.render(dictobj={'name': 'thomas'})
        print(output)

    def test_literal(self):
        template = self.jinja_env.from_string(
        """
        {% display "hey" + " man" %}
        """)
        output = template.render(dictobj={'name': 'thomas'})
        print(output)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()