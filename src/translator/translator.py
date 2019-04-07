import pandas as pd
import numpy as np
import yaml
import json
import pymongo
from bson.objectid import ObjectId
from validate import validator
from utilities import setup, insert_into_db, transformation
from nameko.rpc import rpc

class TranslatorService():

    name = "translator_service"
    
    @rpc
    def hello(self , parameter):
        received_param = parameter
        client = pymongo.MongoClient("mongodb://mongo:27017")
        set = setup(client)
        var = check_parameters(received_param)
        return var

def check_parameters(received_param):

    client = pymongo.MongoClient("mongodb://mongo:27017")
    set = setup(client)
    
    if received_param == "sonata_to_osm":
    
        insert = insert_into_db(client)
        ref = insert.insert_nsd('sonata')
        rcvd_file1 = set.get_source_descriptor(ref[0])
        rcvd_file2 = set.get_source_descriptor(ref[1])
        ret_translated1 = toOsm(rcvd_file1)
        ret_translated2 = toOsm(rcvd_file2)
        #trnsltd_file = set.get_source_nsd(ret_translated)
        return str(ret_translated1) + str(ret_translated2)  

    elif received_param == "osm_to_sonata":
    
        insert = insert_into_db(client)
        ref = insert.insert_nsd('osm')
        rcvd_file1 = set.get_source_descriptor(ref[0])
        rcvd_file2 = set.get_source_descriptor(ref[1])
        ret_translated1 = toSonata(rcvd_file1)
        ret_translated2 = toSonata(rcvd_file2)
        #trnsltd_file = set.get_source_nsd(ret_translated)
        return str(ret_translated1) + str(ret_translated2) 
        
def toSonata(received_file):

    client = pymongo.MongoClient("mongodb://mongo:27017")
    setup_obj = setup(client)
    
    if 'vnfd:vnfd-catalog' in received_file:
    
        doc = setup_obj.db_descriptors["translated_vnfd"]
        translated = setup_obj.translate_to_sonata_vnfd(received_file)
        check= sonata_vnfd_validate(translated)
        
        if check == "True":
            temp = doc.insert_one(translated)
            translated_ref = temp.inserted_id
            
        return str(translated) + 'validate status : ' + str(check)

    elif 'nsd:nsd-catalog' in received_file:
    
        doc = setup_obj.db_descriptors["translated_nsd"]
        translated = setup_obj.translate_to_sonata_nsd(received_file)
        check= sonata_nsd_validate(translated)
        
        if check == "True":
            temp = doc.insert_one(translated)
            translated_ref = temp.inserted_id
            
        return str(translated) + 'validate status : ' + str(check)
        
def toOsm(received_file):

    client = pymongo.MongoClient("mongodb://mongo:27017")
    setup_obj = setup(client)
    
    if 'network_functions' in received_file:
    
        doc = setup_obj.db_descriptors["translated_nsd"]
        translated = setup_obj.translate_to_osm_nsd(received_file)
        check= osm_validator(translated)
        
		if check == "True":
        temp = doc.insert_one(translated)
        translated_ref = temp.inserted_id
        
        return translated
        
    elif 'virtual_deployment_units' in received_file:
    
        doc = setup_obj.db_descriptors["translated_vnfd"]
        translated = setup_obj.translate_to_osm_vnfd(received_file)
        check= osm_validator(translated)
        
		check == "True":
        temp = doc.insert_one(translated)
        translated_ref = temp.inserted_id
        
        return translated