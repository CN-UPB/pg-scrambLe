import os
import json
from flask import Flask, redirect, url_for, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
import logging

app = Flask(__name__)
CORS(app)
client = MongoClient("mongodb://db:27017")
db = client.tododb
cors = CORS(app, resources={r"/mano_create": {"origins": "*"}, r"/mano/remove": {"origins": "*"}})	

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("son-gtkmano:app")
LOG.setLevel(logging.DEBUG)

@app.route('/mano')
def todo():

	listmano = db.tododb.find()
	listmano = list(listmano)
	
	for mano in listmano:
	    mano['_id'] = str(mano['_id'])

	return json.dumps(listmano)

@app.route('/mano_create', methods=['POST'])
def new():
	content = request.get_json()
	if content:
		LOG.info("Printing Content from son-bss {}".format(str(request.data)))
		x = db.tododb.insert_one(content)
	
	return  redirect('/mano')

@app.route('/mano/remove', methods=['POST'])
def remove ():
	rec = request.get_json()
	if rec:
		LOG.info("Printing Content from son-bss {}".format(str(request.data)))
		id = rec["_id"]
		db.tododb.delete_one({"_id":ObjectId(id)})
		return "success"
	else:
		return "failure"

@app.route('/mano_uuid', methods=['POST'])
def uuid ():
	x = []
	dictionary = {}
	rec = request.get_json()
	id = rec["_id"]
	found = db.tododb.find({"_id": ObjectId(id)})
	for doc in found:
		x.append(doc)
	dlist = x
	for i , d in enumerate(dlist):
		dictionary[i] = d
	ret = dumps(dictionary)
	y = json.loads(ret)
	return y

if __name__ == "__main__":

	app.run(host='0.0.0.0', port=7001, debug=True)