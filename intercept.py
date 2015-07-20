#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

import sys
sys.path.append(".")

from hashlib import sha1
from bs4 import BeautifulSoup
from libmproxy.protocol.http import decoded
from csp_applier import html, mongo_driver, template

def start(context, argv):
    if len(argv) != 3:
        raise ValueError('Usage: -s "intercept.py [http_path] [file_path]"')

    context.http_path, context.file_path = argv[1], argv[2]

def response(context, flow):
    with decoded(flow.response):  # Automatically decode gzipped responses.
        if flow.response.headers["Content-Type"] == ["text/html"]:
            soup = BeautifulSoup(flow.response.content)
            f = open("test.text", "w")
            f.write(flow.request.url + "\n")
            f.close()
            html_parser = html.HTMLParser(soup)
            filter_list = []
            # pattern = fetch_template(flow.request.get_url(), flow.response)
            # if pattern:
            #     filter_list = pattern.compare(html_parser)

            new_content = html.HTMLGenerator(html_parser, filter_list, sha1(flow.request.url).hexdigest(),
                                             context.file_path, context.http_path)
            new_content.write_js()
            new_content.write_css()
            new_content.rewrite_html()
            flow.response.content = str(new_content.html_parser.soup)

def fetch_template(url, response):
    db = mongo_driver.MongoDriver()
    template_string = db.query(sha1(url).hexdigest())
    if template_string:
        return template.Template(template_string)
    else:
        return None
