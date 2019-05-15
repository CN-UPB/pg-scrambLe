import wrappers
import json

USERNAME = "admin"
PASSWORD = "admin"

HOST_URL = "vm-hadik3r-05.cs.uni-paderborn.de"

osm_nsd = wrappers.OSMClient.Nsd(HOST_URL)
osm_auth = wrappers.OSMClient.Auth(HOST_URL)
osm_vnfpkgm = wrappers.OSMClient.VnfPkgm(HOST_URL)

_token = json.loads(osm_auth.auth(
                        username=USERNAME, 
                        password=PASSWORD))

_token = json.loads(_token["data"])

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
