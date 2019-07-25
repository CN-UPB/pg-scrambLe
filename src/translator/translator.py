import pandas as pd
import numpy as np
import yaml
import json
import pymongo
from bson.objectid import ObjectId
from validate import validator
from utilities import setup, insert_into_db, transformation
from nameko.rpc import rpc
API_VERSION = "v1"

class TranslatorService():

    name = "translator_service"
    
    @rpc
    def hello(self,param_list):

        var = check_parameters(param_list)  
        return var
    
def check_parameters(received_param):
    
    client = pymongo.MongoClient("mongodb://mongo:27017")
    set = setup(client)
    
    param = received_param['instruction']
    
    if param == "sonata_to_osm":
    
        rcvd_file = received_param['descriptor']
        ret_translated = toOsm(rcvd_file)

    elif param == "osm_to_sonata":
    
        rcvd_file = received_param['descriptor']
        ret_translated = toSonata(rcvd_file)
    
    return ret_translated
        
def toSonata(received_file):

    client = pymongo.MongoClient("mongodb://mongo:27017")
    setup_obj = setup(client)
    validate_obj = validator()
    
    if 'vnfd:vnfd-catalog' in received_file:
    
        doc = setup_obj.db_descriptors["translated_vnfd"]
        translated = setup_obj.translate_to_sonata_vnfd(received_file)
        
        check = validate_obj.sonata_vnfd_validate(translated)
        
        if check == "True":
            temp = doc.insert_one(translated)
            translated_ref = temp.inserted_id

    elif 'nsd:nsd-catalog' in received_file:
    
        doc = setup_obj.db_descriptors["translated_nsd"]
        translated = setup_obj.translate_to_sonata_nsd(received_file)
        
        check = validate_obj.sonata_nsd_validate(translated)
        
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
        
    elif 'virtual_deployment_units' in received_file:
    
        doc = setup_obj.db_descriptors["translated_vnfd"]
        translated = setup_obj.translate_to_osm_vnfd(received_file)
        
        check= validate_obj.osm_validator(translated)
        
        if check == "True":
            temp = doc.insert_one(translated)
            translated_ref = temp.inserted_id
        
    return {"descriptor":translated ,"VALIDATE STATUS" :check}