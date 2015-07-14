import unittest
import html
from bs4 import BeautifulSoup

class TestHTMLParser(unittest.TestCase):
    def setUp(self):
        soup = BeautifulSoup(open("resources/test.html"))
        self.parser = html.HTMLParser(soup)

    def test_extract_js(self):
        external, inline, attr = self.parser.scripts
        self.assertEqual(4, len(external))
        self.assertEqual(6, len(inline))
        self.assertEqual(7, len(attr))

        for event, tag, uuid in attr:
            if event == 'onclick' and tag[event] == 'myfunction1()':
                self.assertEqual('button1', tag['id'])
            if event == 'onclick' and tag[event] == 'myfunction2()':
                self.assertTrue('button2' in tag['class'])
            if event == 'onmouseover' and tag[event] == 'myfunction4()':
                self.assertTrue('button2' in tag['class'])
            if event == 'onmouseover' and tag[event] == 'myfunction3()':
                self.assertEqual('button3', tag['id'])
            if event == 'onclick' and tag[event] == 'myfunction3()':
                self.assertEqual('button3', tag['id'])
            if event == 'onsubmit' and tag[event] == 'myfunction4()':
                self.assertEqual('get', tag['method'])
            if event == 'onsubmit' and tag[event] == 'myfunction5()':
                self.assertEqual('form1', tag['id'])

    def test_extract_css(self):
        external, inline, attr = self.parser.styles
        self.assertEqual(1, len(inline))
        self.assertEqual(3, len(attr))

if __name__ == "__main__":
    unittest.main()
