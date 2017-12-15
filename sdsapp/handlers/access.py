'''
Created on Dec 13, 2017

@author: candle
'''
from lxml import etree

from sdsapp.utils import strip_whitespace

import logging
log = logging.getLogger('sdsapp')

class Permission (object):
    """
    Access Permission rule.
    As mockup - implementing very simple access control model:
        - everything prohibited by default
        - permissions granted per user, no Groups and/or Roles
        - there are no items hierarchy and permission derived by hierarchy
        - you can use following "wildcard" keywords instead of exact view/action/user/item:
            - "$any$" - any (every) known entity (view, action, user, item)
            - "$user$ - any (every) logged-in user
            - "$new$" - new (non-existent) items, e.g. create new articles
            - "$own$" - items owned by user 
    """
    def __init__ (self, user='$any$', view='$any$', action='$any$', item='$any$'):
        self.user = user
        self.view = view
        self.action = action
        self.item = item
        
    def match (self, user, view, action, item, strict=True, is_owner=None):
        """
        Match this permission against specified access request.
        Call with strict=False and view/action=None if you need to see all permissions for specified user or user permissions for specified view
        """
        weak = not strict
#        log.debug ('%s %s %s %s %s' % (user, view, action, item, strict))
#        log.debug ('%s %s %s %s %s' % (self.user, self.view, self.action, self.item, strict))
        if (self.user == '$any$' or self.user == user) or (self.user == '$user$' and user is not None):
            if self.view == '$any$' or self.view == view or (view is None and weak):
                if self.action == '$any$' or self.action == action or (action is None and weak):
                    if self.item == '$new$' and (item == '$new$' or item is None):
                        #Rule for access non-existent items - e.g. create new one
#                        log.debug ('------------------------------------------------------ allow (new items)')
                        return True
                    elif item is None and weak:
#                        log.debug ('------------------------------------------------------ allow (weak)')
                        return True
                    elif self.item == '$any$':
                        #Rule for access every item
#                        log.debug ('------------------------------------------------------ allow (by $any$ item)')
                        return True
                    elif self.item == item:
                        #Rule for access item with specified id
#                        log.debug ('------------------------------------------------------ allow (by item_Id)')
                        return True
                    elif self.item == '$own$' and is_owner is not None and item is not None and is_owner (user, item):
                        #Rule for access owned items
#                        log.debug ('------------------------------------------------------ allow (by owner)')
                        return True
#        log.debug ('------------------------------------------------------ deny')
        return False

class AccessHandler(object):
    """
    """
    def __init__(self):
        self.permissions = list ()
        pass
    
    def find_permission (self, user, view, action, item):
        def is_owner (user, item):
            return user == item.get ('ownerId')

        strict = item is not None

        for perm in self.permissions:
            if perm.match (user, view, action, item, strict, is_owner):
                return perm
        return None
    
    def get_permissions_normal (self, user, view, action, item, target=None):
        """
        Returns all permission matching specified user, view, action and item as XML
        Optionally append result to XML node provided as "target" 
        """
        if target is None:
            proot = etree.Element ('permissions')
        else:
            proot = target
            
        for perm in self.permissions:
            if perm.match (user, view, action, item, False):
                pnode = etree.SubElement (proot, 'permission')
                if perm.view is not None:
                    pnode.set ('view', perm.view)
                if perm.action is not None:
                    pnode.set ('action', perm.action)
                if perm.item is not None:
                    pnode.set ('item', perm.item)
                
        return proot
    
#    def get_permissions_using_filter (self, user, view, action, item, target=None):
    def get_permissions_using_filter (self, user, view, action, item, target=None):
        """
        Returns all permission matching specified user, view, action and item as XML
        Optionally append result to XML node provided as "target" 
        """
        if target is None:
            proot = etree.Element ('permissions')
        else:
            proot = target
            
        def filter_func (x):
            return x.match (user, view, action, item, False)
        
        for perm in filter (filter_func, self.permissions):
            pnode = etree.SubElement (proot, 'permission')
            if perm.view is not None:
                pnode.set ('view', perm.view)
            if perm.action is not None:
                pnode.set ('action', perm.action)
            if perm.item is not None:
                pnode.set ('item', perm.item)
                
        return proot

#    def get_permissions_using_map (self, user, view, action, item, target=None):
    def get_permissions (self, user, view, action, item, target=None):
        """
        Returns all permission matching specified user, view, action and item as XML
        Optionally append result to XML node provided as "target" 
        """
        if target is None:
            proot = etree.Element ('permissions')
        else:
            proot = target
            
        def perm_match (perm):
            return perm.match (user, view, action, item, False)

        def perm_xml (perm):
            pnode = etree.Element ('permission')
            if perm.view is not None:
                pnode.set ('view', perm.view)
            if perm.action is not None:
                pnode.set ('action', perm.action)
            if perm.item is not None:
                pnode.set ('item', perm.item)
            return pnode
        
        for pnode in map (perm_xml, filter (perm_match, self.permissions)):
            proot.append (pnode)
                
        return proot

    
    def grant_permission (self, user='$any$', view='$any$', action='$any$', item='$any$'):
        perm = self.find_permission (user, view, action, item)
        if perm is None:
            perm = Permission (user, view, action, item)
            self.permissions.append (perm)
    
    def apply_permissions (self, user, view, actions, items, target=None):
        """
        Match user permissions for specified view/actions against provided items
        and return exact permission rule for every matched item.
        Processing wildcard rules (with "$any$", "$own$", etc.) in templates very bad idea,
        so this method made to provide exact view/action/item IDs  
        """
#        log.debug ('%s %s %s %s' % (user, view, actions, items))
        if target is None:
            proot = etree.Element ('permissions')
        else:
            proot = target
            
        def is_owner (user, item):
            return user == item.get ('ownerId')
        
        for action in actions:
            for item in items:
                for perm in self.permissions:
                    if perm.match (user, view, action, item, True, is_owner):
                        pnode = etree.SubElement (proot, 'cpermission')
                        if perm.view is not None:
                            pnode.set ('view', view)
                        if perm.action is not None:
                            pnode.set ('action', action)
                        if perm.item is not None:
                            if item is not None:
                                pnode.set ('item', item.get ('id'))
                        break
        
        return proot
    
    def login (self, user_name, user_pass):
        """
        Authentificate and login user.
        """
        if user_name == 'candle' and user_pass != 'candle645':
            return 'Invalid user password'

        if user_name is None:
            return 'Invalid user name'
        
        uname = strip_whitespace (user_name)
        if user_name != uname or uname =='':
            return 'Invalid user name'
        
        if user_pass is None:
            return 'Invalid user password'
        
        upass = strip_whitespace (user_pass)

        if user_pass != upass or upass =='':
            return 'Invalid user password'
    
    def logout (self):
        return 
        

class AccessHandlerSingleton:
    class __Internal (AccessHandler):
        def __init__ (self):
            super().__init__()
    instance = None
    def __init__  (self):
        if AccessHandlerSingleton.instance is None:
            AccessHandlerSingleton.instance = AccessHandlerSingleton.__Internal ()
    
    def __getattr__ (self, name):
        return getattr (self.instance, name)
