'''
Created on Dec 12, 2017

@author: candle
'''
import threading
import string

import logging
log = logging.getLogger('sdsapp')

from lxml import etree
from sdsapp.model.category import Category
from sdsapp.model.article import Article

from sdsapp.utils import strip_whitespace

class DatabaseAdapter(object):
    '''
    "Database" interface
    '''
    def init (self, params):
        """
        Initialize database connection
        """
    
    def begin (self):
        """ 
        Begin transaction 
        """
    
    def commit (self):
        """ 
        Commit transaction 
        """
        
    def rollback (self):    
        """ 
        Rollback transaction 
        """
    
    def load_item (self, item_cls, item_id):
        """
        Lookups and returns specified item data, if any 
        """
        
    def save_item (self, item):
        """
        Queue specified item data to store/update in current transaction
        """
        
    def load_top_items (self, item_type, count):
        """
        Loads and returns up to <count> of most recently added/modified items
        """

class DBException (Exception):        
    """Database access exception"""

class XMLDBAdapter(object):
    """
    "Database" mockup, uses XML file to store data.
    New/Updated items always added/moved to file end, so we can easily get most recent items by simple XPath query.
    Write access can be done only within "transaction" and only by single thread(connection) at time.
    """
    ITEM_TYPES = {
                  Category.ITEM_TYPE: {
                                       'rootNode': 'categories',
                                       'queryGet': "categories/category[@id='%s']",
                                       'queryTop': "categories/category[position() > count(categories/category) - %s]",
                                       'querySlug': "categories/category[@slug='%s']",
                                       'queryFind': "categories/category[@slug='%s']/@id",
                                       },
                  Article.ITEM_TYPE: {
                                       'rootNode': 'articles',
                                       'queryGet': "articles/article[@id='%s']",
                                       'queryTop': "articles/article[position() > count(articles/article) - %s]",
                                       'querySlug': "articles/article[@slug='%s']",
                                       'queryFind': "articles/article[@slug='%s']/@id",
                                       'queryList': "articles/article[@categoryId='%s']",
                                       },
                  }
    
    LOCK_TIMEOUT = 5

    def __init__(self):
        '''
        Constructor
        '''
        self.root = etree.Element ('sdsapp')
        self.rawData = etree.tostring (self.root, encoding='UTF-8', pretty_print=True)
        self.dbLock = threading.Lock()
        self.inTransaction = False
        self.dbPath = ''
        
    def init (self, params):
        self.dbPath = params.get ('path')
        db_file = open (self.dbPath, "r", encoding="utf-8")
        self.rawData = db_file.read ()
        db_file.close ()
        self.root = etree.XML (self.rawData)

    def begin (self):
        """ 
        Begin transaction 
        """
        if not self.dbLock.acquire (XMLDBAdapter.LOCK_TIMEOUT):
            raise DBException ("Transaction Start Timeout")
        self.inTransaction = True
    
    def commit (self):
        """ 
        Commit transaction 
        """
        #TODO: rename old, write new instead of rewrite existing
        self.rawData = etree.tostring (self.root, encoding='UTF-8', pretty_print=True)
        db_file = open (self.dbPath, "wb")
        db_file.write (self.rawData)
        self.inTransaction = False
        self.dbLock.release ()
        
    def rollback (self):    
        """ 
        Rollback transaction 
        """
        self.root = etree.XML (self.rawData)
        self.inTransaction = False
        self.dbLock.release ()
        
    def next_item_id (self, item_type):
        """
        Generate next ID for specified item type
        """
        item_md = self.ITEM_TYPES.get (item_type)
        if item_md is None:
            raise DBException ("Unknown item type: [%s]" % item_type)
        
        if self.inTransaction ==False:
            raise DBException ("Can't write data outside transaction")

        items_root = self.root.find (item_md ['rootNode'])
        if items_root is None:
            items_root = etree.SubElement (self.root, item_md ['rootNode'], last_id='1')            

        next_id = int(items_root.get ('last_id')) + 1
        items_root.set ('last_id', str (next_id)) 
        
        return next_id
    
    def get_id_by_slug (self, item_type, item_slug): 
        """
        Search database for item with specified slug and returns it ID
        """
