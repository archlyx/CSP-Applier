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
    # f1 = open("ctype.txt", "a")
    # f1.write(flow.response.headers.get_first("content-type", ""))
    # f1.write('\n')
    # f1.close()
    if "text/html" in flow.response.headers.get_first("content-type", ""):
        with decoded(flow.response):  # Automatically decode gzipped responses.
            f = open(context.file_path + "/url.text", "a")
            f.write("------------------" + "\n")
            f.write(flow.request.url)
            f.write('\n')

            soup = BeautifulSoup(flow.response.content)
            try:
                html_parser = html.HTMLParser(soup)
                filter_list = []
        
                # TODO: If database daemon is running, uncomment these lines
                # pattern = fetch_template(flow.request.host)
                # if pattern:
                #     filter_list = pattern.compare(html_parser)
        
                new_content = html.HTMLGenerator(html_parser, filter_list, sha1(flow.request.host).hexdigest(),
                                                 context.file_path, context.http_path)
                new_content.write_js()
                new_content.write_css()
                new_content.rewrite_html()
            except:
                f.write("Unexpected error: " + sys.exc_info()[0])

            flow.response.content = str(new_content.html_parser.soup)

            f.write('\n')
            f.close()

def fetch_template(url):
    db = mongo_driver.MongoDriver()
    template_string = db.query(sha1(url).hexdigest())
    if template_string:
        return template.Template(template_string)
    else:
        return None
