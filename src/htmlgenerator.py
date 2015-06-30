from bs4 import BeautifulSoup

__author__ = 'archlyx'

class HTMLGenerator:

    def __init__(self, html_parser, filter_list, file_name, directory, http_path):
        self.html_parser = html_parser
        self.filter_list = filter_list
        self.file_name = file_name
        self.directory = directory
        self.http_path = http_path

    def generate_html(self):

    def write_js(self):

    def write_css(self):

    def generate_inline_js(self):
        file_path = self.directory + self.file_name +
        f = open(self.directory + self.file_name + , 'w')

    def generate_attr_js(self):

    def generate_inline_css(self):

    def generate_attr_css(self):