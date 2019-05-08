import pandas as pd
import numpy as np
import yaml
import json
import pymongo
from bson.objectid import ObjectId
from validate import validator
from utilities import setup, insert_into_db, transformation
from nameko.rpc import rpc
from flask import Flask, request

app = Flask(__name__)


class TranslatorService():

    name = "translator_service"
    
    @rpc
    def hello(self,name):
        #descriptor = request.values.get('descriptor')
        #received_param = name#request.values.get('param')
        #client = pymongo.MongoClient("mongodb://mongo:27017")
        #set = setup(client)
        var = check_parameters(name)  
        return var
    
def check_parameters(received_param):

    client = pymongo.MongoClient("mongodb://mongo:27017")
    set = setup(client)
    
    param=received_param['instruction']
    if param == "sonata_to_osm":
    
        #insert = insert_into_db(client)
        #ref = insert.insert_nsd('sonata')
        rcvd_file1 = received_param['descriptor']#set.get_source_descriptor(ref[0])
        #rcvd_file2 = set.get_source_descriptor(ref[1])
        ret_translated1 = toOsm(rcvd_file1)
        #ret_translated2 = toOsm(rcvd_file2)
        #trnsltd_file = set.get_source_nsd(ret_translated)
        return ret_translated1 #+ json.dumps(ret_translated2)

    elif param == "osm_to_sonata":
    
        #insert = insert_into_db(client)
        #ref = insert.insert_nsd('osm')
        rcvd_file1 = received_param['descriptor']#set.get_source_descriptor(ref[0])
        #rcvd_file2 = set.get_source_descriptor(ref[1])
        ret_translated1 = toSonata(rcvd_file1)
        #ret_translated2 = toSonata(rcvd_file2)
        #trnsltd_file = set.get_source_nsd(ret_translated)
        return ret_translated1 #+ json.dumps(ret_translated2)
        
def toSonata(received_file):

    client = pymongo.MongoClient("mongodb://mongo:27017")
    setup_obj = setup(client)
    validate_obj = validator()
    
    if 'vnfd:vnfd-catalog' in received_file:
    
        doc = setup_obj.db_descriptors["translated_vnfd"]
        translated = setup_obj.translate_to_sonata_vnfd(received_file)
        
        check= validate_obj.sonata_vnfd_validate(translated)
        
        if check == "True":
            temp = doc.insert_one(translated)
            translated_ref = temp.inserted_id
            
        return {"descriptor":translated ,"VALIDATE STATUS" :check}

    elif 'nsd:nsd-catalog' in received_file:
    
        doc = setup_obj.db_descriptors["translated_nsd"]
        translated = setup_obj.translate_to_sonata_nsd(received_file)
        check= validate_obj.sonata_nsd_validate(translated)
        
        if check == "True":
            temp = doc.insert_one(translated)
            translated_ref = temp.inserted_id
            
        return {"descriptor":translated ,"VALIDATE STATUS" :check}
        
def toOsm(received_file):

    client = pymongo.MongoClient("mongodb://mongo:27017")
    setup_obj = setup(client)
    validate_obj = validator()
    
    if 'network_functions' in received_file:
    
        doc = setup_obj.db_descriptors["translated_nsd"]
        translated = setup_obj.translate_to_osm_nsd(received_file)
        check= validate_obj.osm_validator(translated)
        
        if check == "True":
            temp = doc.insert_one(translated)
            translated_ref = temp.inserted_id
        
        return {"descriptor":translated ,"VALIDATE STATUS" :check}
        
    elif 'virtual_deployment_units' in received_file:
    
        doc = setup_obj.db_descriptors["translated_vnfd"]
        translated = setup_obj.translate_to_osm_vnfd(received_file)
        check= validate_obj.osm_validator(translated)
        
        if check == "True":
            temp = doc.insert_one(translated)
            translated_ref = temp.inserted_id
        
        return {"descriptor":translated ,"VALIDATE STATUS" :check}
        
#if __name__ == '__main__':
#    app.debug = True
#    app.run()
#    app.run(debug=True)
