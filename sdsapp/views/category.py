from pyramid.view import view_config

from lxml import etree
from pyramid.httpexceptions import (
                                    HTTPNotFound, 
                                    )

from sdsapp.model.category import Category
from sdsapp.model.article import Article
from sdsapp.xslt import xslt_transform_m

from .base import BaseView

import logging
log = logging.getLogger('sdsapp')

class CategoryView (BaseView):
    VIEW_TYPE = 'category'
    @view_config(route_name='category')
    @xslt_transform_m(template_name='main')
    def catalog (self):
        """
        Category page, shows all categories list (at left) and current category articles (on right)
        """
        self.action = 'catalog'
        self.check_permission ()
        
        request = self.request
        category_handler = request.registry.SDSDataHandlers.get (Category.ITEM_TYPE)
        article_handler = request.registry.SDSDataHandlers.get (Article.ITEM_TYPE)
        
        cat_slug = self.request.matchdict ['category']
        cat_id = category_handler.get_id_by_slug (cat_slug)
        if cat_id is None:
            raise HTTPNotFound ('Invalid or unknown category: [%s]' % cat_slug)
        
        ret = self.root ()
        croot = etree.SubElement (ret, 'categories')
        category_handler.list (croot)

        aroot = article_handler.list (cat_id)
        if aroot is not None:        
            ret.append (aroot)
            
        if self.request.authenticated_userid is not None:
            proot = ret.find ('permissions')
            ret.set ('user', self.request.authenticated_userid)
            access_handler = self.request.registry.SDSAccessHandler
            access_handler.apply_permissions (self.request.authenticated_userid, 'article', ['create'], [None], proot)
        return ret
