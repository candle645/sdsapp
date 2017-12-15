'''
Created on Dec 12, 2017

@author: candle
'''
from lxml import etree

class BaseDataHandler(object):
    '''
    classdocs
    '''

    def __init__(self, db_conn):
        '''
        Constructor
        '''
        self.db = db_conn
        
    def show (self, item_id, target=None):
        art_info = self.db.load_item (self.ITEM_CLASS.ITEM_TYPE, item_id)
        if art_info is None:
            return None

        item = self.ITEM_CLASS ()
        item.from_xml (art_info)
        ixml = item.to_xml ()
        if target is not None:
            target.append (ixml)
            
        return ixml
    
    def get_item (self, item_id):
        return self.show (item_id)
    
    def modify (self, item_id, item_data, target):
        art_info = self.db.load_item (self.ITEM_CLASS.ITEM_TYPE, item_id)
        if art_info is None:
            return False

        item = self.ITEM_CLASS ()
        item.from_xml (art_info)
        item.update (item_data)
        inode = etree.Element (self.ITEM_CLASS.ITEM_TYPE)
        is_valid = item.validate (inode)
        
        if is_valid:
            self.db.begin ()
            self.db.save_item (self.ITEM_CLASS.ITEM_TYPE, item.id, item.to_xml ())
            self.db.commit ()
            return True
        else:
            target.append (inode)
            return False
        
    def create (self, owner_id, item_data, target):
        item = self.ITEM_CLASS ()
        item.ownerId = owner_id
        item.update (item_data)
        inode = etree.Element (self.ITEM_CLASS.ITEM_TYPE)
        is_valid = item.validate (inode)
        
        if is_valid:
            self.db.begin ()
            item.id = self.db.next_item_id (self.ITEM_CLASS.ITEM_TYPE)
            self.db.save_item (self.ITEM_CLASS.ITEM_TYPE, item.id, item.to_xml ())
            self.db.commit ()
            return True
        else:
            target.append (inode)
            return False
    
    def check_exists (self, item_slug):
        item_id = self.db.get_id_by_slug (self.ITEM_CLASS.ITEM_TYPE, item_slug)
        if item_id is None:
            return False
        return True
    
    def get_id_by_slug (self, item_slug):
        item_id = self.db.get_id_by_slug (self.ITEM_CLASS.ITEM_TYPE, item_slug)
        return item_id
    
    def delete (self, item_id):
        """
        """
        self.db.begin ()
        res = self.db.delete_item (self.ITEM_CLASS.ITEM_TYPE, item_id)
        self.db.commit ()
        return res
        
    def _update_slugs (self):
        ilist = self.db.load_top_items (self.ITEM_CLASS.ITEM_TYPE)
        self.db.begin ()
        for item_info in ilist:
            item = self.ITEM_CLASS ()
            item.from_xml (item_info)
            self.db.save_item (self.ITEM_CLASS.ITEM_TYPE, item.id, item.to_xml ())
        self.db.commit ()
        