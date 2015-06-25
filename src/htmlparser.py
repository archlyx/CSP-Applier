from bs4 import BeautifulSoup

__author__ = 'archlyx'

class HTMLParser:

    __listeners = [
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
                external_js.append((tag['src'], tag))
            else:
                inline_js.append(tag)

        attr_js = []
        for listener in self.__listeners:
            for tag in self.soup.find_all(True):
                if tag.has_attr(listener):
                    attr_js.append((listener, tag))
        return external_js, inline_js, attr_js

    def extract_css(self):
        external_css = []
        for tag in self.soup.find_all('link'):
            if tag.has_attr('href'):
                if tag['href'].endswith('.css'):
                    external_css.append((tag['href'], tag))

        inline_css = []
        for tag in self.soup.find_all('style'):
            inline_css.append(tag)

        attr_css = []
        for tag in self.soup.find_all(True):
            if tag.has_attr('style'):
                attr_css.append(tag)

        return external_css, inline_css, attr_css
