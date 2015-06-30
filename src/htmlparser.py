from uuid import uuid4
from bs4 import BeautifulSoup

__author__ = 'archlyx'

class HTMLParser:

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

    def __init__(self, html):
        self.html = html
        self.soup = BeautifulSoup(html)

        self.scripts = self.extract_js()
        self.styles = self.extract_css()

    def extract_js(self):
        external_js = []
        inline_js = []
        for tag in self.soup.find_all('script'):
            if tag.has_attr('src'):
                external_js.append((tag['src'], tag, uuid4().hex))
            else:
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
