from bs4 import BeautifulSoup
from bs4 import NavigableString
from urlparse import urlparse
from uuid import uuid4
import logging, sys, re, tldextract, json, urllib, hashlib, os, time

logger = logging.getLogger('HTMLParser')
hdlr = logging.FileHandler('./logs/html_parser2.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)

class DOMAnalyzer:
	
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

	def __init__(self, soup, local_url, dest_dir, page_url='undefined'):
		self.soup = soup
		self.inlines = {}
		self.externals = []
		self.script_tags = []
		self.url = page_url
		self.local_url = \
			local_url if (local_url[-1]=='/') else (local_url+'/')
		self.dest_dir = dest_dir
		self.attr_js = []

		m = hashlib.md5()
		m.update(page_url)
		self.urlhash = m.hexdigest()

	def process(self):
		self.inlines = {}
		self.externals = [] # for debugging use
		self.remove_tags = []
		self.clear_tags = []
		self.attr_js = []

		logger.info('start processing %s' %self.url)
		self._traverse(self.soup, None, 0)
		try:
			[tag.decompose() for tag in self.remove_tags]
			[tag.clear() for tag in self.clear_tags]
		except Exception as e:
			logger.error('error in removing/clearing tag node: %s' %str(e))

		logger.info('done processing DOM, cleared %d tags and removed %d tags' \
			%(len(self.clear_tags), len(self.remove_tags)))

		# write inlines
		for key in self.inlines:
			#logger.debug('sc contents: %s' %self.inlines[key] )
			if not self._write_external_script(key, self.inlines[key]):
				logger.error('failed to write external script: %s' %key)
			else:
				logger.info('done writing external script: \
					%s size: %d' %(key, len(self.inlines[key])) )
		logger.info('Process result: %d inlines and %d externals' \
			%(len(self.inlines), len(self.externals)))

		# process event listeners
		inline_event_listeners = []
		for item in self.attr_js: #(id, event, script)
			sc = self._wrap_event_listener(item[0], item[1], item[2])
			if sc == None:
				continue
			inline_event_listeners.append(sc)

		if len(inline_event_listeners) > 0:
			try:
				full_listeners = \
					"document.addEventListener('DOMContentLoaded', function () { console.log('domcontentloaded!!'); %s } );\r\n"
				full_listeners = full_listeners % ( '\r\n'.join(inline_event_listeners) )
				file_name = 'script_%s_%s_event.js' %(uuid4().hex, self.urlhash)
				self._write_external_script(file_name, full_listeners)
				# modify html page
				new_tag = self.soup.new_tag('script',src=self._build_local_url_path(file_name))
				self.soup.head.insert(1, new_tag)
			except Exception as e:
				logger.error('error in generating event listener: %s' %(str(e)))

	def _traverse(self, root, parent_node, level):
		#print "traverse: ",str(root)
		if root == None:
			return ""

		if isinstance(root, NavigableString):
			rs = root.string
			if rs == None:
				return None
				
			try:
				rs = rs.encode('utf-8').strip()
			except Exception as e:
				pass
			return rs

		external = None
		inline = None
		try:
			#logger.debug("NAME:%s TYPE:%s" %(root.name, str(root.get('type')) ) )
			tag = root.name.lower()
			if tag == 'script':
				if root.get('src') != None:
					external = root.get('src').strip().lower()
					#root['id'] = len(self.externals)
					#self.remove_tags.append(root)
					if not self._check_url(external):
						self.remove_tags.append(root)
				elif isinstance(root.contents[0], NavigableString):
					inline = self._traverse(root.contents[0], root, level+1)
					if inline == None:
						logger.debug('None inline contents: %s' %root)
					rs = self._check_inline_script(inline)
					self.clear_tags.append(root)
					if rs == None or len(rs) == 0:
						logger.info('Script failed checking: %s' % self._encode_script(inline) )
					else:					
						file_name = 'script_%d_%s_inline.js' %(len(self.inlines), self.urlhash)
						root['src'] = self._build_local_url_path(file_name)
						self.inlines[file_name] = rs
				else:
					logger.warning("unknown script tag: "+str(tag)) 
				# for debugging
				if external != None:
					self.externals.append(external)
			
			for event in self.__events:
				if root.has_attr(event):
					if not root.has_attr('id'):
						root['id'] = uuid4().hex
					tag_id = root['id']
					script = root[event]
					del root[event]
					self.attr_js.append((tag_id, event, script))
					logger.debug("inline event listener: %s" %str((tag_id, event, script))) 

		except Exception as e:
			logger.error("Error: %s" % ( str(e)+" "+root.name))

		for child in root.contents:
			self._traverse(child, root, level+1)

	def _wrap_event_listener(self, tag_id, event, body):
		try:
			#fun_name = 'csp_%s_%s' %(tag_id, event)
			#listener = "var %s = function() { %s }; \r\n" \
			#	%(fun_name, body)

			call_stat = \
				"try { \r\n" + \
					"console.log('eventlistener!!');\r\n" +\
					"document.getElementById('%s')" + \
					".addEventListener('%s', function () { %s }); \r\n" + \
				"} catch(e) {console.log(e);}\r\n"
			call_stat = call_stat % (tag_id, event[2:], body)
		except Exception as e:
			logger.error('error in _wrap_event_listener: %s ' %(str(e)))
			return None

		return call_stat

	def _build_local_url_path(self, full_name):
		return self.local_url + full_name

	def _encode_script(self, script):
		rs  = None
		try:
			try:
				rs = script.encode('utf-8', 'ignore').strip()
			except UnicodeEncodeError:
				#logger.debug('UnicodeEncodeError failed encoding utf-8')
				rs = unicode(script)
			except UnicodeDecodeError:
				#logger.debug('UnicodeDecodeError failed encoding utf-8')
				rs = script				
		except Exception as e:
			logger.error(' %s failed encoding script: %s' %(e.__class__.__name__, str(e)))
		return rs

	# TODO: not implemented
	def _check_url(self, url):
		try:
			domain = self._get_effective_domain(url)
			logger.debug('_check_url: find domain: %s' %(domain))
			if domain == None:
				return True
			else:
				# add template matching methods here
				return True
		except Exception as e:
			return False

	# TODO: not implemented
	def _check_inline_script(self, content):
		return content

	def _write_external_script(self, file_name, contents):
		try:
			full_path = os.path.join(self.dest_dir, file_name)
			rs = self._encode_script(contents)
			if rs == None:
				logger.error('_write_external_script failed: encoding contents failed')
				return False
			fw = open(full_path, 'w')
			fw.write("// CSP-Applier: Script - " + self.url + " \r\n")
			fw.write("%s\r\n" % (rs))
			fw.close()
			return True
		except Exception as e:
			logger.error('_write_external_script failed: %s' %str(e))
			return False

	def _get_effective_domain(self, url):
		try:
			url = urllib.unquote_plus(url.lower())
			no_fetch_extract = tldextract.TLDExtract(suffix_list_url=False)
			o = no_fetch_extract(url)
			return o.domain + '.' + o.suffix
		except Exception as e:
			logger.error("error in getting getEffectiveDomain %s" %str(e))
			return None

def main():
	t1 = time.time()
	#tldextract.TLDExtract(suffix_list_url=False)
	#tldextract.extract('http://www.cnn.com')
	t2 = time.time()
	contents = open(sys.argv[1]).read()
	#print contents
	try:
		soup = BeautifulSoup( contents, "html5lib")
	except Exception as e:
		soup = BeautifulSoup( contents, 'lxml')
	analyzer = DOMAnalyzer(soup, \
		'https://localhost:4433/allowed-resources/', './js_repository/', 'https://www.sina.com')
	analyzer.process()
	t3 = time.time()
	logger.debug("time difference: DOM:%f, whole:%f" %((t3-t2), (t3-t1)))
	#logger.debug('NEXT ROUND')
	#analyzer.process()
	new_tag = soup.new_tag("script", src="https://localhost:4433/libs/client_lib.js")
	analyzer.soup.head.insert(1, new_tag)
	print analyzer.soup.prettify().encode('utf-8')
	#print soup.prettify().encode('utf-8')

if __name__ == "__main__":
	main()

	'''
	def extract_js(self):
		external_js = []
		inline_js = []
		for tag in self.soup.find_all('script'):
		    if tag.has_attr('src'):
		        external_js.append((tag['src'], tag, uuid4().hex))
		    elif tag.has_attr('type') and tag["type"] != "text/html":
		        logger.debug('[INLINE SCRIPT]: %s' %str(tag) )
		        inline_js.append((tag, uuid4().hex))

		attr_js = []
		for listener in self.__events:
		    for tag in self.soup.find_all(True):
		        if tag.has_attr(listener):
		            attr_js.append((listener, tag, uuid4().hex))
		logger.debug('[JS SUMMARY] %d inline, %d external, %d attrs' \
		    %(len(inline_js), len(external_js), len(attr_js) ) )

		self.external_js = external_js
		self.inline_js = inline_js
		self.attr_js = attr_js
	'''