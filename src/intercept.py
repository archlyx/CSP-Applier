#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

from hashlib import sha1
from template import Template
from bs4 import BeautifulSoup

import html
import mongo_driver

from libmproxy.protocol.http import decoded

def start(context, argv):
    if len(argv) != 3:
        raise ValueError('Usage: -s "intercept.py [http_path] [file_path]')

    context.http_path, context.file_path = argv[1], argv[2]

def response(context, flow):
    with decoded(flow.response):  # automatically decode gzipped responses.
        soup = BeautifulSoup(flow.response.content)
        if soup.body:
            template = fetch_template(flow.request.get_url(), flow.response)
            if template:
                html_parser = html.HTMLParser(soup)
                filter_list = template.compare(html_parser)
                new_content = html.HTMLGenerator(html_parser, sha1(flow.request.get_url()).hexdigest(),
                                                 filter_list, context.file_path, context.http_path)
                new_content.write_js()
                new_content.write_css()
                new_content.rewrite_html()
                flow.response.content = str(new_content.html_parser.soup)

def fetch_template(url, response):
    db = mongo_driver.MongoDriver()
    template_string = db.query(sha1(url).hexdigest())
    if template_string:
        return Template(template_string)
    else:
        return None
