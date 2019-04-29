import yaml
import pymongo
from pprint import pprint
from bson import ObjectId
from bson.objectid import ObjectId

def Fetchfile(ref, param):
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["scramble_nsd"]
    check = db[param]
    #parameters = param
    received_ref = ref
    received_file = ""
    cursor = db.list_collection_names()
    for x in check.find():
        reference = x.get('_id')
    for ref in cursor:
        doc = db.get_collection(ref)
        received_file = [ns for ns in doc.find({'_id': ObjectId(received_ref)})]
        if len(received_file) > 0:
            break
    return received_file
