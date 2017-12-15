from pyramid.view import view_config

from pyramid.httpexceptions import (
                                    HTTPFound, 
                                    )

from .base import BaseView

import logging
log = logging.getLogger('sdsapp')
    
from pyramid.security import (
    remember,
    forget,
    )
class LoginView (BaseView):
    VIEW_TYPE = 'login'
    @view_config(route_name='login', renderer='json')
    def login (self):
        request = self.request
        access_handler = request.registry.SDSAccessHandler
        user_name = request.params.get ('login')
        user_pass = request.params.get ('password')
        err = access_handler.login (user_name, user_pass)
        ret = {}
        if err is not None:
            ret ['error'] = err
            return ret
        
        ret ['success'] = True
        headers = remember (request, user_name)
        request.response.headers.extend (headers)
        
        return ret
        
    @view_config(route_name='logout')
    def logout (self):
        request = self.request
        access_handler = request.registry.SDSAccessHandler
        access_handler.logout ()
        headers = forget (request)
        url = request.route_url('home')
        return HTTPFound (location=url, headers=headers)
