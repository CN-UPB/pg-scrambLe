import json
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

    
            