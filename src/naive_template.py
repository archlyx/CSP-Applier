#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
from hashlib import sha1
from diff_match_patch import diff_match_patch

class NaiveTemplate:

    def __init__(self, incoming_html=None):
        self.js_dict = {}
        self.css_dict = {}

        if incoming_html:
            self.html = incoming_html

    def build_js(self):
        external_js_list, inline_js_list, attr_js_list = zip(*[html.scripts for html in self.html_candidates])

        for external_js in self.group_tags(external_js_list):
            sha, tag = self.external_js_hash(external_js)
            self.js_dict.setdefault(sha, []).append(self.tag_to_dict(tag))

        for inline_js in self.group_tags(inline_js_list):
            sha, is_dynamic, skeleton, tag = self.inline_js_hash(inline_js)
            if is_dynamic:
                self.js_dict.setdefault(sha, []).append(self.tag_to_dict(tag, skeleton=skeleton))
            else:
                self.js_dict.setdefault(sha, []).append(self.tag_to_dict(tag))

        for attr_js in self.group_tags(attr_js_list):
            sha, tag, event = self.attr_js_hash(attr_js)
            self.js_dict.setdefault(sha, []).append(self.tag_to_dict(tag, event=event))

    def build_css(self):
        external_css_list, inline_css_list, attr_css_list = zip(*[html.styles for html in self.html_candidates])

        for external_css in self.group_tags(external_css_list):
            sha, tag = self.external_css_hash(external_css)
            self.css_dict.setdefault(sha, []).append(self.tag_to_dict(tag))

        for inline_css in self.group_tags(inline_css_list):
            sha, is_dynamic, skeleton, tag = self.inline_css_hash(inline_css)
            if is_dynamic:
                self.css_dict.setdefault(sha, []).append(self.tag_to_dict(tag, skeleton=skeleton))
            else:
                self.css_dict.setdefault(sha, []).append(self.tag_to_dict(tag))

        for attr_css in self.group_tags(attr_css_list):
            sha, tag = self.attr_css_hash(attr_css)
            self.css_dict.setdefault(sha, []).append(self.tag_to_dict(tag))

    # Input external_js is the same script in different version
    @staticmethod
    def external_js_hash(js_list):
        src, tag, uuid = js_list[0]
        return sha1(src), tag

    def inline_js_hash(self, js_list):
        sha, is_dynamic, skeleton = self.skeleton_hash(js_list)
        return sha, is_dynamic, skeleton, js_list[0]

    @staticmethod
    def attr_js_hash(js_list):
        event, tag, uuid = js_list[0]
        return sha1(unicode(tag.string)), tag, event

    @staticmethod
    def external_css_hash(css_list):
        href, tag, uuid = css_list[0]
        return sha1(href), tag

    def inline_css_hash(self, css_list):
        sha, is_dynamic, skeleton = self.skeleton_hash(css_list)
        return sha, is_dynamic, skeleton, css_list[0]

    @staticmethod
    def attr_css_hash(css_list):
        tag, uuid = css_list[0]
        return sha1(unicode(tag.string)), tag

    def dump_json(self):
        return json.dumps({"js": self.js_dict, "css": self.css_dict})

    # tag_lists: a list of tag_list generated for each version of HTML
    @staticmethod
    def group_tags(tag_lists):
        min_length = min([len(l) for l in tag_lists])
        list_of_tags = []
        for i in range(min_length):
            list_of_tags.append([l[i] for l in tag_lists])
        return list_of_tags

    # tag_group: a list of text strings of the tags
    def skeleton_hash(self, tag_group):
        text_group = [unicode(tag.string) for tag, uuid in tag_group]
        if len(text_group) < 2:
            return sha1(text_group[0]), False, text_group[0]

        intersect = self.two_string_diff(text_group[0], text_group[1])
        for tag in text_group[2:]:
            intersect = self.two_string_diff(intersect, tag)

        return sha1(intersect), len(intersect) < len(text_group[0]), intersect

    def tag_to_dict(self, tag, event=None, skeleton=None):
        extra = {"tag": tag.name, "path": self.find_path(tag, [])}

        if event:
            extra["csp_event"] = event

        if skeleton:
            extra["dynamic_skeleton"] = skeleton

        return self.__merge_dict(tag.attrs, extra)

    def find_path(self, tag, tag_path):
        parent = tag.parent
        if parent is None:
            return tag_path
        else:
            info = parent.attrs.copy()
            info["tag"] = parent.name
            tag_path.append(info)

        return self.find_path(parent, tag_path)

    @staticmethod
    def __merge_dict(x, y):
        z = x.copy()
        z.update(y)
        return z

