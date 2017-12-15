'''
Created on Dec 12, 2017

@author: candle
'''

from functools import wraps
from lxml import etree 
from pyramid.response import Response
from pyramid.httpexceptions import HTTPException 

import logging
log = logging.getLogger('sdsapp')

class XSLTException ():
    """XSLT Transform exception"""

class XSLTTransform(object):
    """
    Simple interface to XSLT transformations.
    """
#TODO: Implement "pyramid.reload_templates" feature support for XSLT templates
    def __init__(self):
        self.templatesPath = '~/sdsapp/templates'
        self.templates = dict ()

    def init (self, params):
        self.templatesPath = params.get ('path')
        
    def transform (self, template_name, node):
        if template_name not in self.templates:
            self._load_template (template_name)
        
        template = self.templates.get (template_name)
        
        return str (template (node))

    def _load_template (self, template_name):
        xslt_file = open ('%s/%s.xsl' % (self.templatesPath, template_name) , "r", encoding="utf-8")
        xslt_raw = xslt_file.read ()
        xslt_file.close ()
        xslt_doc = etree.XML (xslt_raw) 
        xslt_xform = etree.XSLT (xslt_doc)
        self.templates [template_name] = xslt_xform
    
def xslt_transform_f (template_name):
    """
    Helper decorator for Pyramid views implemented as functions
    """
    def use_params (function):
        def func_wrapper (*args, **kwargs):
            req = args[1]
            res = function (req, **kwargs)
            if isinstance (res, HTTPException): 
                return res
            html = req.registry.XSLTEngine.transform (template_name, res)
            return Response (html)
    
        return func_wrapper
    return use_params

def xslt_transform_m (template_name):
    """
    Helper decorator for Pyramid views implemented as classes
    """
    def use_params (function):
        @wraps(function)
        def method_wrapper (self, *args, **kwargs):
            res = function (self, **kwargs)
            if isinstance (res, HTTPException): 
                return res
            html = self.request.registry.XSLTEngine.transform (template_name, res)
            return Response (html)
    
        return method_wrapper
    return use_params


