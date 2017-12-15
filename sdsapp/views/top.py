from pyramid.view import view_config

from lxml import etree

from sdsapp.model.category import Category
from sdsapp.model.article import Article
from sdsapp.xslt import xslt_transform_m

from .base import BaseView

import logging
log = logging.getLogger('sdsapp')
    
class TopView (BaseView):
    VIEW_TYPE = 'top'
    @view_config(route_name='home')
    @xslt_transform_m(template_name='main')
    def home (self):
        """
        Category page, shows all categories list (at left) and most recent articles (on right)
        """
        self.action = 'home'
        self.check_permission ()
        
        request = self.request
        category_handler = request.registry.SDSDataHandlers.get (Category.ITEM_TYPE)
        if category_handler is None:
            raise Exception ()
    
        article_handler = request.registry.SDSDataHandlers.get (Article.ITEM_TYPE)
        if article_handler is None:
            raise Exception ()
    
        ret = self.root ()
        croot = etree.SubElement (ret, 'categories')
        category_handler.list (croot)
        
        aroot = article_handler.list ()
        ret.append (aroot)
        if self.request.authenticated_userid is not None:
            proot = ret.find ('permissions')
            ret.set ('user', self.request.authenticated_userid)
            access_handler = self.request.registry.SDSAccessHandler
            access_handler.apply_permissions (self.request.authenticated_userid, 'article', ['create'], [None], proot)

        return ret
