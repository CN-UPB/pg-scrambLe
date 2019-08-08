from wrappers import SONATAClient 
from pytest import fixture
from .sonata_fixture import * 
from .config import *
import json
import time
from .helpers import Helpers

def test_get_csd_descriptors(get_csd_descriptors_keys):
    """Tests API call to fetch multiple NS descriptor resources"""
    sonata_pishahang = SONATAClient.Pishahang(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    
    response = json.loads(sonata_pishahang.get_csd_descriptors(
                        token=_token["token"]["access_token"], limit=1000))
    
    response = json.loads(response["data"])
    assert isinstance(response, list)
    if len(response) > 0:
        assert set(get_csd_descriptors_keys).issubset(
                    response[0].keys()), "All keys should be in the response"

def test_post_csd_descriptors(post_csd_descriptors_keys):
    """Tests API call to onboard VNF descriptor resources"""
    sonata_pishahang = SONATAClient.Pishahang(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)

    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    Helpers._delete_test_csds(_token=_token["token"]["access_token"])

    response = json.loads(sonata_pishahang.post_csd_descriptors(
                                token=_token["token"]["access_token"],
                                package_path="tests/samples/csd_example.yml"))
    print(response)
    assert response['error'] == False
    assert response['data'] != ''

def test_post_cosd_descriptors(post_cosd_descriptors_keys):
    """Tests API call to onboard NS descriptor resources"""
    sonata_pishahang = SONATAClient.Pishahang(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)

    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    Helpers._delete_test_cosds(_token=_token["token"]["access_token"])


    response = json.loads(sonata_pishahang.post_cosd_descriptors(
                        token=_token["token"]["access_token"],
                        package_path="tests/samples/cosd_example.yml"))

    assert response['error'] == False
    assert response['data'] != ''

def test_get_cosd_descriptors(get_cosd_descriptors_keys):
    """Tests API call to fetch multiple NS descriptor resources"""
    sonata_pishahang = SONATAClient.Pishahang(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(sonata_pishahang.get_cosd_descriptors(
                        token=_token["token"]["access_token"], limit=1000))
    response = json.loads(response["data"])

    assert isinstance(response, list)
    if len(response) > 0:
        assert set(get_cosd_descriptors_keys).issubset(
                    response[0].keys()), "All keys should be in the response"

def test_post_cs_instances_nsinstanceid_instantiate(post_cs_instances_nsinstanceid_instantiate_keys):
    """Tests API call to instantiate an NS"""
    sonata_pishahang = SONATAClient.Pishahang(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)

    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _cosd_list = json.loads(sonata_pishahang.get_cosd_descriptors(token=_token["token"]["access_token"]))
    _cosd_list = json.loads(_cosd_list["data"])

    _ns = None
    for _n in _cosd_list:
        if "scramble-cosd" == _n['cosd']['name']:            
            _ns = _n['uuid']

    print(_ns)
    if _ns:
        response = json.loads(
                    sonata_pishahang.post_cs_instances_nsinstanceid_instantiate(
                        token=_token["token"]["access_token"], nsInstanceId=_ns))

        print(response)
        assert response['error'] == False
        response = json.loads(response["data"])
        assert isinstance(response, dict)
        assert set(post_cs_instances_nsinstanceid_instantiate_keys).issubset(
                    response.keys()), "All keys should be in the response"
    else:
        return False

def test_post_cs_instances_nsinstanceid_terminate(post_cs_instances_nsinstanceid_terminate_keys):
    """Tests API call to instantiate an NS"""
    sonata_nslcm = SONATAClient.Nslcm(HOST_URL)
    sonata_pishahang = SONATAClient.Pishahang(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)

    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _csd_list = json.loads(sonata_pishahang.get_csd_descriptors(
                            token=_token["token"]["access_token"]))
    _csd_list = json.loads(_csd_list["data"])

    _ns_list = json.loads(sonata_nslcm.get_ns_instances(
                            token=_token["token"]["access_token"]))
    _ns_list = json.loads(_ns_list["data"])

    _ns = None
    for _n in _csd_list:
        if "scramble-csd" == _n['csd']['name']:            
            print(_n['uuid'])
            for _n2 in _ns_list:
                print(_n2)
                if _n['uuid'] == _n2['descriptor_reference']:
                    _ns = _n2['uuid']

    if _ns:
        response = json.loads(
                    sonata_pishahang.post_cs_instances_nsinstanceid_terminate(
                        token=_token["token"]["access_token"], nsInstanceId=_ns))
        assert response['error'] == False
        response = json.loads(response["data"])
        assert isinstance(response, dict)
        assert set(post_cs_instances_nsinstanceid_terminate_keys).issubset(
                    response.keys()), "All keys should be in the response"
    else:
        return False





