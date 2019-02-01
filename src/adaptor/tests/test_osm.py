import vcr
import json
import time
from wrappers import OSMClient 
from pytest import fixture
from tests.osm_fixture import * 

HOST_URL = "vm-hadik3r-05.cs.uni-paderborn.de"
USERNAME = "admin"
PASSWORD = "admin"

# @vcr.use_cassette('tests/vcr_cassettes/osm/auth.yml')
def test_auth(auth_keys):
    """Tests API call to fetch Auth token"""
    osm_c = OSMClient(HOST_URL)
    response = json.loads(osm_c.auth(username=USERNAME, password=PASSWORD))
    response = json.loads(response["data"])

    assert isinstance(response, dict)
    assert set(auth_keys).issubset(
                response.keys()), "All keys should be in the response"


# @vcr.use_cassette('tests/vcr_cassettes/osm/post_ns_descriptors.yml')
def test_post_ns_descriptors(post_ns_descriptors_keys):
    """Tests API call to onboard NS descriptor resources"""
    osm_c = OSMClient(HOST_URL)
    _token = json.loads(osm_c.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(osm_c.post_ns_descriptors(token=_token["id"],
                        package_path="samples/test_osm_cirros_nsd.tar.gz"))
    response = json.loads(response["data"])

    assert isinstance(response, dict)
    assert set(post_ns_descriptors_keys).issubset(
                    response.keys()), "All keys should be in the response"

# @vcr.use_cassette('tests/vcr_cassettes/osm/get_ns_descriptors.yml')
def test_get_ns_descriptors(get_ns_descriptors_keys):
    """Tests API call to fetch multiple NS descriptor resources"""
    osm_c = OSMClient(HOST_URL)
    _token = json.loads(osm_c.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(osm_c.get_ns_descriptors(token=_token["id"]))
    response = json.loads(response["data"])

    assert isinstance(response, list)
    if len(response) > 0:
        assert set(get_ns_descriptors_keys).issubset(
                    response[0].keys()), "All keys should be in the response"

# @vcr.use_cassette('tests/vcr_cassettes/osm/delete_ns_descriptors.yml')
def test_delete_ns_descriptors(delete_ns_descriptors_keys):
    """Tests API call to delete NS descriptor resources"""
    osm_c = OSMClient(HOST_URL)
    _token = json.loads(osm_c.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _nsd_list = json.loads(osm_c.get_ns_descriptors(token=_token["id"]))
    _nsd_list = json.loads(_nsd_list["data"])

    for _n in _nsd_list:
        if "test_osm_cirros_2vnf_nsd" == _n['id']:            
            _nsd = _n['_id']

    print("ssup {0}".format(_nsd))
    time.sleep(10) # Wait for NSD onboarding
    response = json.loads(osm_c.delete_ns_descriptors(token=_token["id"], id=_nsd))

    assert isinstance(response, dict)
    assert response["data"] == ""

# clear && py.test -s tests/test_osm.py::test_post_ns_descriptors
# clear && py.test -s tests/test_osm.py::test_delete_ns_descriptors
