# import wrappers
# make method which does the following, take mano as parameter

# get start time
# sleep 5 min
# get NS instantiation time
# send instantiation request to osm/sonata

from wrappers import SONATAClient
import time
import json
import requests
from urllib.request import urlopen
import csv
import os
# import docker
# client = docker.DockerClient(base_url='unix://container/path/docker.sock')

# DOCKER_EXCLUDE = ['experiment-runner']


IDLE_SLEEP = 0.1
NS_TERMINATION_SLEEP = 2
NO_INSTANCES = 15

USERNAME = "sonata"
PASSWORD = "1234"

HOST_URL = "vm-hadik3r-08.cs.uni-paderborn.de"
NSNAME = "cirros_case1-{_id}"
NSDESCRIPTION = "cirros-case2-50_NS-30mins-run2"

# NSD_PATH = "/app/SONATA/Descriptors/CASE1/stress_case1_nsd.yaml"
# VNFD_PATH = "/app/SONATA/Descriptors/CASE1/stress_vnfd.yaml"

NSD_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/experiment-runner/SONATA/Descriptors/CASE1/stress_case1_nsd_sonata.yml"
VNFD_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/experiment-runner/SONATA/Descriptors/CASE1/stress_vnfd.yml"


with open(NSD_PATH, 'r') as file:
    nsd_data = file.read()


sonata_nsd = SONATAClient.Nsd(HOST_URL)
sonata_nslcm = SONATAClient.Nslcm(HOST_URL) 
sonata_auth = SONATAClient.Auth(HOST_URL)
sonata_vnfpkgm = SONATAClient.VnfPkgm(HOST_URL)

experiment_timestamps = {}


def sonata_cleanup_update():

    print("Sonata NSD/VNFD Cleanup")

    _token = json.loads(sonata_auth.auth(
                    username=USERNAME,
                    password=PASSWORD))
    _token = json.loads(_token["data"])

    nsd_list = json.loads(sonata_nsd.get_ns_descriptors(
                        token=_token["token"]["access_token"]))
    nsd_list = json.loads(nsd_list["data"])

    for _nsd in nsd_list:
        sonata_nsd.delete_ns_descriptors_nsdinfoid(
                    token=_token["token"]["access_token"],
                    nsdinfoid=_nsd["uuid"]) 

    nsd_list = json.loads(sonata_nsd.get_ns_descriptors(
                        token=_token["token"]["access_token"]))
    nsd_list = json.loads(nsd_list["data"])

    # Delete VNFDs

    vnf_list = json.loads(sonata_vnfpkgm.get_vnf_packages(
                        token=_token["token"]["access_token"]))
    vnf_list = json.loads(vnf_list["data"])

    for _vnfd in vnf_list:
        sonata_vnfpkgm.delete_vnf_packages_vnfpkgid(token=_token["token"]["access_token"], vnfPkgId=_vnfd["uuid"]) 

    vnf_list = json.loads(sonata_vnfpkgm.get_vnf_packages(
                        token=_token["token"]["access_token"]))
    vnf_list = json.loads(vnf_list["data"])

    time.sleep(5)

    _res = sonata_vnfpkgm.post_vnf_packages(token=_token,
        package_path=VNFD_PATH)
    print(_res)
    time.sleep(3)

    for i in range(0, NO_INSTANCES):
        with open("/tmp/" + NSNAME.format(_id=str(i)), "w") as _file:
            _file.write(nsd_data.format(_id=i))
            
        _res = sonata_nsd.post_ns_descriptors(token=_token,
            package_path="/tmp/" + NSNAME.format(_id=str(i)))
        print(_res)
        time.sleep(0.5)