#        log.debug ('get_id_by_slug (%s, %s)' % (item_type, item_slug))
        item_md = self.ITEM_TYPES.get (item_type)
        if item_md is None:
            raise DBException ("Unknown item type: [%s]" % item_type)
        
        xpq = item_md ['queryFind'] % (item_slug)
        nodes = self.root.xpath (xpq)
        if nodes is None or len (nodes) == 0:
            return None
        
#        log.debug ('---- found: %s' % nodes[0])
        
        return nodes [0]
        
    def load_item (self, item_type, item_id):
        item_md = self.ITEM_TYPES.get (item_type)
        if item_md is None:
            raise DBException ("Unknown item type: [%s]" % item_type)
        
        xpq = item_md ['queryGet'] % (item_id)
        nodes = self.root.xpath (xpq)
        if nodes is None or len (nodes) == 0:
            return None
        
        item_data = nodes [0]
        self._make_slug(item_type, item_id, item_data, item_md)
        
        return item_data
    
    def delete_item (self, item_type, item_id):
        item_md = self.ITEM_TYPES.get (item_type)
        if item_md is None:
            raise DBException ("Unknown item type: [%s]" % item_type)
        
        if self.inTransaction ==False:
            raise DBException ("Can't write data outside transaction")

        xpq = item_md ['queryGet'] % (item_id)
        nodes = self.root.xpath (xpq)
        if nodes is None or len (nodes) == 0:
            return False
        
        item_data = nodes [0]
        xpq = item_md ['rootNode']
        nodes = self.root.xpath (xpq)
        if nodes is None or len (nodes) == 0:
            return False
        nodes [0].remove (item_data)
        
        return True
    
    def save_item (self, item_type, item_id, item_data):
        item_md = self.ITEM_TYPES.get (item_type)
        if item_md is None:
            raise DBException ("Unknown item type: [%s]" % item_type)
        
        if self.inTransaction ==False:
            raise DBException ("Can't write data outside transaction")

        xpq = item_md ['queryGet'] % (item_id)
        items_root = self.root.find (item_md ['rootNode'])
        if items_root is None:
            items_root = etree.SubElement (self.root, item_md ['rootNode'])            
        nodes = self.root.xpath (xpq)
        if nodes is not None and len (nodes) != 0:
            items_root.remove (nodes [0])

        self._make_slug(item_type, item_id, item_data, item_md)
        if items_root is None:
            items_root = etree.SubElement (self.root, item_md ['rootNode'])            
        
        items_root.append (item_data)
        
    def load_top_items (self, item_type, max_count=100):
        item_md = self.ITEM_TYPES.get (item_type)
        if item_md is None:
            raise DBException ("Unknown item type: [%s]" % item_type)
        
        xpq = item_md ['queryTop'] % (max_count)
        nodes = self.root.xpath (xpq)
        if nodes is None or len (nodes) == 0:
            return None
        
        return nodes
    
    def load_category_items (self, item_type, category_id):
        item_md = self.ITEM_TYPES.get (item_type)
        if item_md is None:
            raise DBException ("Unknown item type: [%s]" % item_type)
        
        xpq = item_md ['queryList'] % (category_id)
        nodes = self.root.xpath (xpq)
        if nodes is None or len (nodes) == 0:
            return None
        
        return nodes
    
    def _make_slug (self, item_type, item_id, item_data, item_md):
        """
        Generate unique string ID of item used in user-friendly URLs.
        It based on item title, but for SEO purposes generated only once and remains same
        during whole item life.
        """
        slug = item_data.get ('slug')
        if slug is not None:
            return
        
        #TODO: use pytils.translit.slugify () instead ad-hoc implementation below
        # Unfortunately pytils.translit not available in pypi repository
        slug = item_data.find('title').text
        slug = strip_whitespace (slug)
        slug = slug.lower ()
        
        xpq = item_md ['querySlug'] % slug
        log.debug ('slug query: [%s]' % xpq)
        nodes = self.root.xpath (xpq)
        log.debug (nodes)
        if nodes is not None and len (nodes) != 0:
            slug = '%s%s' % (slug, item_id)
        log.debug ('new slug: [%s]' % slug)
        item_data.set ('slug', slug)
