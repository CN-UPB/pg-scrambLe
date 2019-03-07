import pandas as pd
import numpy as np
import yaml
import json
import pymongo
from bson.objectid import ObjectId
from validate import validate
from utilities import setup, insert_into_db, transformation
from nameko.rpc import rpc


class TranslatorService():
    name = "translator_service"
	
	@rpc
    def hello(self , parameter):
        received_param = parameter
        client = pymongo.MongoClient("mongodb://localhost:27017")
        set = setup(client)
        var = check_parameters(received_param)
        return var


def check_parameters(param):
    client = pymongo.MongoClient("mongodb://localhost:27017")
    set = setup(client)
    received_param = param
    if received_param == "sonata_to_osm":
        insert = insert_into_db(client)
        ref = insert.insert_nsd('sonata')
        rcvd_file = set.get_source_nsd(ref)
        ret_translated = sonata(rcvd_file)
        trnsltd_file = set.get_source_nsd(ret_translated)
        return str(str(rcvd_file) + '\n\n\n has been converted to \n\n\n' + str(trnsltd_file))  # str(var)#

    elif received_param == "osm_to_soanata":
        insert = insert_into_db(client)
        ref = insert.insert_nsd('osm')
        rcvd_file = set.get_source_nsd(ref)
        ret_translated = osm(rcvd_file)
        trnsltd_file = set.get_source_nsd(ret_translated)
        return str(str(rcvd_file) + '\n\n\n has been converted to \n\n\n' + str(trnsltd_file))  # str(var)#


def sonata(file):
    received_file = file
    client = pymongo.MongoClient("mongodb://localhost:27017")
    set = setup(client)
    if 'eu.5gtango' and 'virtual_deployment_units' in received_file:
        doc = set.db_descriptors["translated_vnfd"]
        translated = setup.translate_to_osm(received_file)
        check = validate(received_file, translated)
        if check == "True":
            temp = doc.insert_one(translated)
            translated_ref = temp.inserted_id
            return translated_ref

    elif 'eu.5gtango' and 'connection_points' in received_file:
        doc = set.db_descriptors["translated_nsd"]
        translated = setup.translate_to_osm(received_file)
        check = validate(received_file, translated)
        if check == "True":
            temp = doc.insert_one(translated)
            translated_ref = temp.inserted_id
            return translated_ref


def osm(file):
    client = pymongo.MongoClient("mongodb://localhost:27017")
    set = setup(client)
    received_file = file
    if 'osm' and 'constituent-vnfd' in received_file:
        doc = set.db_descriptors["translated_nsd"]
        translated = setup.translate_to_sonata(received_file)
        check = validate(received_file , translated)
        if check == "True":
            temp = doc.insert_one(translated)
            translated_ref = temp.inserted_id
            return translated_ref
    elif 'osm' and 'management interface' in received_file:
        doc = set.db_descriptors["translated_vnfd"]
        translated = setup.translate_to_sonata(received_file)
        check = validate(received_file , translated)
        if check == "True":
            temp = doc.insert_one(translated)
            translated_ref = temp.inserted_id
            return translated_ref
    
   
            
       

    

