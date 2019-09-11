import wrappers
import json

USERNAME = "admin"
PASSWORD = "admin"

DEL_NSD = True
DEL_VNFD = True
DEL_INSTANCES = True

HOST_URL = "manodemo3.cs.upb.de"

osm_nsd = wrappers.OSMClient.Nsd(HOST_URL)
osm_auth = wrappers.OSMClient.Auth(HOST_URL)
osm_vnfpkgm = wrappers.OSMClient.VnfPkgm(HOST_URL)
osm_nslcm = wrappers.OSMClient.Nslcm(HOST_URL) 

_token = json.loads(osm_auth.auth(
                        username=USERNAME, 
                        password=PASSWORD))

_token = json.loads(_token["data"])

if DEL_NSD:
    # Delete NSDs
    nsd_list = json.loads(osm_nsd.get_ns_descriptors(
                        token=_token["id"]))
    nsd_list = json.loads(nsd_list["data"])

    print(nsd_list)

    for _nsd in nsd_list:
        print(_nsd["_id"])    
        osm_nsd.delete_ns_descriptors_nsdinfoid(token=_token["id"], nsdinfoid=_nsd["_id"]) 

    nsd_list = json.loads(osm_nsd.get_ns_descriptors(
                        token=_token["id"]))
    nsd_list = json.loads(nsd_list["data"])

    print(nsd_list)

if DEL_VNFD:
    # Delete VNFDs

    vnf_list = json.loads(osm_vnfpkgm.get_vnf_packages(
                        token=_token["id"]))
    vnf_list = json.loads(vnf_list["data"])

    print(vnf_list)

    for _vnfd in vnf_list:
        print(_vnfd["_id"])    
        osm_vnfpkgm.delete_vnf_packages_vnfpkgid(token=_token["id"], vnfPkgId=_vnfd["_id"]) 

    vnf_list = json.loads(osm_vnfpkgm.get_vnf_packages(
                        token=_token["id"]))
    vnf_list = json.loads(vnf_list["data"])

    print(vnf_list)

if DEL_INSTANCES:
    _ns_list = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
    _ns_list = json.loads(_ns_list["data"])

    _ns = None
    for _n in _ns_list:
        try:
            _ns = _n['_id']
            if _ns:
                response = json.loads(osm_nslcm.post_ns_instances_nsinstanceid_terminate(
                                        token=_token["id"], 
                                        nsInstanceId=_ns))
                print(response)
        except Exception as e:
            pass
