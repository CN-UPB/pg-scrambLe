from nameko.rpc import rpc
import pandas as pd
import numpy as np
import yaml
import json
import pymongo
from bson.objectid import ObjectId

from utilities import setup, insert_into_db , transformation
import validate


class TranslatorService():
    name = "translator_service"
        
    @rpc
    def hello(self, name):
    
    
        
        client = pymongo.MongoClient("mongodb://mongo:27017/")
        set = setup(client)

        if name == 'sonata_to_osm':

            insert = insert_into_db(client)
            ref= insert.insert_nsd('sonata')
            rcvd_file = set.get_source_nsd(ref[0])
            var = set.translate_to_osm(rcvd_file)
            #trnsltd_file = set.get_source_nsd(var)
			
			
			
        elif name == 'osm_to_sonata':
            
            insert = insert_into_db(client)
            ref= insert.insert_nsd('osm')
            rcvd_file = set.get_source_nsd(ref[0])
            var = set.translate_to_sonata(rcvd_file)
            #trnsltd_file = set.get_source_nsd(var)
            
        else :
            var = 'wrong choice!!!'
            
        return str(str(rcvd_file)+'\n\n\n has been converted to \n\n\n' +str(var))#str(trnsltd_file))#

    

