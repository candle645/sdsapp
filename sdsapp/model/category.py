'''
Created on Dec 12, 2017

@author: candle
'''

from .base import BaseItem

class Category(BaseItem):
    '''
    classdocs
    '''
    FUZZY_ATTRIBUTES = frozenset ([
                                   'title', 
                                   ])
    ITEM_TYPE = 'category'
    
    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        
