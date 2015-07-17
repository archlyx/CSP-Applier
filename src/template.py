from hashlib import sha1
from naive_template import NaiveTemplate

import json

class Template:
    def __init__(self, entry=None):
        self.template = {}

        if entry:
            self.build_from_db(entry)

    def build_from_db(self, entry):
        self.template = json.dumps(entry)

    def compare(self, html):
        return self.compare_js(html) + self.compare_css(html)

    def compare_js(self, html):
        external_js, inline_js, attr_js = html.scripts
        return self.compare_external_js(external_js) + \
            self.compare_inline_js(inline_js) + \
            self.compare_attr_js(attr_js)

    def compare_css(self, html):
        external_css, inline_css, attr_css = html.styles
        return self.compare_external_css(external_css) + \
            self.compare_inline_css(inline_css) + \
            self.compare_attr_css(attr_css)

    def compare_external_js(self, external_js):
        filter_list = []
        for src, tag, uuid in external_js:
            if sha1(src) not in self.template['js'].keys():
                filter_list.append(uuid)
        return filter_list

    def compare_inline_js(self, inline_js):
        js_skeletons = [v["dynamic_skeleton"] for v in self.template['js'].values() if "dynamic_skeleton" in v.keys()]
        filter_list = []
        for tag, uuid in inline_js:
            is_block = True
            content = unicode(tag.string)
            for skeleton in js_skeletons:
                intersect = NaiveTemplate.two_string_diff(content, skeleton)
                if len(intersect) == len(skeleton):
                    is_block = False
                    break
            if is_block:
                filter_list.append(uuid)
        return filter_list

    def compare_attr_js(self, attr_js):
        filter_list = []
        for event, tag, uuid in attr_js:
            if sha1(unicode(tag.string)) not in self.template['js'].keys():
                filter_list.append(uuid)
        return filter_list

    def compare_external_css(self, external_css):
        filter_list = []
        for href, tag, uuid in external_css:
            if sha1(href) not in self.template['css'].keys():
                filter_list.append(uuid)
        return filter_list

    def compare_inline_css(self, inline_css):
        css_skeletons = [v["dynamic_skeleton"] for v in self.template['css'].values() if "dynamic_skeleton" in v.keys()]
        filter_list = []
        for tag, uuid in inline_css:
            is_block = True
            content = unicode(tag.string)
            for skeleton in css_skeletons:
                intersect = NaiveTemplate.two_string_diff(content, skeleton)
                if len(intersect) == len(skeleton):
                    is_block = False
                    break
            if is_block:
                filter_list.append(uuid)
        return filter_list

    def compare_attr_css(self, attr_css):
        filter_list = []
        for event, tag, uuid in attr_css:
            if sha1(unicode(tag.string)) not in self.template['css'].keys():
                filter_list.append(uuid)
        return filter_list

    # Get the info for CSP
    def get_csp_src(self):
        return self.template["csp-sources"]
