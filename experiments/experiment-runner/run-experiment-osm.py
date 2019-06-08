# import wrappers
# make method which does the following, take mano as parameter

# get start time
# sleep 5 min
# get NS instantiation time
# send instantiation request to osm/sonata

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


IDLE_SLEEP = 0.1
NS_TERMINATION_SLEEP = 0.1
NO_INSTANCES = 1

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

experiment_timestamps = {}

# http://patorjk.com/software/taag/#p=display&h=1&v=1&f=ANSI%20Shadow&t=OSM%20%0AExperiment
print("""


 ██████╗ ███████╗███╗   ███╗                                                     
██╔═══██╗██╔════╝████╗ ████║                                                     
██║   ██║███████╗██╔████╔██║                                                     
██║   ██║╚════██║██║╚██╔╝██║                                                     
╚██████╔╝███████║██║ ╚═╝ ██║                                                     
 ╚═════╝ ╚══════╝╚═╝     ╚═╝                                                     
███████╗██╗  ██╗██████╗ ███████╗██████╗ ██╗███╗   ███╗███████╗███╗   ██╗████████╗
██╔════╝╚██╗██╔╝██╔══██╗██╔════╝██╔══██╗██║████╗ ████║██╔════╝████╗  ██║╚══██╔══╝
█████╗   ╚███╔╝ ██████╔╝█████╗  ██████╔╝██║██╔████╔██║█████╗  ██╔██╗ ██║   ██║   
██╔══╝   ██╔██╗ ██╔═══╝ ██╔══╝  ██╔══██╗██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║   ██║   
███████╗██╔╝ ██╗██║     ███████╗██║  ██║██║██║ ╚═╝ ██║███████╗██║ ╚████║   ██║   
╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝   
██████╗ ██╗   ██╗███╗   ██╗███╗   ██╗███████╗██████╗                             
██╔══██╗██║   ██║████╗  ██║████╗  ██║██╔════╝██╔══██╗                            
██████╔╝██║   ██║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝                            
██╔══██╗██║   ██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗                            
██║  ██║╚██████╔╝██║ ╚████║██║ ╚████║███████╗██║  ██║                            
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝                            
                                                                                 

                
""")

print("PHASE 1 : Recording 5 min of idle metrics...")
experiment_timestamps["start_time"] = int(time.time())

time.sleep(60*IDLE_SLEEP)

print("PHASE 2 : Starting Instantiation Sequence...")

experiment_timestamps["ns_inst_time"] = int(time.time())

_token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
_token = json.loads(_token["data"])

_nsd_list = json.loads(osm_nsd.get_ns_descriptors(token=_token["id"]))
_nsd_list = json.loads(_nsd_list["data"])

_nsd = None
for _n in _nsd_list:
    if nsdId == _n['id']:            
        _nsd = _n['_id']

for i in range(0, NO_INSTANCES):
    response = json.loads(osm_nslcm.post_ns_instances_nsinstanceid_instantiate(token=_token["id"],
                    nsDescription=NSDESCRIPTION, 
                    nsName=NSNAME, 
                    nsdId=_nsd, 
                    vimAccountId=VIMACCOUNTID))
    print(response)
    time.sleep(1)

# Helpers._delete_test_nsd("test_osm_cirros_2vnf_nsd")
experiment_timestamps["ns_inst_end_time"] = int(time.time())

print("PHASE 2 : Recording Metrics Post NS instantiation...")
time.sleep(60*NS_TERMINATION_SLEEP)

print("PHASE 3 : Starting Termination Sequence...")
experiment_timestamps["ns_term_start_time"] = int(time.time())

_token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
_token = json.loads(_token["data"])

_ns_list = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
_ns_list = json.loads(_ns_list["data"])

_ns = None
for _n in _ns_list:
    try:
        if nsdId == _n['nsd']['id']:            
            _ns = _n['_id']
            response = None
            if _ns:
                response = json.loads(osm_nslcm.post_ns_instances_nsinstanceid_terminate(
                                        token=_token["id"], 
                                        nsInstanceId=_ns))
                print(response)
    except Exception as e:
        pass

experiment_timestamps["ns_term_end_time"] = int(time.time())

print("PHASE 3 : Recording Metrics Post NS ...")

time.sleep(60*IDLE_SLEEP)

experiment_timestamps["end_time"] = int(time.time())                                 

print("\n ########### FINISHED ########### \n")

