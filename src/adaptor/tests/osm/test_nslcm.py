from wrappers import OSMClient 
from pytest import fixture
from .osm_fixture import * 
from .config import *
import json
import time
from .helpers import Helpers



def test_post_ns_instances(post_ns_instances_keys):
    """Tests API call to create a NS instance resource"""
    Helpers._delete_test_ns_instance()
    time.sleep(5) # Wait 
    osm_nslcm = OSMClient.Nslcm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(osm_nslcm.post_ns_instances(token=_token["id"],
                    nsDescription=NSDESCRIPTION,nsName= NSNAME ,nsdId= NSDID, vimAccountId= VIMACCOUNTID))
    response = json.loads(response["data"])

    assert isinstance(response, dict)
    assert set(post_ns_instances_keys).issubset(
                    response.keys()), "All keys should be in the response"
    time.sleep(5) # Wait for NS instantiation
   
                    
    

def test_get_ns_instances(get_ns_instances_keys):
    """Tests API call query multiple NS instances"""
    osm_nslcm = OSMClient.Nslcm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
    response = json.loads(response["data"])
    assert isinstance(response, list)
    if len(response) > 0:
         assert set(get_ns_instances_keys).issubset(
                    response[0].keys()), "All keys should be in the response"
    

def test_get_ns_instances_nsinstanceid():
    """Tests API call to read an individual NS instance resource"""
    Helpers._upload_test_ns_instance()
    time.sleep(5) # Wait for NS instantiation
    osm_nslcm = OSMClient.Nslcm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    _ns_list = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
    _ns_list = json.loads(_ns_list["data"])

    _ns = None
    for _n in _ns_list:
        if "test" == _n['id']:            
            _ns = _n['_id']

    response = json.loads(osm_nslcm.get_ns_instances_nsinstanceid(token=_token["id"], id=_ns))
    if response["error"]:
        return True
    else:
        return False
    

def test_delete_ns_instances_nsinstanceid(delete_ns_instances_nsinstanceid_keys):
    """Tests API call to delete NS instance resource"""
    osm_nslcm = OSMClient.Nslcm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    _ns_list = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
    _ns_list = json.loads(_ns_list["data"])

    _ns = None
    for _n in _ns_list:
        if "test" == _n['short-name']:            
            _ns = _n['_id']
    
    response = None
    if _ns:
        response = json.loads(osm_nslcm.delete_ns_instances_nsinstanceid(token=_token["id"], id=_ns))
        _rid = response["data"]
        assert isinstance(response, dict)
        assert response["data"] == _rid

        

def test_get_ns_lcm_op_ops(get_ns_lcm_op_ops_keys):
    """Tests API call to query multiple NS LCM operation occurrences"""
    Helpers._upload_test_ns_instance()
    time.sleep(5) # Wait for NS instantiation
    osm_nslcm = OSMClient.Nslcm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    _ns_list = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
    _ns_list = json.loads(_ns_list["data"])

    _ns = None
    for _n in _ns_list:
        if "test" == _n['short-name']:            
            _ns = _n['_id']

    response = json.loads(osm_nslcm.get_ns_lcm_op_ops(token=_token["id"], id=_ns))
    response = json.loads(response["data"])
    assert isinstance(response, list)
    if len(response) > 0:
         assert set(get_ns_lcm_op_ops_keys).issubset(
                    response[0].keys()), "All keys should be in the response"
    time.sleep(5)
    Helpers._delete_test_ns_instance()
    

def test_get_ns_lcm_op_ops_nslcmopoccid(get_ns_lcm_op_ops_nslcmopoccid_keys):
    """Tests API call to read an individual NS LCM operation occurrence resource"""
    osm_nslcm = OSMClient.Nslcm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    _ns_list = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
    _ns_list = json.loads(_ns_list["data"])

    _ns = None
    for _n in _ns_list:
        if "test" == _n['short-name']:            
            _ns = _n['_id']

    nslcmopocc = json.loads(osm_nslcm.get_ns_lcm_op_ops(token=_token["id"], id=_ns))
    nslcmopocc = json.loads(nslcmopocc["data"])

    _nslcmopoccid = None
    for _nslcmopocc in nslcmopocc:
        if "COMPLETED" or "FAILED"  == _nslcmopocc['operationState']:
             _nslcmopoccid = _nslcmopocc['id']

    response = json.loads(osm_nslcm.get_ns_lcm_op_ops_nslcmopoccid(token=_token["id"], id=_nslcmopoccid))
    response = json.loads(response["data"])
    assert isinstance(response, dict)
    if len(response) > 0:
        assert set(get_ns_lcm_op_ops_nslcmopoccid_keys).issubset(
                    response.keys()), "All keys should be in the response"
    time.sleep(5)
    Helpers._delete_test_ns_instance()
    



    




