from wrappers import OSMClient 
from pytest import fixture
from .osm_fixture import * 
from .config import *
import json
import time
from .helpers import Helpers

def test_get_user_list(get_user_list_keys):
    """Tests API call to get the list of users"""
    osm_admin = OSMClient.Admin(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(osm_admin.get_user_list(token=_token["id"]))
    response = json.loads(response["data"])
    assert isinstance(response, list)
    if len(response) > 0:
         assert set(get_user_list_keys).issubset(
                    response[0].keys()), "All keys should be in the response"

def test_get_user_info():
    """Tests API call to get the information about individual users"""
    osm_admin = OSMClient.Admin(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _u_list = json.loads(osm_admin.get_user_list(token=_token["id"]))
    _u_list = json.loads(_u_list["data"])

    for _u in _u_list:
        if "admin" == _u['_id']:            
            _usr = _u['_id']

    response = json.loads(osm_admin.get_user_info(token=_token["id"], id=_usr))
    if response["error"]:
            return True
    else:
            return False

def test_get_project_list(get_project_list_keys):
    """Tests API call to get the list of projects"""
    osm_admin = OSMClient.Admin(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(osm_admin.get_project_list(token=_token["id"]))
    response = json.loads(response["data"])
    assert isinstance(response, list)
    if len(response) > 0:
        assert set(get_project_list_keys).issubset(
                    response[0].keys()), "All keys should be in the response"
    
def test_get_project_info(get_project_info_keys):
    """Tests API call to get the information about individual project"""
    osm_admin = OSMClient.Admin(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _p_list = json.loads(osm_admin.get_project_list(token=_token["id"]))
    _p_list = json.loads(_p_list["data"])

    for _p in _p_list:
        if "test" == _p['_id']:            
            _project = _p['_id']

    response = json.loads(osm_admin.get_project_info(token=_token["id"], id=_project))
    if response["error"]:
            return True
    else:
            return False




    


