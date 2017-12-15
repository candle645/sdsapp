'''
Created on Dec 12, 2017

@author: candle
'''

from datetime import datetime
import string

import logging
log = logging.getLogger('sdsapp')

def to_timestamp (dt):
    return dt.strftime ('%d.%m.%Y %H:%M:%S')

def to_datetime (st):
    return datetime.strptime (st, "%d.%m.%Y %H:%M:%S")
    
def strip_whitespace (src):
    ret = src
    for ch in string.whitespace:
        ret = ret.replace (ch, '')
    return ret

def strip_formatting (src):
    ret = src
    ret = ret.replace ('\n', '')
    ret = ret.replace ('\t', '')
    ret = ret.replace ('\\t', '')
    ret = ret.replace ('\\n', '')
    return ret


from urllib.request import urlopen
from html.parser import HTMLParser
from lxml import etree
class SDSHTMLParser (HTMLParser):
    def __init__ (self):
        super().__init__()
        
    def parse (self, data):
        self.is_html = False
        self.xml = etree.Element ('html')
        self.cur_node = self.xml

        self.feed (data)
        
        return self.xml
        
    def handle_starttag(self, tag, attrs):
        tag = tag.lower ()
        self.cur_node = etree.SubElement (self.cur_node, tag)
        for attr, val in attrs:
            try:
                self.cur_node.set (attr, val)
            except:
                pass
                    
    def handle_endtag(self, tag):
        tag = tag.lower ()
        if tag == self.cur_node.tag:
            self.cur_node = self.cur_node.getparent ()
            if self.cur_node is None:
                self.cur_node = self.xml
    
    def handle_data(self, data):
        if data is None:
            return
#        data = data.strip (string.whitespace)
        if data == '':
            return
        
        clist = self.cur_node.getchildren () 
        if len (clist) == 0:
            if self.cur_node.text is None:
                self.cur_node.text = data
            else:
                self.cur_node.text += data
        else:
            if clist [len(clist)-1].tail is None:
                clist [len(clist)-1].tail = data
            else:
                clist [len(clist)-1].tail += data

def parse_html (data):
    parser = SDSHTMLParser ()
    return parser.parse(data)

def load_url (url):
    ret = urlopen (url).read ()
    return ret

def test_func_q4 (url):
    
    html = load_url (url)
    
    sample_html="""
    <html>
        <script>alert('qq');</script>
        <div>text-only div</div>
        <div>have subnodes<p>and more content</p></div>
        <div>have subnodes<p>and more content</p>and even more content</div>
        <div>
            have div childrens
            <div>child div content<p>and more content</p></div>
        </div>
    </html>
    """
    
#    html = sample_html
    xml = parse_html (str (html))

    # Remove all nodes which definitely can't contain any useful text information
    ignored_tags = frozenset (['script', 'style', 'meta', 'head', 'link', 'svg'])
    
    from functools import reduce
    def add_tag_to_xquery (left, right):
        return left + (" or local-name()='%s'" % right)
     
    xpq = reduce (add_tag_to_xquery, ignored_tags, 'false()')
    
    xpq = '//*[%s]' % xpq
    
    nodes = xml.xpath (xpq)
    for node in nodes:
        node.getparent ().remove (node)
        
    # Get all <div> elements not contained inside other <div>
    xpq = '//div[not(ancestor::div)]'
    nodes = xml.xpath (xpq)

    #dump inner HTML of nodeset to HTML_output 
    html_output = ''
    for node in nodes:
        inner_html = node.xpath ('*|text()')
        for inode in inner_html:
            if isinstance (inode, str):
                html_output += inode
            else:
                html_output += etree.tostring (inode, encoding='UTF-8', pretty_print=True).decode('UTF-8')
    return html_output
