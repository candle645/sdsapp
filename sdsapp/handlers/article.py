'''
Created on Dec 12, 2017

@author: candle
'''
from lxml import etree
from urllib.request import urlopen

from sdsapp.model.article import Article
from sdsapp.model.category import Category
from sdsapp.utils import (
                          parse_html, 
                          strip_whitespace,
                          strip_formatting
                          )
from .base import BaseDataHandler

import logging
log = logging.getLogger('sdsapp')


class ArticleHandler (BaseDataHandler):
    """
    Provides base DataHandler implementation access to data type manipulated by this Handler 
    """
    ITEM_CLASS = Article

    def __init__(self, db_conn):
        super().__init__(db_conn)
        
    def list (self, category_id=None, target=None):
        """
        Retreive list of items and appends it data to specified XML node, if provided
        Returns XML node containing all liste items
        """
        if target is None:
            croot = etree.Element ('articles')
        else:
            croot = target
            
        if category_id is None:
            alist = self.db.load_top_items (Article.ITEM_TYPE, 10)
        else:
            alist = self.db.load_category_items (Article.ITEM_TYPE, category_id)
            croot.set ('categoryId', str (category_id))
            
        if alist is None:
            return croot
            
        for art_info in alist:
            art = Article ()
            art.from_xml (art_info)
            croot.append (art.to_xml())
            
        return croot
        
    def import_desc (self, article_title):
        ret = dict ()
        try:
            url = "https://en.wikipedia.org/wiki/%s" % article_title
            from sdsapp.utils import test_func_q4
            ret ['html'] = test_func_q4 (url)
            ret ['success'] = True
        except Exception as e:
            ret ['error'] = str (e)
        
        return ret