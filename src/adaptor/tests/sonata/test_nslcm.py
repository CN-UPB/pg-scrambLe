from wrappers import SONATAClient 
from pytest import fixture
from .sonata_fixture import * 
from .config import *
import json
import time
from .helpers import Helpers


def test_get_ns_instances(get_ns_instances_keys):
    """Tests API call query multiple NS instances"""
    sonata_nslcm = SONATAClient.Nslcm(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    response = json.loads(sonata_nslcm.get_ns_instances(token=_token["token"]["access_token"]))
    response = json.loads(response["data"])
    assert isinstance(response, list)
    if len(response) > 0:
         assert set(get_ns_instances_keys).issubset(
                    response[0].keys()), "All keys should be in the response"

def test_get_ns_instances_nsinstanceid():
    """Tests API call to read an individual NS instance resource"""
    sonata_nslcm = SONATAClient.Nslcm(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    _ns_list = json.loads(sonata_nslcm.get_ns_instances(token=_token["token"]["access_token"]))
    _ns_list = json.loads(_ns_list["data"])

    _ns = None
    for _n in _ns_list:
        if "test" == _n['id']:            
            _ns = _n['_id']

    response = json.loads(sonata_nslcm.get_ns_instances_nsinstanceid(token=_token["token"]["access_token"], id=_ns))
    if response["error"]:
        return True
    else:
        return False


        





