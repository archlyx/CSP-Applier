import json
from hashlib import sha1

__author__ = 'archlyx'

class Template:

    def __init__(self, html_parser):
        js_dict = {}
        for external_js, inline_js, attr_js in html_parser.scripts:
            for src, tag in external_js:
                js_dict.setdefault(sha1(src), []).append(self.tag_to_json(tag))

            for tag in inline_js:
                js_dict.setdefault(sha1(unicode(tag.string)), []).append(self.tag_to_json(tag))

            for event, tag in attr_js:
                js_dict.setdefault(sha1(tag[event]), []).append(self.tag_to_json(tag, event))

        css_dict = {}
        for external_css, inline_css, attr_css in html_parser.styles:
            for href, tag in external_css:
                js_dict.setdefault(sha1(href), []).append(self.tag_to_json(tag))

            for tag in inline_css:
                js_dict.setdefault(sha1(unicode(tag.string)), []).append(self.tag_to_json(tag))

            for tag in attr_css:
                js_dict.setdefault(sha1(tag['style']), []).append(self.tag_to_json(tag))

        self.js_json = json.dumps(js_dict)
        self.css_json = json.dumps(css_dict)

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
