import yaml
import pymongo
from pprint import pprint
from bson import ObjectId
from bson.objectid import ObjectId

def Fetchfile(ref, param):
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["sonata_nsd"]
    check = db["OSM_nsd"]
    parameters = param
    received_ref = ref
    cursor = db.list_collection_names()
    for x in check.find():
        reference = x.get('_id')
    for ref in cursor:
        doc = db.get_collection(ref)
        received_file = [ns for ns in doc.find({'_id': ObjectId(received_ref)})]
        if len(received_file) > 0:
            break
    print(received_file)
    return received_file
    #call splitter logic

class FetchData:

    def __init__(self, reference, parameters):
        self.parameters = parameters
        self.reference = reference
        #pprint(reference)
        #pprint(parameters)
        self.client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = self.client["sonata_nsd"]
        self.doc = self.db["OSM_nsd"]
        for x in self.doc.find({"_id": ObjectId(self.reference)}):
            self.received_file = x