import pymongo
from test import check1
from pprint import pprint
from bson.objectid import ObjectId


def test(reference, parameters):
    received_ref = reference
    received_param = parameters
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["test"]
    cursor = db.list_collection_names()
    for ref in cursor:
        doc = db.get_collection(ref)
        received_file = [ns for ns in doc.find({'_id': ObjectId(received_ref)})]
        if len(received_file)>0:
            break
    var = check_parameters(received_param, received_file[0])
    return var


def check_parameters(param, file):
    received_param = param
    received_file = file
    if received_param == "sonata_to_osm":
        ret_translated = sonata(received_file)
        return ret_translated
    elif received_param == "osm_to_soanata":
        ret_translated = osm(received_file)
        return ret_translated


def sonata(file):
    received_file = file
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["test"]
    if 'eu.5gtango' and 'virtual_deployment_units' in received_file:
        doc = db["osm_vnfd"]
        translated = check1()
        temp = doc.insert_one(translated)
        translated_ref = temp.inserted_id
        return translated_ref
    elif 'eu.5gtango' and 'connection_points' in received_file:
        doc = db["osm_nsd"]
        translated = check1()
        temp = doc.insert_one(translated)
        translate_ref = temp.inserted_id
        return translate_ref


def osm(file):
    received_file = file
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["test"]
    if 'osm' and 'constituent-vnfd' in received_file:
        doc = db["sonata_nsd"]
        translated = check1()
        temp = doc.insert_one(translated)
        translated_ref = temp.inserted_id
        return translated_ref
    elif 'osm' and 'management interface' in received_file:
        doc = db["sonata_vnfd"]
        translated = check1()
        temp = doc.insert_one(translated)
        translated_ref = temp.inserted_id
        return translated_ref

