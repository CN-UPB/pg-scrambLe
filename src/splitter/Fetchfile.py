import pymongo
from pprint import pprint
from bson import ObjectId

class FetchData:

    def __init__(self, reference, parameters):
        self.parameters = parameters
        self.reference = reference
        #pprint(reference)
        #pprint(parameters)
        self.client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = self.client["sonata_nsd"]
        self.doc = self.db["sonata_nsd"]
        for x in self.doc.find({"_id": ObjectId(self.reference)}):
            self.received_file = x
        pprint(self.received_file)


