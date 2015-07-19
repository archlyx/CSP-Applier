#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import unittest
import html
import naive_template
import template
from hashlib import sha1
from bs4 import BeautifulSoup

class TestTemplate(unittest.TestCase):
    def setUp(self):
        parser = html.HTMLParser(BeautifulSoup(open("resources/test.html")))
        self.template = template.Template(naive_template.NaiveTemplate(parser).generate_template())

        self.changes = [
            sha1("myfunction_evil()").hexdigest(),
            sha1("evil_yeah()").hexdigest(),
            sha1("color:red;margin-left:20px;").hexdigest()
        ]

    def test_compare(self):
        evil_parser = html.HTMLParser(BeautifulSoup(open("resources/test_evil.html")))
        filter_list = self.template.compare(evil_parser)
        self.assertEqual(3, len(filter_list))

        external, inline, attr = evil_parser.scripts
        for event, tag, uuid in attr:
            if uuid in filter_list:
                self.assertTrue(sha1(unicode(tag[event])).hexdigest() in self.changes)

        external, inline, attr = evil_parser.styles
        for tag, uuid in attr:
            if uuid in filter_list:
                self.assertTrue(sha1(unicode(tag["style"])).hexdigest() in self.changes)

if __name__ == "__main__":
    unittest.main()
