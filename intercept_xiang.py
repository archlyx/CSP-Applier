import sys, traceback
sys.path.append(".")

from hashlib import sha1
from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
from libmproxy.protocol.http import decoded
from csp_applier import html, template
from dom_analyzer import DOMAnalyzer

def start(context, argv):
    if len(argv) != 3:
        raise ValueError('Usage: -s "intercept.py [http_path] [file_path]"')

    #context.http_path, context.file_path = argv[1], argv[2]
    context.f = open('./logs/log','w',0)

def response(context, flow):
<<<<<<< HEAD
    try:
        url = flow.request.url
        context.f.write('receive response: %s\n'%flow.request.url)
        with decoded(flow.response):  # Automatically decode gzipped responses.
            if (not "Content-Type" in flow.response.headers) or \
                len(flow.response.headers) == 0:
                return
            tp = flow.response.headers["Content-Type"][0].lower()
            #context.f.write('  type:%s\n' %tp)
            if "text/html" in tp:
                flow.response.headers['Content-Security-Policy'] = \
                    ["default-src 'self' 'unsafe-eval' *; style-src 'self' 'unsafe-eval' 'unsafe-inline' *"]
                flow.response.headers['Cache-Control'] = ["no-cache"]
                #context.f.write('  rewrite response %s %s\n' % (flow.request.url, \
                #    str(flow.response.headers) ) )
                try:
                    soup = BeautifulSoup( flow.response.content, "html5lib")
                except Exception as e:
                    soup = BeautifulSoup( flow.response.content, 'lxml')
                analyzer = DOMAnalyzer(soup, \
                    'https://localhost:4433/allowed-resources/', \
                    './js_repository/', flow.request.url)
                analyzer.process()
                client_lib_node = soup.new_tag("script", src="https://localhost:4433/libs/client_lib.js")
                analyzer.soup.head.insert(1, client_lib_node)
                #try:
                #    context.f.write('  OLD response %s:\n' % soup.prettify().encode('ascii', 'ignore'))
                #except Exception as e:
                #    context.f.write('  display response error %s\n' %(str(e)) )
                #context.f.write("    debug before analyzing\n")
                #context.f.write("    debug after analyzing %d\n" %(len(html_parser)) )

                context.f.write("  need write %d inlines \n" %(len(analyzer.inlines)) )
                #new_content = UnicodeDammit(analyzer.soup.prettify())
                #flow.response.content = new_content.unicode_markup
                try:
                    flow.response.content = analyzer.soup.prettify().encode('utf-8')
                    context.f.write('newcontent:%s\n' %flow.response.content)
                except Exception as e:
                    context.f.write("  encoding exception: %s\n" %(str(e)))
                #context.f.write("  new HTML:\n %s  \n" %(flow.response.content) )
            else:
                pass
                #context.f.write('NOT rewriting %s %s response\n' % (flow.request.url,\
                #    flow.response.headers["Content-Type"]) )
            context.f.write('\n')
            
    except Exception as e:
        context.f.write('exception at %s for error: %s\n' %(url, str(e)))
        traceback.print_exc(file=context.f)


=======
    # f1 = open("ctype.txt", "a")
    # f1.write(flow.response.headers.get_first("content-type", ""))
    # f1.write('\n')
    # f1.close()
    if "text/html" in flow.response.headers.get_first("content-type", ""):
        with decoded(flow.response):  # Automatically decode gzipped responses.
            f = open(context.file_path + "/url.text", "a")
            f.write("------------------" + "\n")
            f.write(flow.request.url)
            f.write('\n')

            soup = BeautifulSoup(flow.response.content)
            try:
                html_parser = html.HTMLParser(soup)
                filter_list = []
        
                # TODO: If database daemon is running, uncomment these lines
                # pattern = fetch_template(flow.request.host)
                # if pattern:
                #     filter_list = pattern.compare(html_parser)
        
                new_content = html.HTMLGenerator(html_parser, filter_list, sha1(flow.request.host).hexdigest(),
                                                 context.file_path, context.http_path)
                new_content.write_js()
                new_content.write_css()
                new_content.rewrite_html()
            except:
                f.write("Unexpected error: " + sys.exc_info()[0])

            flow.response.content = str(new_content.html_parser.soup)
>>>>>>> 5e1980555fca88c8f49e2bf698c6c23bac8d32aa

            f.write('\n')
            f.close()

def fetch_template(url):
    db = mongo_driver.MongoDriver()
    template_string = db.query(sha1(url).hexdigest())
    if template_string:
        return template.Template(template_string)
    else:
        return None
