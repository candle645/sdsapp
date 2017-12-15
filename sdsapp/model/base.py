'''
Created on Dec 12, 2017

@author: candle
'''
from datetime import datetime
from lxml import etree

import logging
log = logging.getLogger('sdsapp')

from sdsapp.utils import to_timestamp, to_datetime

class BaseItem(object):
    """
    Base interface/implementation for business-layer objects
    """
    def __init__(self):
        '''
        Constructor
        '''
        
        self.id = ''
        self.ownerId = ''
        self.ctime = datetime.now ()
        self.mtime = self.ctime
        self.slug = None
        for attr in self.FUZZY_ATTRIBUTES:
            # init atribute
            setattr(self, attr, None)
            
            # getter
            setattr(self, "get_%s" % attr,
                    lambda attr=attr: self.__getattribute__(attr))
            setattr(self.__dict__["get_%s" % attr], '__name__',  "get_%s" % attr)

            # setter
            setattr(self, "set_%s" % attr,
                    lambda value, attr=attr: self.__setattr__(attr, value))
            setattr(self.__dict__["set_%s" % attr], '__name__',  "set_%s" % attr)
            
    def update (self, item_data):
        """
        """
        for attr in self.FUZZY_ATTRIBUTES:
            if attr not in item_data:
                continue
            self.__setattr__ (attr, item_data.get (attr))
        self.mtime = datetime.now ()

    def validate (self, target = None):
        """
        Check whenever item is valid. If validation fails and <target> passed - provide errors information there   
        """
        res = True
        for attr in self.FUZZY_ATTRIBUTES:
            val = self.__getattribute__ (attr)
            if val is None or len (val) == 0:
                res = False
                if target is not None:
                    err = "%s %s can't be empty" % (self.ITEM_TYPE, attr)
                    etree.SubElement (target, attr, error=err).text = str (val)
                    
        if res == False and target is not None:
            self._add_core_attributes(target)
            for attr in self.FUZZY_ATTRIBUTES:
                anode = target.find (attr)
                if anode is None:
                    etree.SubElement (target, attr).text = str (self.__getattribute__ (attr))

        return res

    def _add_core_attributes (self, target):
        target.set ('id', str (self.id))
        target.set ('ctime', to_timestamp (self.ctime))
        target.set ('mtime', to_timestamp (self.mtime))
        if self.slug is not None:
            target.set ('slug', self.slug)
            
        owner = self.ownerId
        if owner is None:
            owner = ''
        target.set ('ownerId', str (owner))
        
    def to_xml (self):
        """
        Serialize object to XML format
        """
        ret = etree.Element (self.ITEM_TYPE)
        self._add_core_attributes(ret)
        
        for attr in self.FUZZY_ATTRIBUTES:
            etree.SubElement (ret, attr).text = self.__getattribute__ (attr)
            
        return ret
            
    def to_string (self):
        """
        Serialize to XML and return as string, mostly for debugging/logging purposes.
        In "real" application may be too "heavy"/redundant, so intentionally made as separate method instead of __str() or __repr() override 
        """
        return etree.tostring (self.to_xml (), encoding='UTF-8', pretty_print=True)
            
    def from_xml (self, node):
        """
        De-serialize object from xml format
        """
        self.id = node.get ('id')
        self.ownerId = node.get ('ownerId')
        self.slug = node.get ('slug')
        self.ctime = to_datetime (node.get ('ctime'))
        self.mtime = to_datetime (node.get ('mtime'))
        
        for child in node.findall ('*'):
            if child.tag not in self.FUZZY_ATTRIBUTES:
                log.debug ('Unknown attribute %s.%s skipped' % (self.ITEM_NAME, child.tag))
                continue
            attr = child.tag
            self.__setattr__ (attr, child.text)

