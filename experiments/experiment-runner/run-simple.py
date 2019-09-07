"""
A python script that can be used to instantiate a service in Pishahang remotely.
Requirements:
- Python3.6
- Pishahang's credential
- Pishahang's IP address
- The service descriptor UUID
"""


import wrappers
import json
import threading
import time

# the following 4 variables need to be populated with the right values
USERNAME = "sonata"
PASSWORD = "1234"
HOST_URL = "sonatamano.cs.upb.de"

# for _vnfd in VNFD_PATHS:
NS_NAME = "cirros_case2-{_id}"
IMAGE = "cirros"
CASE = "2"
VNFD_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/experiment-runner/SONATA/Descriptors/CASE{case}/{image}_vnfd_{vnfid}.yml"
NSD_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/experiment-runner/SONATA/Descriptors/CASE{case}/{image}_case{case}_nsd_sonata.yml".format(case=CASE, image=IMAGE)

pishahang = wrappers.SONATAClient.Auth(HOST_URL)
pishahang_nsd = wrappers.SONATAClient.Nsd(HOST_URL)
pishahang_nslcm = wrappers.SONATAClient.Nslcm(HOST_URL)
pishahang_vnfpkgm = wrappers.SONATAClient.VnfPkgm(HOST_URL)



# def sonata_cleanup():

#     print("Sonata NSD/VNFD Cleanup")

#     _token = json.loads(pishahang.auth(
#                     username=USERNAME,
#                     password=PASSWORD))
#     _token = json.loads(_token["data"])

#     nsd_list = json.loads(pishahang_nsd.get_ns_descriptors(
#                         token=_token["token"]["access_token"], limit=1000))
#     nsd_list = json.loads(nsd_list["data"])

#     print(len(nsd_list))
#     for _nsd in nsd_list:
#         pishahang_nsd.delete_ns_descriptors_nsdinfoid(
#                     token=_token["token"]["access_token"],
#                     nsdinfoid=_nsd["uuid"]) 

#     nsd_list = json.loads(pishahang_nsd.get_ns_descriptors(
#                         token=_token["token"]["access_token"]))
#     nsd_list = json.loads(nsd_list["data"])

#     # Delete VNFDs

#     vnf_list = json.loads(pishahang_vnfpkgm.get_vnf_packages(
#                         token=_token["token"]["access_token"], limit=1000))
#     vnf_list = json.loads(vnf_list["data"])

#     for _vnfd in vnf_list:
#         pishahang_vnfpkgm.delete_vnf_packages_vnfpkgid(token=_token["token"]["access_token"], vnfPkgId=_vnfd["uuid"]) 

#     vnf_list = json.loads(pishahang_vnfpkgm.get_vnf_packages(
#                         token=_token["token"]["access_token"]))
#     vnf_list = json.loads(vnf_list["data"])

#     time.sleep(5)


# sonata_cleanup()

# extracting the token
token = json.loads(pishahang.auth(username=USERNAME, password=PASSWORD))
token = json.loads(token["data"])


# for _c in range(1, 6):
#     # for _vnfd in VNFD_PATHS:
#     _VNFD_PATH = VNFD_PATH.format(image=IMAGE, case=CASE, vnfid=_c)
#     _res = pishahang_vnfpkgm.post_vnf_packages(token=token,
#         package_path=_VNFD_PATH)
#     print(_res)
#     time.sleep(0.5)


# _res = pishahang_nsd.post_ns_descriptors(token=token,
#         package_path=NSD_PATH)
# print(_res)

# time.sleep(2)

_nsd_list = json.loads(pishahang_nsd.get_ns_descriptors(token=token["token"]["access_token"], limit=1000))
_nsd_list = json.loads(_nsd_list["data"])

NS_UUID  = "UUID"

for _n in _nsd_list:
    if NS_NAME == _n['nsd']['name']:            
        NS_UUID = _n['uuid']
        print("UUID")
        print(NS_UUID)
        break


# calling the service instantiation API 
instantiation = json.loads(pishahang_nslcm.post_ns_instances_nsinstanceid_instantiate(
                           token=token["token"]["access_token"], nsInstanceId=NS_UUID))
instantiation = json.loads(instantiation["data"])
print ("Service instantiation request has been sent!")


# extracting the request id
_rq_id = instantiation["id"]

# checking the service instantiation status
counter, timeout, sleep_interval = 0, 60, 2

while counter < timeout:

    #calling the request API
    request = json.loads(pishahang_nslcm.get_ns_instances_request_status(
                         token=token["token"]["access_token"], nsInstanceId=_rq_id))
    request = json.loads(request["data"])

    # checking if the call was successful
    try:
        request_status = request["status"]
    except:
        print ("Error in request status chaeking!")
        break

    # checking if the instantiation was successful
    if request["status"] == "ERROR":
        print ("Error in service instantiation")
        break
    elif request["status"] == "READY":
        print (request["status"] + " : Service has been successfully instantiated!")
        break

    # printing the current status and sleep
    print (request["status"] + "...")
    time.sleep(sleep_interval)
    counter += sleep_interval

if counter > timeout:
    print ("Error: service instantiation remained incomplete")