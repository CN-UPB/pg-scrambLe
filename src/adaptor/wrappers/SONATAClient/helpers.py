import json
from wrappers import SONATAClient 
from wrappers.SONATAClient.auth import Auth
from wrappers.SONATAClient.vnfpkgm import VnfPkgm
from wrappers.SONATAClient.nsd import Nsd
from tests.sonata.config import *
import time
class Helpers():

    def _upload_test_vnf():
        sonata_vnfpkgm = SONATAClient.VnfPkgm(HOST_URL)
        sonata_auth = SONATAClient.Auth(HOST_URL)
        _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
        _token = json.loads(_token["data"])

        response = json.loads(sonata_vnfpkgm.post_vnf_packages(token=_token["token"]["access_token"],
                            package_path="samples/vnfd_example.yml"))
        
        if response["error"]:
            return True
        else:
            return False

    def _delete_test_vnf(vnfname="vnfd_example"):
        sonata_vnfpkgm = SONATAClient.VnfPkgm(HOST_URL)
        sonata_auth = SONATAClient.Auth(HOST_URL)
        _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
        _token = json.loads(_token["data"])

        _vnfd_list = json.loads(sonata_vnfpkgm.get_vnf_packages(token=_token["token"]["access_token"]))
        _vnfd_list = json.loads(_vnfd_list["data"])

        _vnfd = None
        for _v in _vnfd_list:
            if "vnfd_example" == _v['uuid']:            
                _vnfd = _v['uuid']

        response = None
        if _vnfd:
            response = json.loads(sonata_vnfpkgm.delete_vnf_packages_vnfpkgid(token=_token["token"]["access_token"], id=_vnfd))

                
    def _delete_test_nsd(nsdname="sonata-demo"):
        sonata_vnfpkgm = SONATAClient.VnfPkgm(HOST_URL)
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

        time.sleep(10)
        response = json.loads(sonata_nsd.delete_ns_descriptors(token=_token["token"]["access_token"], id=_nsd))

        time.sleep(2)

        _vnfd_list = json.loads(sonata_vnfpkgm.get_vnf_packages(token=_token["token"]["access_token"]))
        _vnfd_list = json.loads(_vnfd_list["data"])

        _vnfd = None
        for _v in _vnfd_list:
            if "vnfd_example" == _v['uuid']:            
                _vnfd = _v['uuid']

        response = None
        if _vnfd:
            response = json.loads(sonata_vnfpkgm.delete_vnf_packages_vnfpkgid(token=_token["token"]["access_token"], id=_vnfd))