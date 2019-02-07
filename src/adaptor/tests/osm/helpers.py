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

    def _delete_test_vnf():
        osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
        osm_auth = OSMClient.Auth(HOST_URL)
        _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
        _token = json.loads(_token["data"])

        _vnfd_list = json.loads(osm_vnfpkgm.get_vnf_packages(token=_token["id"]))
        _vnfd_list = json.loads(_vnfd_list["data"])

        _vnfd = None
        for _v in _vnfd_list:
            if "test_osm_cirros_vnfd" == _v['id']:            
                _vnfd = _v['_id']

        response = None
        if _vnfd:
            response = json.loads(osm_vnfpkgm.delete_vnf_packages_vnfpkgid(token=_token["id"], id=_vnfd))

    def _descriptor_update(tarf, data_path):
        # extract the package on a tmp directory
        tarf.extractall('/tmp')
        with open(data_path, 'r') as dfile:
            _data=dfile.read()
        for name in tarf.getnames():
            if name.endswith(".yaml") or name.endswith(".yml"):
                with open('/tmp/' + name, 'w') as outfile:
                    json.safe_dumps(_data, outfile, default_flow_style=False)
            break

        tarf_temp = tarfile.open('/tmp/' + tarf.getnames()[0] + ".tar.gz", "w:gz")

        for tarinfo in tarf:
            tarf_temp.add('/tmp/' + tarinfo.name, tarinfo.name, recursive=False)
        tarf_temp.close()
        return tarf
            