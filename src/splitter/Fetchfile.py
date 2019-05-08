import yaml
import pymongo
from pprint import pprint
from bson.objectid import ObjectId

def Fetchfile(ref, param):
    client = pymongo.MongoClient("mongodb://mongo:27017")
    db = client["scramble_nsd"]
    check = db[param]
    received_file = [ns for ns in check.find({'_id': ObjectId(ref)})]
    return received_file