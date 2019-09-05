from wrappers import SONATAClient 
from pytest import fixture
from .sonata_fixture import * 
from .config import *
import json
import yaml
import time

def test_get_mano_list(get_mano_list_keys):
 
    sonata_database = SONATAClient.Database(HOST_URL)
    response = json.loads(sonata_database.get_mano_list())
    response = json.loads(response["data"])
    
    assert isinstance(response, list)
    if len(response) > 0:
        assert set(get_mano_list_keys).issubset(response[0].keys())
  
				
def test_post_mano_create(post_mano_create_keys):
    sonata_database = SONATAClient.Database(HOST_URL)
    response = json.loads(sonata_database.post_mano_create())
    response = json.loads(response["data"])
    print(response)
    assert isinstance(response, list)
    if len(response) > 0:
        assert set(post_mano_create_keys).issubset(response[0].keys())

def test_post_mano_remove(post_mano_remove_keys):
    sonata_database = SONATAClient.Database(HOST_URL)
    _mano_list = json.loads(sonata_database.get_mano_list())
    _mano_list = json.loads(_mano_list["data"])

    _mano = None
    for _m in _mano_list:
        if "mano3" == _m['name']:
            _mano = _m['_id']
            print(_mano)
    response = json.loads(sonata_database.post_mano_remove())
    if response["error"]:
        return True
    else:
        return False
	