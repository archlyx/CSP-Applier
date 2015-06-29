import json
from hashlib import sha1
from diff_match_patch import diff_match_patch

__author__ = 'archlyx'

class Template:

    def __init__(self, html_parsers):
        self.js_dict = {}
        external_js_list, inline_js_list, attr_js_list = zip(*[html.scripts for html in html_parsers])

        for external_js in self.group_tags(external_js_list):
            sha, tag = external_js_hash(external_js)
            self.js_dict.setdefault(sha, []).append(self.tag_to_json(tag))

        for inline_js in self.group_tags(inline_js_list):
            sha, tag = inline_js_hash(inline_js)
            self.js_dict.setdefault(sha, []).append(self.tag_to_json(tag))

        for attr_js in self.group_tags(attr_js_list):
            sha, tag = attr_js_hash(attr_js)
            self.js_dict.setdefault(sha, []).append(self.tag_to_json(tag))

        self.css_dict = {}
        external_css_list, inline_css_list, attr_css_list = zip(*[html.styles for html in html_parsers])

        for external_css in self.group_tags(external_css_list):
            sha, tag = external_css_hash(external_css)
            self.css_dict.setdefault(sha, []).append(self.tag_to_json(tag))

        for inline_css in self.group_tags(inline_css_list):
            sha, tag = inline_css_hash(inline_css)
            self.css_dict.setdefault(sha, []).append(self.tag_to_json(tag))

        for attr_css in self.group_tags(attr_css_list):
            sha, tag = attr_css_hash(attr_css)
            self.css_dict.setdefault(sha, []).append(self.tag_to_json(tag))

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
        if len(tag_group) < 2:
            return tag_group

        intersect = self.two_string_diff(tag_group[0], tag_group[1])
        for tag in tag_group[2:]:
            intersect = self.two_string_diff(intersect, tag)

        return sha1(intersect)

    def tag_to_json(self, tag, event=""):
        extra = {"tag": tag.name, "event": event, "path": self.find_path(tag, [])}
        json_tag = Template.__merge_dict(tag.attrs, extra)
        return json.dumps(json_tag)

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

    @staticmethod
    def two_string_diff(s1, s2):
        dmp = diff_match_patch()
        dmp.Diff_Timeout = 16
        diffs = dmp.diff_main(s1, s2)
        dmp.diff_cleanupSemantic(diffs)
        return "".join([s for o, s in diffs if o == 0])