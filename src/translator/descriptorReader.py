import pandas as pd
import numpy as np
import yaml
import json
import pymongo
from bson.objectid import ObjectId

### @Arka
class read_dict():

    def dict_parser(self,dictionary, key, level, lineage):
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
        lineage : str
            variable to maintain and determine the lineage of items 

        Returns
        -------
        python.iterator
            yields a a list of [parent level valule, parent key value, current level value, current key value, item index value] 
        at each level of iteration 
        
        '''
        
        if isinstance(dictionary, dict):

            for k,v in dictionary.items():

                if isinstance(v,str)  or isinstance(v, int):
                    result = [level-1,str(key),level,str(k),v,lineage]
                    yield result
                    
                if isinstance(v, dict):
                    yield [level-1,str(key),level,str(k),None,None]
                    for res in self.dict_parser(v,k,level+1,str(lineage)+'|'+key+'|0'):
                        yield res
                        
                elif isinstance(v, list):
                    if(isinstance(v[0],str)):
                        yield [level-1,str(key),level,str(k),v,lineage]
                    else:
                        yield [level-1,str(key),level,str(k),None,None]
                        for j,i in enumerate(v):
                            for res in self.dict_parser(i,k,level+1,(str(lineage)+'|'+key+'|'+str(j))):
                                yield res
                
        else:
            pass