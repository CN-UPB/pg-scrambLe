import pandas as pd
import numpy as np
import yaml
import json
import pymongo
from bson.objectid import ObjectId

class read_dict():

    def dict_parser(self,dictionary, key, level, pk):
        '''
        reads a dictionary and iterate over its items in a heirarchy and returns all 
        information (parent key, parent level, current key, current level, current value, primary key) 
        at each level.
        Params
        ------
        dictionary : dict
            dictionary containing the descriptor details
        key : str
            the name of the root node/key (while calling this function for the first time this variable can be any string).
        level : int
            the level of the root node/key (default : 1)
        pk : int
            variable to maintain and determine the item index in an array of items 
        Returns
        -------
        python.iterator
            yields a a list of [parent level valule, parent key value, current level value, current key value, item index value] 
        at each level of iteration 
        
        '''
        
        if isinstance(dictionary, dict):
            for k,v in dictionary.items():
                if isinstance(v,str)  or isinstance(v, int):
                    result = [level-1,str(key),level,str(k),v,pk]
                    yield result
                    
                if isinstance(v, dict):
                    yield [level-1,str(key),level,str(k),None,None]
                    for res in self.dict_parser(v,k,level+1,pk):
                        yield res
                        
                elif isinstance(v, list):
                    if(isinstance(v[0],str)):
                        yield [level-1,str(key),level,str(k),v,pk]
                        for i in v:
                            for res in self.dict_parser(i,k,level+1,None):
                                yield res
                    else:
                        yield [level-1,str(key),level,str(k),None,None]
                        for j,i in enumerate(v):
                            for res in self.dict_parser(i,k,level+1,(10*(pk) + j+1)):
                                yield res
        else:
            pass

            
    