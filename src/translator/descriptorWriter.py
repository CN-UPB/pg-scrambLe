import pandas as pd
import numpy as np
import yaml
import json
import pymongo
from bson.objectid import ObjectId

class write_dict():

    def append_dict(self,parent_key, lvl, dictionary):
        '''
        reads a parent key , a list of values that should be mapped to the parent key and an empty dictionary
        to contain the result.  

        Params
        ------
        parent_key : str
            contains the key which is to be assigned a value
        lvl : list
            contains an array of items which needs to be transformed properly before assigning to the key
       dictionary : dict
            empty dictionary for the result

        Returns
        -------
        dict
            returns a full dictionary containing a key and a value which is another dictionary
        
        '''
        inner_dict = {}
        list_dict = []

        k, v = lvl[0][1].split(' : ')
        inner_dict.update({k: v})

        for i in range(1, len(lvl)):

            if (lvl[i - 1][0] == lvl[i][0]):
                k, v = lvl[i][1].split(' : ')
                inner_dict.update({k: v})

            elif (lvl[i - 1][0] != lvl[i][0]):
                list_dict.append(inner_dict)
                inner_dict = {}
                k, v = lvl[i][1].split(' : ')
                inner_dict.update({k: v})

        list_dict.append(inner_dict)
        dictionary[parent_key] = list_dict

        return dictionary

    def getKey(self,item):
        '''
        used to sort items in a list
        '''
        return item[0]

    def make_json(self,dataset, level):
        '''
        takes a python DataFrame and iterate over all the keys at a particular level
        which are mapped to higher levels

        Params
        ------
        ds : pandas.DataFrame
            dataframe containing the details at a particular level
        levels : int
            current level to be checked

        Returns
        -------
        list , dict
            returns an iterator containing both a list of parent key values and a current level dictionary 
        
        '''
    
        parent_level = dataset[(dataset['level'] == level) & (dataset['value']!= 'NULL')]['parent_level'].unique()  # getting the parent level from the dataframe
        s=dataset[(dataset['level'] == level) & (dataset['value']!= 'NULL')].groupby(by=['parent_key']).agg({'key':lambda x: x.nunique() })  # getting the unique set of keys whose values are at higher levels 
                                                                                                                                                                                                # along with the number of items
                                                                                                                                                                                                # (in case the values at the higher levels are repeated in an array)
        s=s.to_dict()  # converting the set of keys 
            
        for parent,ele in s['key'].items():             #iterating over each keys found in previous step
            lvl_dict={}
            parent_key=[]
            
            lvl=list(dataset[(dataset['level'] == level) & (dataset['value']!= 'NULL') & (dataset['parent_key']== parent )][['id','key','value']].apply(lambda x : (x.id,x.key+' : '+str(x.value)), axis=1).values)
            # list containing the id ( which is used to maintain an enumeration of arrays ) and a concatenation of key,value 
            
            lvl_dict.update(self.append_dict(parent,sorted(lvl,key=self.getKey),{})) # calling append function to tidy up the dictionary 
            
            parent_key.append(np.unique(dataset[(dataset['key'] == parent) & (dataset['level'] == parent_level[0])  & (dataset['value']== 'NULL')]['parent_key'].values)) # creating a list of parents at this level
            
            yield parent_key, lvl_dict
        
        
    def reverse_loop(self,dictionary, key, value):
        '''
        takes a dictionary and a key value pair. The key is searched in the dictionary, 
        when found the value is mapped to the key.

        Params
        ------
        dictionary : python dict / python list
            variable containing the values at a particular level
        key : str
            contains the key to which the value is to be assigned
        value : int / list / str
            contains the item/s which is mapped to the key
        Returns
        -------
        dict
            returns a complete dictionary/list of a particular level
        '''
        if (isinstance(dictionary, dict)):
            for k, v in dictionary.items():
                if (k == key):
                    if (isinstance(v, dict)):
                        dictionary[k].update(value)
                    elif (isinstance(v, list)):
                        for val in dictionary[k]:
                            val.update(value)
                else:
                    self.reverse_loop(dictionary[k], key, value)
        elif (isinstance(dictionary, list)):
            for d in dictionary:
                self.reverse_loop(d, key, value)
                
        return dictionary

    def write(self,dataset, levels):
        '''
        takes a pandas.DataFrame and an array containing the number of levels
        and iterates over each level to call make_json and reverse_loop functions in order to create
        a full dictionary at each level together with mapping/connecting it with its previous level key

        Params
        ------
        ds : pandas.DataFrame
            dataframe containing the descriptor details
        levels : array
            array of levels in the descriptor
        
        Returns
        -------
        dict
            returns a dictionary of the translated descriptor
        
        '''
        full_dict = {}
        for level in levels:   # iterating at each level and creating a dictionary and mapping it further down with higher levels
            for key,val in self.make_json(dataset, level):
                if len(key[0]) >= 1:
                    if not full_dict: # check to ensure this the first iteration and full_dict is empty
                        full_dict[key[0][0]] = val
                    else:               # for iterations when full_dict already been populated with values
                        full_dict = self.reverse_loop(full_dict, key[0][0], val)
                elif len(key[0])==0 and level == 1:
                    full_dict = val

        return full_dict

    def translate_nsd(self,ds):
        '''
        takes a pandas.DataFrame and pass it as parameter to write function
        along with an array containing the number of levels

        Params
        ------
        ds : pandas.DataFrame
            dataframe containing the descriptor details
        
        Returns
        -------
        dict
            returns a dictionary of the translated descriptor
        
        '''
        return self.write(ds,range(8))


