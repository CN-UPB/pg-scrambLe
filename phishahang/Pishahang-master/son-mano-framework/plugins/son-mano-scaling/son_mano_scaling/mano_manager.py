import wrappers
import json
import time
from son_mano_scaling.config import *

class ManoManager():
    def __init__(self):
        self._osm_instances = []
        self._pishahang_instances = []
        self.sonata_nslcm = wrappers.SONATAClient.Nslcm(PARENT_IP)
        self.sonata_auth = wrappers.SONATAClient.Auth(PARENT_IP)
        self.sonata_nsd = wrappers.SONATAClient.Nsd(PARENT_IP)
        self.sonata_vnfpkgm = wrappers.SONATAClient.VnfPkgm(PARENT_IP)


    def osm_check(self):
        pass

    def create_osm_instance(self):
        _token = json.loads(self.sonata_auth.auth(username=PISHAHANG_DEFAULT_USERNAME, password=PISHAHANG_DEFAULT_PASSWORD))
        _token = json.loads(_token["data"])

        self.sonata_vnfpkgm.post_vnf_packages(token=_token,
            package_path="descriptors/osm/osm-instance-vnfd.yml")
        time.sleep(3)

        self.sonata_nsd.post_ns_descriptors(token=_token,
            package_path="descriptors/osm/osm-instance-nsd.yml")
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
            print(response)
            if response["error"]:
                return False
            else:
                # TODO: wait for instantiation and get IP and return meta dict
                return response
        else:
            return False


    def create_pishahang_instance(self):
        _token = json.loads(self.sonata_auth.auth(username=PISHAHANG_DEFAULT_USERNAME, password=PISHAHANG_DEFAULT_PASSWORD))
        _token = json.loads(_token["data"])

        self.sonata_vnfpkgm.post_vnf_packages(token=_token,
            package_path="descriptors/pishahang/pishahang-instance-vnfd.yml")
        time.sleep(3)

        self.sonata_nsd.post_ns_descriptors(token=_token,
            package_path="descriptors/pishahang/pishahang-instance-nsd.yml")
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

if __name__ == "__main__":
    mano_manager = ManoManager()
    # mano_manager.create_pishahang_instance()
    mano_manager.create_osm_instance()
    _token = json.loads(mano_manager.sonata_auth.auth(username=PISHAHANG_DEFAULT_USERNAME, password=PISHAHANG_DEFAULT_PASSWORD))
    _token = json.loads(_token["data"])

    nsr_payload = json.loads(mano_manager.sonata_nslcm.get_ns_instances(token=_token["token"]["access_token"]))
    nsr_payload = json.loads(nsr_payload["data"])