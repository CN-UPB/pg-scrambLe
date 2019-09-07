import os
import json
from flask import Flask, redirect, url_for, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
import logging
import wrappers


app = Flask(__name__)
CORS(app)
client = MongoClient("mongodb://db:27017")
db = client.tododb
scramble_db = client.scrambled
cors = CORS(app, resources={r"/mano_create": {"origins": "*"}, r"/mano/remove": {"origins": "*"}, r"/scrambled_ns": {"origins": "*"}, r"/mano_uuid" : {"origins": "*"}, r'/osm/getnsr' : {"origins": "*"}, r'/pishahang/getnsr' : {"origins": "*"} })    

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
        LOG.info("Printing Content from son-bss/son-gui {}".format(str(request.data)))
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

@app.route('/nsd_uuid')
def uuid ():
    nsmano = scramble_db.functions_route.find()
    nsmano = list(nsmano)
    
    for ns in nsmano:
        ns['_id'] = str(ns['_id'])

    return json.dumps(nsmano)
    
    
@app.route('/mano_uuid', methods=['POST'])
def manouuid():

    rec = request.get_json()
    id = rec["_id"]
    LOG.info("Printing Content from son-bss {}".format(str(rec)))
    manos = db.tododb.find({"_id":ObjectId(id)})
    
    manos = list(manos)
    
    for mano in manos:
        mano['_id'] = str(mano['_id'])

    return json.dumps(manos)
    
    
@app.route('/osm/getnsr', methods=['POST'])
def scrambled_getosmnsr ():
    content = request.get_json()
    nsr_vnfr= {}
    if content:
        LOG.info("Printing Content from son-bss {}".format(str(request.data)))
        osm_details = scramble_db.functions_route.find({'nsd_uuid' : str(content['uuid'])})
        osm_details = list(osm_details)[0]
        LOG.info("Printing Content from son-bss {}".format(str(osm_details)))
        osm_host = osm_details['url']
        osm_user = osm_details['user']
        osm_pwd = osm_details['password']
        
        osm_instance_id = osm_details["ns_instantiation_id_osm"]
        
        osm_auth = wrappers.OSMClient.Auth(osm_host)
        osm_nslcm = wrappers.OSMClient.Nslcm(osm_host)
        token = json.loads(osm_auth.auth(username =osm_user , password= osm_pwd))
        _token = json.loads(token["data"])
        
        response = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
        nsrs = json.loads(response['data'])
        
        response = json.loads(osm_nslcm.get_vnf_instances(token=_token["id"]))
        vnfrs = json.loads(response['data'])
        
        
        vnfr_list=[]
        for nsr in nsrs:
            if nsr['_id'] == osm_instance_id:   
                nsr_vnfr['nsr'] = nsr
                vnfr_ids = nsr['constituent-vnfr-ref']
                for vnfr in vnfrs:
                    if vnfr['id'] in vnfr_ids:
                        vnfr_list.append(vnfr)
                nsr_vnfr['vnfr'] = vnfr_list
    return json.dumps(nsr_vnfr) 

    
@app.route('/pishahang/getnsr', methods=['POST'])
def scrambled_getpishnsr ():
    content = request.get_json()
    nsr_vnfr= {}
    if content:
        LOG.info("Printing Content from son-bss {}".format(str(request.data)))
        pish_details = scramble_db.functions_route.find({'nsd_uuid' : str(content['uuid'])})
        pish_details = list(pish_details)[0]
        LOG.info("Printing Content from son-bss {}".format(str(pish_details)))
        pish_host = pish_details['url']
        pish_user = pish_details['user']
        pish_pwd = pish_details['password']
        
        pish_instance_id = pish_details["nsd_id_pishahang"]
        
        pish_auth = wrappers.SONATAClient.Auth(pish_host)
        pish_nslcm = wrappers.SONATAClient.Nslcm(pish_host)
        token = json.loads(pish_auth.auth(username =pish_user , password= pish_pwd))
        _token = json.loads(token["data"])
        
        response = json.loads(pish_nslcm.get_ns_instances(token=_token['token']['access_token'], limit=1000))
        nsrs = json.loads(response['data'])
        
        response = json.loads(pish_nslcm.get_vnf_instances(token=_token['token']['access_token'], limit=1000))
        vnfrs = json.loads(response['data'])
        
        
        vnfr_list=[]
        for nsr in nsrs: 
            if nsr['descriptor_reference'] == pish_instance_id:   
                nsr_vnfr['nsr'] = nsr
                vnfr_ids = nsr['network_functions']
                for vnfr in vnfrs:
                    if vnfr['uuid'] in [items.get('vnfr_id') for items in vnfr_ids]:
                        vnfr_list.append(vnfr)
                nsr_vnfr['vnfr'] = vnfr_list
    return json.dumps(nsr_vnfr)
    
    
@app.route('/scrambled_ns', methods=['POST'])
def scrambled_functions ():
    content = request.get_json()
    if content:
        LOG.info("Printing Content from son-slm {}".format(str(request.data)))
        x = scramble_db.functions_route.insert_one(content)
    return str(x.inserted_id)

if __name__ == "__main__":

    app.run(host='0.0.0.0', port=7001, debug=True)