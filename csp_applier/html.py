#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
from uuid import uuid4

class HTMLParser:
    """
    Analyze the HTML and re-organize the scripts and styles
    """

    __events = [
        # Mouse Events
        "onclick", "ondblclick", "onmousedown", "onmousemove", "onmouseover", "onmouseout", "onmouseup",
        # Keyboard Events
        "onkeydown", "onkeypress", "onkeyup",
        # Frame/Object Events
        "onabort", "onerror", "onload", "onresize", "onscroll", "onunload",
        # Form Events
        "onblur", "onchange", "onfocus", "onreset", "onselect", "onsubmit"
    ]

    def __init__(self, soup):
        self.soup = soup

        self.scripts = self.extract_js()
        self.styles = self.extract_css()

    def extract_js(self):
        external_js = []
        inline_js = []
        for tag in self.soup.find_all('script'):
            if tag.has_attr('src'):
                external_js.append((tag['src'], tag, uuid4().hex))
            elif (not tag.has_attr("type")) or tag["type"] != "text/html":
                inline_js.append((tag, uuid4().hex))

        attr_js = []
        for listener in self.__events:
            for tag in self.soup.find_all(True):
                if tag.has_attr(listener):
                    attr_js.append((listener, tag, uuid4().hex))
        return external_js, inline_js, attr_js

    def extract_css(self):
        external_css = []
        for tag in self.soup.find_all('link'):
            if tag.has_attr('href'):
                if tag['href'].endswith('.css'):
                    external_css.append((tag['href'], tag, uuid4().hex))

        inline_css = []
        for tag in self.soup.find_all('style'):
            inline_css.append((tag, uuid4().hex))

        attr_css = []
        for tag in self.soup.find_all(True):
            if tag.has_attr('style'):
                attr_css.append((tag, uuid4().hex))

        return external_css, inline_css, attr_css

class HTMLGenerator:

    def __init__(self, html_parser, filter_list, file_name, root_dir, root_http_path):
        self.html_parser = html_parser
        self.filter_list = filter_list
        self.file_name = file_name
        self.directory = self.wrap_path(root_dir) + file_name + "/"
        self.http_path = self.wrap_path(root_http_path) + file_name + "/"

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def rewrite_html(self):
        external_js, inline_js, attr_js = self.html_parser.scripts
        for src, tag, uuid in external_js:
            if uuid in self.filter_list:
                tag.extract()
        for tag, uuid in inline_js:
            if uuid not in self.filter_list:
                src = self.http_path + self.file_name + "_" + uuid + "_inline.js"
                new_tag = self.html_parser.soup.new_tag("script", src=src)
                tag.replace_with(new_tag)
            else:
                tag.extract()
        for event, tag, uuid in attr_js:
            del tag[event]

        external_css, inline_css, attr_css = self.html_parser.styles
        for href, tag, uuid in external_css:
            if uuid in self.filter_list:
                tag.extract()
        for tag, uuid in inline_css:
            tag.extract()
        for tag, uuid in attr_css:
            del tag["style"]

        new_script = self.html_parser.soup.new_tag("script", src=self.http_path + self.file_name + "_events.js")
        self.html_parser.soup.body.append(new_script)

        new_style = self.html_parser.soup.new_tag("link", rel="stylesheet", type="text/css",
                                                  href=self.http_path + self.file_name + ".css")
        self.html_parser.soup.body.append(new_style)

    def write_js(self):
        external_js, inline_js, attr_js = self.html_parser.scripts
        self.generate_inline_js(inline_js)
        self.generate_attr_js(attr_js)

    def write_css(self):
        external_css, inline_css, attr_css = self.html_parser.styles
        self.generate_inline_css(inline_css)
        self.generate_attr_css(attr_css)

    def generate_inline_js(self, inline_js):
        for tag, uuid in inline_js:
            if uuid not in self.filter_list:
                file_path = self.directory + self.file_name + "_" + uuid + "_inline.js"
                f = open(file_path, 'w')
                f.write("// CSP-Applier: Script - " + uuid + " \r\n")
                f.write(str(unicode(tag.string)))
                f.write("\r\n")
                f.close()

    def generate_attr_js(self, attr_js):
        file_path = self.directory + self.file_name + "_events.js"
        f = open(file_path, 'w')
        f.write('\r\n')
        f.write("document.addEventListener('DOMContentLoaded', function () {")
        f.write('\r\n')

        for event, tag, uuid in attr_js:
            if uuid not in self.filter_list:
                content = tag[event]
                js_id = uuid if "id" not in tag.attrs.keys() else tag["id"]
                f.write("// CSP-Applier: Script - " + uuid + " \r\n")
                f.write("var element_" + js_id + " = document.getElementById(\"" + js_id + "\");")
                f.write("\r\n")
                f.write("element_" + js_id + ".addEventListener(\"" + event[2:] +
                        "\", function() {" + content + "}, false);")
                f.write("\r\n")
        f.write("\r\n});")
        f.close()

    def generate_inline_css(self, inline_css):
        file_path = self.directory + self.file_name + ".css"
        f = open(file_path, 'w')
        for tag, uuid in inline_css:
            if uuid not in self.filter_list:
                f.write("/* CSP-Applier: Style - " + uuid + "*/\r\n")
                f.write(str(unicode(tag.string)))
        f.close()

    def generate_attr_css(self, attr_css):
        file_path = self.directory + self.file_name + ".css"
        f = open(file_path, 'w')
        for tag, uuid in attr_css:
            if uuid not in self.filter_list:
                content = tag["style"]
                css_id = uuid if "id" not in tag.attrs.keys() else tag["id"]
                f.write("\r\n")
                f.write("/* CSP-Applier: Style - " + css_id + "*/\r\n")
                f.write("#" + css_id + "{" + content + "}")
                f.write("\r\n")
        f.close()

    @staticmethod
    def wrap_path(path):
        return (path + "/") if path[-1] != "/" else path
