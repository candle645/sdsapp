from pyramid.view import view_config

from lxml import etree
from pyramid.httpexceptions import (
                                    HTTPForbidden 
                                    )

import logging
log = logging.getLogger('sdsapp')

class BaseView (object):
    def __init__(self, request):
        self.request = request
        self.user_id = self.request.authenticated_userid
        
    def root (self):
        """
        Create root XML node and fill it with data common for all views
         - view and action
         - current user (if any) and his permissions for this view
        """
        # Some views may be rendered by same XSLT templates and shown content may depend on current actions
        # so we pass view/action informations to XSLT template 
        ret = etree.Element ('root', view=self.VIEW_TYPE, action=self.action, user_ip=str(self.request.remote_addr))
        
        # Add info about current user permissions inside this view in order to let template 
        # properly render restricted GUI elements, e.g. "edit"/"delete" buttons
        access_handler = self.request.registry.SDSAccessHandler
        proot = etree.SubElement (ret, 'permissions')
        if self.request.authenticated_userid is not None:
            ret.set ('user', self.request.authenticated_userid)
        access_handler.get_permissions (self.request.authenticated_userid, self.VIEW_TYPE, None, None, proot)
            
        return ret
    
    def check_permission (self, item=None):
        access_handler = self.request.registry.SDSAccessHandler

        log.debug ('Checking permission ---- %s: %s.%s (%s)' % (self.request.authenticated_userid, self.VIEW_TYPE, self.action, item))
        perm = access_handler.find_permission (self.request.authenticated_userid, self.VIEW_TYPE, self.action, item)
        if perm is not None:
            log.debug ('Permission found   ----  %s: %s.%s (%s)' % (perm.user, perm.view, perm.action, perm.item))

        if perm is None:
            if item is not None:
                idesc = item.get ('slug')
            else:
                idesc = ''
            
            if self.request.authenticated_userid is None:
                udesc = 'Anonymous'
            else:
                udesc = self.request.authenticated_userid
            
            errmsg = 'User [%s] have no access to %s.%s (%s)' % (udesc, self.VIEW_TYPE, self.action, idesc)
            raise HTTPForbidden (errmsg) 