print("Experiment Start Time {0}".format(experiment_timestamps["start_time"]))
print("Instantiation Start Time {0}".format(experiment_timestamps["ns_inst_time"]))
print("Instantiation End Time {0}".format(experiment_timestamps["ns_inst_end_time"]))
print("Termination Start Time {0}".format(experiment_timestamps["ns_term_start_time"]))
print("Termination End Time {0}".format(experiment_timestamps["ns_term_end_time"]))
print("Experiment End Time {0}".format(experiment_timestamps["end_time"]))

# TODO: Save all the data generated into csv file
#       + Use before, after and fetch csv data from url as it is in the html file and write it to a file, named accordingly
#       + Create a folder with the "ns_inst_time" as name
#       'http://osmmano.cs.upb.de:19999/api/v1/data?chart=system.cpu&format=csv&options=nonzero'


print("PHASE 4 : Saving Metrics  ...")

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' + directory)

nit = "{0}-{1}".format(str(experiment_timestamps["ns_inst_time"]), NSDESCRIPTION)
createFolder("./{nit}/".format(nit=nit))

_charts = {
    "system-cpu" : { 
        "url": "http://{host}:19999/api/v1/data?chart=system.cpu&after={after}&before={before}&format=csv&options=nonzero".format(host=HOST_URL,after=experiment_timestamps["start_time"],before=experiment_timestamps["end_time"])
    },
    "system-load" : { 
        "url": "http://{host}:19999/api/v1/data?chart=system.load&after={after}&before={before}&format=csv&options=nonzero".format(host=HOST_URL, after=experiment_timestamps['start_time'], before=experiment_timestamps["end_time"])
    },
    "system-ram" : { 
        "url": "http://{host}:19999/api/v1/data?chart=system.ram&format=datasource&after={after}&before={before}&format=csv&options=nonzero".format(host=HOST_URL, after=experiment_timestamps['start_time'], before=experiment_timestamps["end_time"])
    },
    "system-net" : { 
        "url": "http://{host}:19999/api/v1/data?chart=system.net&format=datasource&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"])
    },
    "system-io" : { 
        "url": "http://{host}:19999/api/v1/data?chart=system.io&format=datasource&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"])
    }
    }

docker_list = {}
for _container in client.containers.list():        
    if not _container.attrs["Name"][1:] in DOCKER_EXCLUDE:
            _charts["{0}-{1}".format(_container.attrs["Name"][1:], "cpu")] = { "url" : "http://{host}:19999/api/v1/data?chart=cgroup_{_name}.cpu&format=csv&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"], _name=_container.attrs["Name"][1:])}
            _charts["{0}-{1}".format(_container.attrs["Name"][1:], "throttle_io")] = { "url" : "http://{host}:19999/api/v1/data?chart=cgroup_{_name}.throttle_io&format=csv&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"], _name=_container.attrs["Name"][1:])}
            _charts["{0}-{1}".format(_container.attrs["Name"][1:], "mem_usage")] = { "url" : "http://{host}:19999/api/v1/data?chart=cgroup_{_name}.mem_usage&format=csv&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"], _name=_container.attrs["Name"][1:])}
            
        
for _sc, value  in _charts.items():
    print(_sc)
    try:
        # TODO: make verify=false as a fallback
        r = requests.get(value["url"], verify=False)

        if r.status_code == requests.codes.ok:
            print("success")

            with open('./{nit}/{sc}.csv'.format(nit=nit,sc=_sc), 'w') as csv_file:
                csv_file.write(r.text)
        else:
            print("Failed")

    except Exception as e:
        print(str(e))


with open('./{nit}/experiment-meta.md'.format(nit=nit), 'w') as _file:
    _file.write("Experiment Start Time {0}\n".format(experiment_timestamps["start_time"]))
    _file.write("Instantiation Start Time {0}\n".format(experiment_timestamps["ns_inst_time"]))
    _file.write("Instantiation End Time {0}\n".format(experiment_timestamps["ns_inst_end_time"]))
    _file.write("Termination Start Time {0}\n".format(experiment_timestamps["ns_term_start_time"]))
    _file.write("Termination End Time {0}\n".format(experiment_timestamps["ns_term_end_time"]))
    _file.write("Experiment End Time {0}\n".format(experiment_timestamps["end_time"]))
    _file.write("\n\nhttp://{host}:9000/?host={host}&after={after}&before={before}".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"]))

print("Metrics saved in folder ./{nit}".format(nit=nit))
print("http://{host}:9000/?host={host}&after={after}&before={before}".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"]))
print("http://{host}:9000/interactive?host={host}&after={after}&before={before}".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"]))