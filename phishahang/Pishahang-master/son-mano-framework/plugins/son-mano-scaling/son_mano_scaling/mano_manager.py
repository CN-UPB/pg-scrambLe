import wrappers
import json
import time
from son_mano_scaling.config import *

class ManoManager():
    def __init__(self):
        self._osm_instances = []
        self._pishahang_instances = []
        self.sonata_nslcm = SONATAClient.Nslcm(PARENT_IP)
        self.sonata_auth = SONATAClient.Auth(PARENT_IP)
        self.sonata_nsd = SONATAClient.Nsd(PARENT_IP)
        self.sonata_vnfpkgm = SONATAClient.VnfPkgm(PARENT_IP)

    def create_osm_instance(self):
        _token = json.loads(self.sonata_auth.auth(username=PISHAHANG_DEFAULT_USERNAME, password=PISHAHANG_DEFAULT_PASSWORD))
        _token = json.loads(_token["data"])

        self.sonata_vnfpkgm.post_vnf_packages(token=_token,
            package_path="descriptors/osm-instance-nsd.json")
        time.sleep(3)

        self.sonata_nsd.post_ns_descriptors(token=_token,
            package_path="descriptors/osm-instance-vnfd.json")
        time.sleep(3)

        _nsd_list = json.loads(self.sonata_nsd.get_ns_descriptors(token=_token["token"]["access_token"]))
        _nsd_list = json.loads(_nsd_list["data"])

        _ns = None
        for _n in _nsd_list:
            if "OSM Instance" == _n['nsd']['description']:            
                _ns = _n['uuid']

        if _ns:
            response = json.loads(
                        self.sonata_nslcm.post_ns_instances_nsinstanceid_instantiate(
                            token=_token["token"]["access_token"], nsInstanceId=_ns))

            if response["error"]:
                return False
            else:
                return True
        else:
            return False

    def osm_check(self):
        pass

    def create_pishahang_instance(self):
        _token = json.loads(self.sonata_auth.auth(username=PISHAHANG_DEFAULT_USERNAME, password=PISHAHANG_DEFAULT_PASSWORD))
        _token = json.loads(_token["data"])

        self.sonata_vnfpkgm.post_vnf_packages(token=_token,
            package_path="descriptors/pishahang-instance-nsd.json")
        time.sleep(3)

        self.sonata_nsd.post_ns_descriptors(token=_token,
            package_path="descriptors/pishahang-instance-vnfd.json")
        time.sleep(3)

        _nsd_list = json.loads(self.sonata_nsd.get_ns_descriptors(token=_token["token"]["access_token"]))
        _nsd_list = json.loads(_nsd_list["data"])

        _ns = None
        for _n in _nsd_list:
            if "Pishahang Instance" == _n['nsd']['description']:            
                _ns = _n['uuid']

        if _ns:
            response = json.loads(
                        self.sonata_nslcm.post_ns_instances_nsinstanceid_instantiate(
                            token=_token["token"]["access_token"], nsInstanceId=_ns))
            if response["error"]:
                return False
            else:
                return True
        else:
            return False

    def pishahang_check(self):
        pass