# http://patorjk.com/software/taag/#p=display&h=1&v=1&f=ANSI%20Shadow&t=OSM%20%0AExperiment
print("""


██████╗ ██╗███████╗██╗  ██╗ █████╗ ██╗  ██╗ █████╗ ███╗   ██╗ ██████╗            
██╔══██╗██║██╔════╝██║  ██║██╔══██╗██║  ██║██╔══██╗████╗  ██║██╔════╝            
██████╔╝██║███████╗███████║███████║███████║███████║██╔██╗ ██║██║  ███╗           
██╔═══╝ ██║╚════██║██╔══██║██╔══██║██╔══██║██╔══██║██║╚██╗██║██║   ██║           
██║     ██║███████║██║  ██║██║  ██║██║  ██║██║  ██║██║ ╚████║╚██████╔╝           
╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝            
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

sonata_cleanup_update()

print("PHASE 1 : Recording idle metrics...")
experiment_timestamps["start_time"] = int(time.time())

time.sleep(60*IDLE_SLEEP)

print("PHASE 2 : Starting Instantiation Sequence...")

experiment_timestamps["ns_inst_time"] = int(time.time())

_token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
_token = json.loads(_token["data"])

_nsd_list = json.loads(sonata_nsd.get_ns_descriptors(token=_token["token"]["access_token"]))
_nsd_list = json.loads(_nsd_list["data"])

for i in range(0, NO_INSTANCES):
    _ns = None
    for _n in _nsd_list:
        if NSNAME.format(_id=str(i)) == _n['nsd']['name']:            
            _ns = _n['uuid']
            print(_ns)
            continue

    if _ns:
        response = json.loads(
                    sonata_nslcm.post_ns_instances_nsinstanceid_instantiate(
                        token=_token["token"]["access_token"], nsInstanceId=_ns))
        if response["error"]:
            print("ERROR - no ns uuid")
    else:
        print("ERROR - no ns uuid")
    #print(response)
    time.sleep(2)

# Helpers._delete_test_nsd("test_osm_cirros_2vnf_nsd")
experiment_timestamps["ns_inst_end_time"] = int(time.time())

print("PHASE 2 : Recording Metrics Post NS instantiation...")
time.sleep(60*NS_TERMINATION_SLEEP)

print("PHASE 3 : Starting Termination Sequence...")
# experiment_timestamps["ns_term_start_time"] = int(time.time())

# _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
# _token = json.loads(_token["data"])

# _nsd_list = json.loads(sonata_nsd.get_ns_descriptors(
#                         token=_token["token"]["access_token"]))
# _nsd_list = json.loads(_nsd_list["data"])

# _ns_list = json.loads(sonata_nslcm.get_ns_instances(
#                         token=_token["token"]["access_token"]))
# _ns_list = json.loads(_ns_list["data"])

# _ns = None
# for _n in _nsd_list:
#     try:
#         if NSNAME.format(_id=str(i)) == _n['nsd']['name']:
#             for _n2 in _ns_list:
#                 if _n['uuid'] == _n2['descriptor_reference']:
#                     _ns = _n2['uuid']
#                     response = json.loads(
#                                 sonata_nslcm.post_ns_instances_nsinstanceid_terminate(
#                                     token=_token["token"]["access_token"], nsInstanceId=_ns))
#     except Exception as e:
#         pass


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
    _file.write("Experiment Description {0}\n\n".format(NSDESCRIPTION))
    _file.write("Experiment Start Time {0}\n".format(experiment_timestamps["start_time"]))
    _file.write("Instantiation Start Time {0}\n".format(experiment_timestamps["ns_inst_time"]))
    _file.write("Instantiation End Time {0}\n".format(experiment_timestamps["ns_inst_end_time"]))
    _file.write("Termination Start Time {0}\n".format(experiment_timestamps["ns_term_start_time"]))
    _file.write("Termination End Time {0}\n".format(experiment_timestamps["ns_term_end_time"]))
    _file.write("Experiment End Time {0}\n".format(experiment_timestamps["end_time"]))
    _file.write("\nhttp://{host}:9000/interactive?host={host}&after={after}&before={before}&start_time={start_time}&ns_inst_time={ns_inst_time}&ns_inst_end_time={ns_inst_end_time}&ns_term_start_time={ns_term_start_time}&ns_term_end_time={ns_term_end_time}&end_time={end_time}&exp_description={exp_description}".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"],start_time=experiment_timestamps["start_time"],ns_inst_time=experiment_timestamps["ns_inst_time"],ns_inst_end_time=experiment_timestamps["ns_inst_end_time"],ns_term_start_time=experiment_timestamps["ns_term_start_time"],ns_term_end_time=experiment_timestamps["ns_term_end_time"],end_time=experiment_timestamps["end_time"],exp_description=NSDESCRIPTION))

print("Metrics saved in folder ./{nit}".format(nit=nit))

print("\nhttp://{host}:9000/?host={host}&after={after}&before={before}&start_time={start_time}&ns_inst_time={ns_inst_time}&ns_inst_end_time={ns_inst_end_time}&ns_term_start_time={ns_term_start_time}&ns_term_end_time={ns_term_end_time}&end_time={end_time}&exp_description={exp_description}".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"],start_time=experiment_timestamps["start_time"],ns_inst_time=experiment_timestamps["ns_inst_time"],ns_inst_end_time=experiment_timestamps["ns_inst_end_time"],ns_term_start_time=experiment_timestamps["ns_term_start_time"],ns_term_end_time=experiment_timestamps["ns_term_end_time"],end_time=experiment_timestamps["end_time"],exp_description=NSDESCRIPTION))

print("\nhttp://{host}:9000/interactive?host={host}&after={after}&before={before}&start_time={start_time}&ns_inst_time={ns_inst_time}&ns_inst_end_time={ns_inst_end_time}&ns_term_start_time={ns_term_start_time}&ns_term_end_time={ns_term_end_time}&end_time={end_time}&exp_description={exp_description}".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"],start_time=experiment_timestamps["start_time"],ns_inst_time=experiment_timestamps["ns_inst_time"],ns_inst_end_time=experiment_timestamps["ns_inst_end_time"],ns_term_start_time=experiment_timestamps["ns_term_start_time"],ns_term_end_time=experiment_timestamps["ns_term_end_time"],end_time=experiment_timestamps["end_time"],exp_description=NSDESCRIPTION))