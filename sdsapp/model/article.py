'''
Created on Dec 12, 2017

@author: candle
'''

from .base import BaseItem

class Article(BaseItem):
    '''
    classdocs
    '''
    FUZZY_ATTRIBUTES = frozenset ([
                                   'title', 
                                   'description',
                                   ])
    ITEM_TYPE = 'article'
    
    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        self.categoryId = ''
        
    def update (self, item_data):
        super().update (item_data)
        if 'categoryId' in item_data:
            self.categoryId = item_data.get ('categoryId')
        
    def load (self, itemId):
        """
        """
        super().load (itemId)
        
    def _add_core_attributes (self, target):
        super()._add_core_attributes (target)
        target.set ('categoryId', str (self.categoryId))
            
    def to_xml (self):
        ret = super ().to_xml ()
        ret.set ('categoryId', str (self.categoryId))
        return ret

    def from_xml (self, node):
        super ().from_xml (node)
        self.categoryId = node.get ('categoryId')
