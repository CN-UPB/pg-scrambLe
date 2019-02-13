from wrappers.SONATAClient.nsd import Nsd
from wrappers.SONATAClient.auth import Auth
from wrappers.SONATAClient.vnfpkgm import VnfPkgm
from pytest import fixture
from .sonata_fixture import * 
from .config import *
import json
import yaml
import time
from .helpers import Helpers

def test_post_ns_descriptors(post_ns_descriptors_keys):
    """Tests API call to onboard NS descriptor resources"""
    sonata_vnfpkgm = VnfPkgm(HOST_URL)
    Helpers._delete_test_nsd()
    sonata_nsd = Nsd(HOST_URL)
    sonata_auth = Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    sonata_vnfpkgm.post_vnf_packages(token=_token["token"]["access_token"],
	package_path="samples/vnfd_example.yml")

    response = json.loads(sonata_nsd.post_ns_descriptors(token=_token["token"]["access_token"],
                        package_path="samples/nsd_example.yml"))
    #print(response)
    assert response['error'] == False
    assert response['data'] != ''

def test_get_ns_descriptors(get_ns_descriptors_keys):
    """Tests API call to fetch multiple NS descriptor resources"""
    sonata_nsd = Nsd(HOST_URL)
    sonata_auth = Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    # print(_token)
    _token = json.loads(_token["data"])

    response = json.loads(sonata_nsd.get_ns_descriptors(token=_token["token"]["access_token"]))
    response = json.loads(response["data"])

    assert isinstance(response, list)
    if len(response) > 0:
        assert set(get_ns_descriptors_keys).issubset(
                    response[0].keys()), "All keys should be in the response"

def test_delete_ns_descriptors(delete_ns_descriptors_keys):
    """Tests API call to delete NS descriptor resources"""
    sonata_vnfpkgm = VnfPkgm(HOST_URL)
    sonata_nsd = Nsd(HOST_URL)
    sonata_auth = Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    
    _nsd_list = json.loads(sonata_nsd.get_ns_descriptors(token=_token["token"]["access_token"]))
    _nsd_list = json.loads(_nsd_list["data"])
    #print(_nsd_list)
    
    _nsd = None
    for _n in _nsd_list:
        # print(_n) 
        # print("\n\n\n\n")
        # print(_n['nsd']['name'])    
        if "sonata-demo" == _n['nsd']['name']:
            
            _nsd = _n['uuid']
                   
    #print(_nsd)
    time.sleep(10) # Wait for NSD onboarding
    response = json.loads(sonata_nsd.delete_ns_descriptors(token=_token["token"]["access_token"], id=_nsd))
    assert isinstance(response, dict)
    assert response["data"] == "OK: NSD removed"
    
    time.sleep(2) #Wait for NSD onboarding

    _vnfd_list = json.loads(sonata_vnfpkgm.get_vnf_packages(token=_token["token"]["access_token"]))
    _vnfd_list = json.loads(_vnfd_list["data"])

    _vnfd = None
    for _v in _vnfd_list:
        if "vnfd_example" == _v['uuid']:            
            _vnfd = _v['uuid']

    response = None
    if _vnfd:
        response = json.loads(sonata_vnfpkgm.delete_vnf_packages_vnfpkgid(token=_token["token"]["access_token"], id=_vnfd))
        assert isinstance(response, dict)
        assert response["data"] == ""
    

def test_get_ns_descriptors_nsdinfoid():
    """Tests API call to read information about an  NS descriptor resources"""
    sonata_nsd = Nsd(HOST_URL)
    sonata_auth = Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    Helpers._upload_test_nsd()
    _nsd_list = json.loads(sonata_nsd.get_ns_descriptors(token=_token["token"]["access_token"]))
    _nsd_list = json.loads(_nsd_list["data"])

    for _n in _nsd_list:
        if "sonata-demo" == _n['nsd']['name']:
            _nsd = _n['uuid']

    response = json.loads(sonata_nsd.get_ns_descriptors(token=_token["token"]["access_token"]))
    Helpers._delete_test_nsd()
    if response["error"]:
        return True
    else:
        return False

def test_delete_ns_descriptors_nsdinfoid(delete_ns_descriptors_nsdinfoid_keys):
    """Tests API call to delete NS descriptor resources"""
    sonata_vnfpkgm = VnfPkgm(HOST_URL)
    sonata_nsd = Nsd(HOST_URL)
    sonata_auth = Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    
    _nsd_list = json.loads(sonata_nsd.get_ns_descriptors(token=_token["token"]["access_token"]))
    _nsd_list = json.loads(_nsd_list["data"])
    
    _nsd = None
    for _n in _nsd_list:
        if "sonata-demo" == _n['nsd']['name']:
            _nsd = _n['uuid']
                   
 
    time.sleep(10) # Wait for NSD onboarding
    response = json.loads(sonata_nsd.delete_ns_descriptors(token=_token["token"]["access_token"], id=_nsd))
    assert isinstance(response, dict)
    assert response["data"] == "{\"error\":\"The NSD ID None does not exist\"}"
    
    time.sleep(2) #Wait for NSD onboarding

    _vnfd_list = json.loads(sonata_vnfpkgm.get_vnf_packages(token=_token["token"]["access_token"]))
    _vnfd_list = json.loads(_vnfd_list["data"])

    _vnfd = None
    for _v in _vnfd_list:
        if "vnfd_example" == _v['uuid']:            
            _vnfd = _v['uuid']

    response = None
    if _vnfd:
        response = json.loads(sonata_vnfpkgm.delete_vnf_packages_vnfpkgid(token=_token["token"]["access_token"], id=_vnfd))
        assert isinstance(response, dict)
        assert response["data"] == ""
    

    
