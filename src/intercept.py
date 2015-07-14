#!/usr/bin/env python
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

    context.old, context.new = argv[1], argv[2]

def response(context, flow):
    with decoded(flow.response):  # automatically decode gzipped responses.
        soup = BeautifulSoup(flow.response.content)
        if soup.body:
            html_parser = html.HTMLParser(soup)

def fetch_template(url, response):
        db = mongo_driver.MongoDriver()
        return Template(db.query(sha1(url)))
