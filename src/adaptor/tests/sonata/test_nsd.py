from wrappers.SONATAClient.nsd import Nsd
from wrappers.SONATAClient.auth import Auth
from wrappers.SONATAClient.vnfpkgm import VnfPkgm
from pytest import fixture
from .sonata_fixture import * 
from .config import *
import json
import yaml
import time

def test_post_ns_descriptors(post_ns_descriptors_keys):
    """Tests API call to onboard NS descriptor resources"""
    sonata_vnfpkgm = VnfPkgm(HOST_URL)
    sonata_nsd = Nsd(HOST_URL)
    sonata_auth = Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    sonata_vnfpkgm.post_vnf_packages(token=_token["token"]["access_token"],
           package_path="samples/nsd_example.yml")

    response = json.loads(sonata_nsd.post_ns_descriptors(token=_token["token"]["access_token"],
                        package_path="samples/nsd_example.yml"))
    response = json.loads(response["data"])

    assert isinstance(response, dict)
    assert set(post_ns_descriptors_keys).issubset(
                    response.keys()), "All keys should be in the response"

def test_get_ns_descriptors(get_ns_descriptors_keys):
    """Tests API call to fetch multiple NS descriptor resources"""
    sonata_nsd = Nsd(HOST_URL)
    sonata_auth = Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
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
    
    _nsd = ""
    for _n in _nsd_list:
        for k,v in _n.items():
            if k == "uuid":
                _nsd = v

    time.sleep(10) # Wait for NSD onboarding
    import pdb
    pdb.set_trace()
    response = json.loads(sonata_nsd.delete_ns_descriptors(token=_token["token"]["access_token"], id=_nsd))

    time.sleep(2) # Wait for NSD onboarding
    
    _vnfd_list = json.loads(sonata_vnfpkgm.get_vnf_packages(token=_token["token"]["access_token"]))
    _vnfd_list = json.loads(_vnfd_list["data"])

    _vnfd = None
    for _v in _vnfd_list:
        if "nsd_example" == _v['uuid']:            
            _vnfd = _v['uuid']

    response = None
    if _vnfd:
        response = json.loads(sonata_vnfpkgm.delete_vnf_packages_vnfpkgid(token=_token["token"]["access_token"], id=_vnfd))
        assert isinstance(response, dict)
        assert response["data"] == ""

    assert isinstance(response, dict)
    assert response["data"] == ""
