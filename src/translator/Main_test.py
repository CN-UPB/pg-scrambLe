import pymongo
from pprint import pprint
from Translator_main import test


client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["test"]
check = db["sonata_nsd"]

for x in check.find():
    ref = x.get('_id')
param = 'sonata_to_osm'


def to_translate():
    var = test(ref, param)
	#pprint(var)
	return var


def main():
	client = pymongo.MongoClient("mongodb://localhost:27017")
	db = client["test"]
	check = db["sonata_nsd"]

	for x in check.find():
		ref = x.get('_id')
	param = 'sonata_to_osm'
    to_translate()

if __name__ == '__main__':
    main()