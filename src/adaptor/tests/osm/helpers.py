import json
import time
from wrappers import OSMClient 
from .config import *
class Helpers():

    def _upload_test_vnf():
        osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
        osm_auth = OSMClient.Auth(HOST_URL)
        _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
        _token = json.loads(_token["data"])

        response = json.loads(osm_vnfpkgm.post_vnf_packages(token=_token["id"],
                            package_path="samples/test_osm_cirros_vnfd.tar.gz"))
        if response["error"]:
            return True
        else:
            return False

    def _delete_test_vnf(vnfname="test_osm_cirros_vnfd"):
        osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
        osm_auth = OSMClient.Auth(HOST_URL)
        _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
        _token = json.loads(_token["data"])

        _vnfd_list = json.loads(osm_vnfpkgm.get_vnf_packages(token=_token["id"]))
        _vnfd_list = json.loads(_vnfd_list["data"])

        _vnfd = None
        for _v in _vnfd_list:
            if vnfname == _v['id']:            
                _vnfd = _v['_id']

        response = None
        if _vnfd:
            response = json.loads(osm_vnfpkgm.delete_vnf_packages_vnfpkgid(token=_token["id"], id=_vnfd))

    def _upload_test_nsd():
        osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
        osm_nsd = OSMClient.Nsd(HOST_URL)
        osm_auth = OSMClient.Auth(HOST_URL)
        _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
        _token = json.loads(_token["data"])

        osm_vnfpkgm.post_vnf_packages(token=_token["id"],
             package_path="samples/test_osm_cirros_vnfd.tar.gz")

        response = json.loads(osm_nsd.post_ns_descriptors(token=_token["id"],
                        package_path="samples/test_osm_cirros_nsd.tar.gz"))
        if response["error"]:
            return True
        else:
            return False

    def _delete_test_nsd(nsdname="test_osm_cirros_2vnf_nsd"):
        osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
        osm_nsd = OSMClient.Nsd(HOST_URL)
        osm_auth = OSMClient.Auth(HOST_URL)
        _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
        _token = json.loads(_token["data"])

        _nsd_list = json.loads(osm_nsd.get_ns_descriptors(token=_token["id"]))
        _nsd_list = json.loads(_nsd_list["data"])

        _nsd = None
        for _n in _nsd_list:
            if "test_osm_cirros_2vnf_nsd" == _n['id']:            
                _nsd = _n['_id']

        time.sleep(10) # Wait for NSD onboarding
        response = json.loads(osm_nsd.delete_ns_descriptors_nsdinfoid(token=_token["id"], id=_nsd))

        time.sleep(2) # Wait for NSD onboarding

        _vnfd_list = json.loads(osm_vnfpkgm.get_vnf_packages(token=_token["id"]))
        _vnfd_list = json.loads(_vnfd_list["data"])

        _vnfd = None
        for _v in _vnfd_list:
            if nsdname == _v['id']:            
                _vnfd = _v['_id']

        response = None
        if _vnfd:
            response = json.loads(osm_vnfpkgm.delete_vnf_packages_vnfpkgid(token=_token["id"], id=_vnfd))

    def _upload_reference_vnfd_for_nsd(_referencevnfdname="hackfest1alt-vnf"):
        osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
        osm_auth = OSMClient.Auth(HOST_URL)
        _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
        _token = json.loads(_token["data"])

        if _referencevnfdname:
            response = json.loads(osm_vnfpkgm.post_vnf_packages(token=_token["id"],
                            package_path="samples/test_osm_hackfest_1alt_vnfd.tar.gz"))
        if response["error"]:
            return True
        else:
            return False

        



    
            