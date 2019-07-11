import pymongo
from bson.objectid import ObjectId


def Fetchfile(ref, param):
    client = pymongo.MongoClient("mongodb://mongo:27017")
    db = client["descriptors"]
    check = db[param]
    received_file = [ns for ns in check.find({'_id': ObjectId(ref)})]
    return received_file
