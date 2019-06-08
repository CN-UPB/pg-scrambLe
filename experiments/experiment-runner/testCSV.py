
from wrappers import OSMClient
import time
import json
import requests
from urllib.request import urlopen
import csv
import os
import docker
client = docker.DockerClient(base_url='unix://container/path/docker.sock')

DOCKER_EXCLUDE = ['experiment-runner']


IDLE_SLEEP = 1
NS_TERMINATION_SLEEP = 20
NO_INSTANCES = 100

USERNAME = "admin"
PASSWORD = "admin"

HOST_URL = "osmmano.cs.upb.de"
NSNAME = "stress_case1"
NSDESCRIPTION = "case1-100_NS"
nsdId = "stress_case1-ns"
VIMACCOUNTID = "6c74d590-aaad-4951-9200-5f1b6d8b0588"

osm_nsd = OSMClient.Nsd(HOST_URL)
osm_nslcm = OSMClient.Nslcm(HOST_URL) 
osm_auth = OSMClient.Auth(HOST_URL)

HOST_URL = "osmmano.cs.upb.de"

_token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
_token = json.loads(_token["data"])

_ns_list = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
_ns_list = json.loads(_ns_list["data"])

_ns = None
for _n in _ns_list:
    if nsdId == _n['nsd']['id']:            
        _ns = _n['_id']
        response = None
        if _ns:
            response = json.loads(osm_nslcm.post_ns_instances_nsinstanceid_terminate(
                                    token=_token["id"], 
                                    nsInstanceId=_ns))
            print(response)
            response = json.loads(response["data"])




# ---
# experiment_timestamps = {}

# experiment_timestamps["start_time"] = int(time.time())
# time.sleep(2)
# experiment_timestamps["end_time"] = int(time.time())                                 

# def createFolder(directory):
#     try:
#         if not os.path.exists(directory):
#             os.makedirs(directory)
#     except OSError:
#         print ('Error: Creating directory. ' + directory)

# nit = experiment_timestamps["start_time"]
# createFolder("./{nit}/".format(nit=nit))

# system_charts = {
#     "system.cpu" : { 
#         "url": "http://{host}:19999/api/v1/data?chart=system.cpu&after={after}&before={before}&format=csv&options=nonzero".format(host=HOST_URL,after=experiment_timestamps["start_time"],before=experiment_timestamps["end_time"])
#     },
#     "system.load" : { 
#         "url": "http://{host}:19999/api/v1/data?chart=system.load&after={after}&before={before}&format=csv&options=nonzero".format(host=HOST_URL, after=experiment_timestamps['start_time'], before=experiment_timestamps["end_time"])
#     },
#     "system.ram" : { 
#         "url": "http://{host}:19999/api/v1/data?chart=system.ram&format=datasource&after={after}&before={before}&format=csv&options=nonzero".format(host=HOST_URL, after=experiment_timestamps['start_time'], before=experiment_timestamps["end_time"])
#     },
#     "system.net" : { 
#         "url": "http://{host}:19999/api/v1/data?chart=system.net&format=datasource&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"])
#     },
#     "system.io" : { 
#         "url": "http://{host}:19999/api/v1/data?chart=system.io&format=datasource&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"])
#     }
#     }

# for _sc, value  in system_charts.items():
#     print(_sc)
#     try:
#         # TODO: make verify=false as a fallback
#         r = requests.get(value["url"], verify=False)
#     except Exception as e:
#         print(str(e))

#     if r.status_code == requests.codes.ok:
#         print("success")

#     with open('./{nit}/{sc}.csv'.format(nit=nit,sc=_sc), 'w') as csv_file:
#         csv_file.write(r.text)
                

print("http://{host}:9000/?host={host}&after={after}&before={before}".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"]))