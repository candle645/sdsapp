from pyramid.view import view_config

from lxml import etree
from pyramid.httpexceptions import (
                                    HTTPNotFound, 
                                    HTTPFound, 
                                    )

from sdsapp.model.category import Category
from sdsapp.model.article import Article
from sdsapp.xslt import xslt_transform_m

from sdsapp.handlers.access import AccessHandlerSingleton

from .base import BaseView

import logging
log = logging.getLogger('sdsapp')

class ArticleView (BaseView):
    VIEW_TYPE = 'article'
    @view_config(route_name='article_show')
    @xslt_transform_m(template_name='main')
    def show (self):
        """
        Article page, logged users can edit owned articles
        """
        self.action = 'show'
        self.check_permission ()

        request = self.request
        category_handler = request.registry.SDSDataHandlers.get (Category.ITEM_TYPE)
        article_handler = request.registry.SDSDataHandlers.get (Article.ITEM_TYPE)
        
        cat_slug = self.request.matchdict ['category']
        art_slug = self.request.matchdict ['article']
        
        cat_id = category_handler.get_id_by_slug (cat_slug)
        if cat_id is None:
            raise HTTPNotFound ('Invalid or unknown category: [%s]' % cat_slug)

        art_id = article_handler.get_id_by_slug (art_slug)
        if art_id is None:
            raise HTTPNotFound ('Invalid or unknown article: [%s]' % art_slug)

        ret = self.root ()
        category_handler.show (cat_id, ret)
        article_handler.show (art_id, ret)
        
        if self.request.authenticated_userid is not None:
            proot = ret.find ('permissions')
            ret.set ('user', self.request.authenticated_userid)
            access_handler = AccessHandlerSingleton ()
            access_handler.apply_permissions (self.request.authenticated_userid, self.VIEW_TYPE, ['modify', 'delete'], ret.findall ('article'), proot)
        
        return ret
        
    @view_config(route_name='article_edit')
    @xslt_transform_m(template_name='main')
    def modify (self):
        """
        Article page, logged users can edit owned articles
        """
        self.action = 'modify'
        self.check_permission ()

        request = self.request
        category_handler = request.registry.SDSDataHandlers.get (Category.ITEM_TYPE)
        article_handler = request.registry.SDSDataHandlers.get (Article.ITEM_TYPE)

        cat_slug = self.request.matchdict ['category']
        art_slug = self.request.matchdict ['article']
        
        cat_id = category_handler.get_id_by_slug (cat_slug)
        if cat_id is None:
            raise HTTPNotFound ('Invalid or unknown category: [%s]' % cat_slug)

        art_id = article_handler.get_id_by_slug (art_slug)
        if art_id is None:
            raise HTTPNotFound ('Invalid or unknown article: [%s]' % art_slug)

        ret = self.root ()
        
        item = article_handler.show (art_id, ret)
        self.check_permission (item)
        
        if request.method == 'GET':
            croot = etree.SubElement (ret, 'categories')
        elif request.method == 'POST':
            res = article_handler.modify (art_id, request.params, ret)
            if res == True:
                location = '/catalog/%s/%s' % (cat_slug, art_slug)
                return HTTPFound (location=location)
            croot = etree.SubElement (ret, 'categories')
            
        category_handler.list (croot)
        category_handler.show (cat_id, ret)
        
        return ret

    @view_config(route_name='article_create')
    @xslt_transform_m(template_name='main')
    def create (self):
        """
        """
        self.action = 'create'
        self.check_permission ()

        request = self.request
        category_handler = request.registry.SDSDataHandlers.get (Category.ITEM_TYPE)
        article_handler = request.registry.SDSDataHandlers.get (Article.ITEM_TYPE)

        ret = self.root ()
        
        if request.method == 'GET':
            croot = etree.SubElement (ret, 'categories')
        elif request.method == 'POST':
            res = article_handler.create (self.user_id, request.params, ret)
            if res == True:
                location = '/'
                return HTTPFound (location=location)
            
            croot = etree.SubElement (ret, 'categories')
            
        category_handler.list (croot)
        
        return ret

    @view_config(route_name='article_delete')
    @xslt_transform_m(template_name='main')
    def delete (self):
        """
        """
        self.action = 'delete'
        self.check_permission ()

        request = self.request
        category_handler = request.registry.SDSDataHandlers.get (Category.ITEM_TYPE)
        article_handler = request.registry.SDSDataHandlers.get (Article.ITEM_TYPE)

        cat_slug = self.request.matchdict ['category']
        art_slug = self.request.matchdict ['article']
        
        cat_id = category_handler.get_id_by_slug (cat_slug)
        if cat_id is None:
            raise HTTPNotFound ('Invalid or unknown category: [%s]' % cat_slug)

        art_id = article_handler.get_id_by_slug (art_slug)
        if art_id is None:
            raise HTTPNotFound ('Invalid or unknown article: [%s]' % art_slug)

        ret = self.root ()
        
        item = article_handler.show (art_id, ret)
        self.check_permission (item)
        
        if request.method == 'GET':
            pass
        elif request.method == 'POST':
            res = article_handler.delete (art_id)
            if res == True:
                location = '/'
                return HTTPFound (location=location)
            
        category_handler.show (cat_id, ret)
        
        return ret
    
    @view_config(route_name='article_import', renderer='json')
    def import_desc (self):
        self.action = 'import'
        self.check_permission ()
        
        request = self.request

        article_handler = request.registry.SDSDataHandlers.get (Article.ITEM_TYPE)
        
        ret = article_handler.import_desc (request.params.get ('title'))
        
        return ret
