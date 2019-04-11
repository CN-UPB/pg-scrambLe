import pandas as pd
import numpy as np
import yaml
import json
import pymongo
from bson.objectid import ObjectId

### @Arka
class write_dict():

    def getKey(self,item):
        return item[0]

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

        k = list(lvl[0][2].keys())[0]
        v = list(lvl[0][2].values())[0]
        inner_dict.update({k: v})

        for i in range(1, len(lvl)):

            k = list(lvl[i][2].keys())[0]
            v = list(lvl[i][2].values())[0]
            
            if lvl[i][0] != lvl[i-1][0]:#k in inner_dict.keys():
                list_dict.append(inner_dict)
                inner_dict = {}
                inner_dict.update({k: v})
                
            else:
                inner_dict.update({k: v})

        list_dict.append(inner_dict)
        
        if ( (len(list_dict) >= 1) & (('id' in list_dict[0].keys()) 
                                      or ('name' in list_dict[0].keys())
                                     or ('id-ref' in list_dict[0].keys())
                                     or ('vnf_id' in list_dict[0].keys())
                                      or ('vnfd-id-ref' in list_dict[0].keys())
                                     or (('member-vnf-index-ref' in list_dict[0].keys())
                                        or ('order' in list_dict[0].keys())
                                        or ('vnfd-connection-point-ref' in list_dict[0].keys())
                                        ))):
            dictionary[parent_key] = list_dict
        else:
            dictionary[parent_key] = list_dict[0]

        return dictionary

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
        list , dict , pos
            returns an iterator containing both a list of parent key values and a current level dictionary 
        
        '''
        s = dataset[(dataset['level'] == level) & (dataset['value']!= 'NULL')].groupby(by=['parent_key']).agg(
            {'key':lambda x: x.nunique() })  # getting the unique set of keys whose values are at higher levels 
                                            # along with the number of items
                                            # (in case the values at the higher levels are repeated in an array)
        s = s.to_dict()   # converting the set of keys 
            
        for parent, _ in s['key'].items():  #iterating over each keys found in previous step
            lvl_dict=[]
            parent_key=[]
            parent_pos=[]
            
            lvl = pd.DataFrame(list(dataset[(dataset['level'] == level) & (dataset['value']!= 'NULL') & 
                                  (dataset['parent_key']== parent )][['lineage','key','value']].apply(
                                                    lambda x : [x.lineage,x.lineage[:-2],{x.key : x.value}] 
                                                    if (x.lineage[-2] == '|' )  
                                                    else [x.lineage,x.lineage,{x.key : x.value}], axis=1).values),
                          columns = ['lineage','lineage_grp','key-value'] )
            
            val = [x.values for _,x in lvl.groupby(['lineage_grp'])]
            
            length=2
            for i in range(2,dataset['level'].max()*2,2):
                if len(np.unique(lvl['lineage_grp'].apply(lambda x : x.split("|")[:-i]).values)) == 1:
                    length = i
                    break
            
            for g,l in enumerate(val):
                
                lvl_dict.append(self.append_dict(parent,l,{})) # calling append function to tidy up the dictionary
                parent_temp =[]
                parent_pos_temp =[]
                
                for j in range(0,length,2):
                    parent_temp.append(val[g][0][1].split('|')[-j-1])
                    parent_pos_temp.append(val[g][0][1].split('|')[-j-2])
                
                parent_key.append(parent_temp)
                parent_pos.append(parent_pos_temp)
            
            
            yield parent_key, lvl_dict ,parent_pos
        
        
    def reverse_loop(self,dictionary, key, value,pos):
        '''
        takes a dictionary and a key value pair. The key is searched in the dictionary, 
        when found the value is mapped to the key.

        Params
        ------
        dictionary : python dict / python list
            variable containing the values at a particular level
        key : list
            contains the lineage of parent keys
        value : int / list / str
            contains the item/s which is mapped to the key
        pos : list
            contains the positions of the lineage of parent keys
        
        Returns
        -------
        dict
            returns a complete dictionary/list of a particular level
        '''
        if (isinstance(dictionary, dict)):
            
            for k, v in dictionary.items():
                if len(key) == 0:
                    return dictionary
                
                if (k == key[-1]):
                    key.pop()
                    
                    if len(key) == 0:    
                        if (isinstance(v, dict)):
                            dictionary[k].update(value)
                            
                        elif (isinstance(v, list)):
                            dictionary[k][int(pos[-1])].update(value)
                    
                        elif(isinstance(v, str) and v == 'NULL'):
                            dictionary[k] = value
                        
                        return dictionary
                    
                    else:
                        p = int(pos.pop())
                        self.reverse_loop(dictionary[k][p], key, value,pos)
                else:
                    self.reverse_loop(dictionary[k], key, value,pos)
                    
        elif (isinstance(dictionary, list)):
            
            for d in dictionary:
                self.reverse_loop(d, key, value,pos)
                
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
            for key,val,pos in self.make_json(dataset, level):

                if not full_dict: # check to ensure this the first iteration and full_dict is empty
                    for i in range(len(key)):
                        full_dict[key[i][0]]= val[i]

                else:               # for iterations when full_dict already been populated with values
                    for i in range(len(key)):
                        pos[i] = [int(p) for p in pos[i]]
                        full_dict = self.reverse_loop(full_dict, key[i], val[i],pos[i])

        return full_dict

    def translate(self,ds):
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