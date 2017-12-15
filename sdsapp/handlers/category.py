'''
Created on Dec 12, 2017

@author: candle
'''
from lxml import etree

from sdsapp.model.category import Category
from .base import BaseDataHandler

from sdsapp.utils import strip_whitespace

class CategoryHandler (BaseDataHandler):
    """
    Provides base DataHandler implementation access to data type manipulated by this Handler 
    """
    ITEM_CLASS = Category

    def __init__(self, db_conn):
        super().__init__(db_conn)
        
    def list (self, target=None):
        """
        Retreive list of items and appends it data to specified XML node, if provided
        Returns XML node containing all liste items
        """
        clist = self.db.load_top_items (Category.ITEM_TYPE)
        
        if target is None:
            croot = etree.Element ('categories')
        else:
            croot = target
        
        for cat_info in clist:
            cat = Category ()
            cat.from_xml (cat_info)
            croot.append (cat.to_xml())
            
        return croot
    
    def generate_test_categories (self):
        croot = etree.Element ('categories')
        for cat_title in self.title_generator ():
            cat_slug = strip_whitespace(cat_title).lower ()
            if not self.check_exists(cat_slug):
                self.create('candle', dict (title=cat_title), croot)
    
    def title_generator (self):
        titles = [
                  'Soccer',
                  'Baseball',
                  'Skiing',
                  'Skating',
                  'Hockey',
                  'Rock Climbing',
                  'Preferans',
                  ]
        for title in titles:
            yield title
