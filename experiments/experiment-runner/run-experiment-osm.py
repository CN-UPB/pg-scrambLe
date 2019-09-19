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
from dateutil import parser
import threading

from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client as nvclient

client_docker = docker.DockerClient(base_url='unix://container/path/docker.sock')

DOCKER_EXCLUDE = ['experiment-runner']


IDLE_SLEEP = 1
NS_TERMINATION_SLEEP = 30
REQUESTS_PER_MINUTE = 30
INTER_EXPERIMENT_SLEEP = 300
# NO_INSTANCES = 1

USERNAME = "admin"
PASSWORD = "admin"
HOST_URL = "osmmano.cs.upb.de"
VIMACCOUNTID = "a94aa0af-e03b-4a8c-8208-a6fb5cc223ea"

AUTH_URL = "http://127.0.0.1/identity/v3"
OS_USERNAME = "demo"
OS_PASSWORD = "123"
OS_PROJECT = "demo"

IMAGES = ["cirros", "ubuntu"]
INSTANCES = [90]
CASES = [1]
RUNS = 3

IS_EXPERIMENT_VNF_INSTANCES_BASED = True
SKIP_EXPERIMENT_IF_ERRORS = True


cases_vnfs = {
    1: 1,
    2: 3,
    3: 5
}


def get_count(init_time):
    auth = v3.Password(auth_url=AUTH_URL,
                    username=OS_USERNAME,
                    password=OS_PASSWORD,
                    project_name=OS_PROJECT,
                    user_domain_id='default',
                    project_domain_id='default')

    sess = session.Session(auth=auth)

    nova = nvclient.Client('2', session=sess)

    _servers = nova.servers.list()

    active_count = 0
    build_count = 0
    error_count = 0

    for _s in _servers:
        server_created = parser.parse(_s.created)
        if int(server_created.strftime("%s")) > int(init_time) :
            if _s.status == "ACTIVE":
                active_count += 1
            elif _s.status == "BUILD":
                build_count += 1
            elif _s.status == "ERROR":
                error_count += 1
            else:
                print("Other Status")
                print(_s.status)

    return active_count, build_count, error_count


def delete_instances():
    time.sleep(60)
    auth = v3.Password(auth_url=AUTH_URL,
                    username=OS_USERNAME,
                    password=OS_PASSWORD,
                    project_name=OS_PROJECT,
                    user_domain_id='default',
                    project_domain_id='default')

    sess = session.Session(auth=auth)

    nova = nvclient.Client('2', session=sess)

    _servers = nova.servers.list()

    for _s in _servers:
        try:
            _s.delete()
        except Exception as e:
            print(e)


def get_individual_times(individual_init_times, folder_path, init_time, _ns_list):
    auth = v3.Password(auth_url=AUTH_URL,
                    username=OS_USERNAME,
                    password=OS_PASSWORD,
                    project_name=OS_PROJECT,
                    user_domain_id='default',
                    project_domain_id='default')

    sess = session.Session(auth=auth)

    nova = nvclient.Client('2', session=sess)

    _servers = nova.servers.list()


    with open('./{nit}/individual-build-times.csv'.format(nit=nit), 'w') as _file:
        _file.write("id,mano_time,ns_mano_time,vim_time\n")

        for _s in _servers:
            ns_init_time = next((item for item in _ns_list if item["short-name"] == "{}-{}".format(_s.name.split("-")[0], _s.name.split("-")[1])), False)
            if not ns_init_time:
                ns_init_time = 0
            else:
                ns_init_time = ns_init_time['crete-time']

            server_created = parser.parse(_s.created)
            launch_time = parser.parse(_s.updated)
            if int(server_created.strftime("%s")) > int(init_time):
                # print(server_created.strftime("%s"), nsname, individual_init_times[int(_s.name.split("-")[1])])
                _mano_time = float(server_created.strftime("%s")) - float(individual_init_times[int(_s.name.split("-")[1])])
                ns_mano_time = float(server_created.strftime("%s")) - float(ns_init_time)
                _vim_time = float(launch_time.strftime("%s")) - float(server_created.strftime("%s"))

                print("{},{},{},{}\n".format(int(_s.name.split("-")[1]), _mano_time, ns_mano_time, _vim_time))
                _file.write("{},{},{},{}\n".format(int(_s.name.split("-")[1]), _mano_time, ns_mano_time, _vim_time))
    

    return

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

for _image in IMAGES:
    for _case in CASES:
        for _instances in INSTANCES:
            for _run in range(1, RUNS+1):
                print("{image}_case{case}_{instances}_Run{run}".format(image=_image, case=_case, instances=_instances, run=_run))
                # NO_INSTANCES = _instances
                NSNAME = "{image}_case{case}".format(image=_image, case=_case)
                nsdId = "{image}_case{case}-ns".format(image=_image, case=_case)
                NSDESCRIPTION = "{image}_case{case}_{instances}_Run{run}".format(image=_image, case=_case, instances=_instances, run=_run)

                print("PHASE 1 : Recording idle metrics...")
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
                
                # TODO: Calculate
                if IS_EXPERIMENT_VNF_INSTANCES_BASED:
                    no_instantiate = int(_instances/cases_vnfs[_case])
                else:
                    no_instantiate = _instances

                def createFolder(directory):
                    try:
                        if not os.path.exists(directory):
                            os.makedirs(directory)
                    except OSError:
                        print ('Error: Creating directory. ' + directory)

                nit = "{0}-{1}".format(str(experiment_timestamps["ns_inst_time"]), NSDESCRIPTION)
                createFolder("./{nit}/".format(nit=nit))

                def successRatioThread():
                    TIME_OUT = 60*NS_TERMINATION_SLEEP
                    QUERY_FREQUENCY = 10
                    COUNTER = 0

                    with open('./{nit}/success-ratio.csv'.format(nit=nit), 'w') as _file:
                        _file.write("Time,Total,Active,Build,Error\n")
                        if IS_EXPERIMENT_VNF_INSTANCES_BASED:
                            TOTAL_INSTANCES = _instances
                        else:
                            TOTAL_INSTANCES = int(cases_vnfs[_case]*_instances)

                        while(COUNTER < TIME_OUT):
                            try:
                                ACTIVE_INSTANCES, BUILD_INSTANCES, ERROR_INSTANCES = get_count(experiment_timestamps["ns_inst_time"])
                                _successratio = "{time},{total},{active},{build},{error}\n".format(
                                                    time=(int(time.time())),
                                                    total=(max(0, TOTAL_INSTANCES)),
                                                    active=(max(0, ACTIVE_INSTANCES)),
                                                    build=(max(0, BUILD_INSTANCES)),
                                                    error=(max(0, ERROR_INSTANCES)))

                                print(_successratio)
                                _file.write(_successratio)

                                if (ACTIVE_INSTANCES + ERROR_INSTANCES) == TOTAL_INSTANCES:
                                    experiment_timestamps["end_to_end_lifecycle_time"] = int(time.time())-int(experiment_timestamps["ns_inst_time"])
                                    print("{image}_case{case}_{instances}_Run{run}".format(image=_image, case=_case, instances=_instances, run=_run))
                                    print("END-TO-END Time {enetime}".format( enetime=experiment_timestamps["end_to_end_lifecycle_time"]))
                                    break
                                
                                if SKIP_EXPERIMENT_IF_ERRORS:
                                    if ERROR_INSTANCES > 0:
                                        print("Skipping Experiment Due To Errors")
                                        break

                                experiment_timestamps["end_to_end_lifecycle_time"] = int(time.time())-int(experiment_timestamps["ns_inst_time"])

                            except Exception as e:
                                print(e)
                                print("ERROR OpenStack")

                            time.sleep(QUERY_FREQUENCY)
                            COUNTER += QUERY_FREQUENCY

 
                successThread = threading.Thread(target=successRatioThread)
                successThread.start()

                individual_init_times = {}

                print("Instantiating {0} NS instances".format(no_instantiate))
                for i in range(0, no_instantiate):
                    response = json.loads(osm_nslcm.post_ns_instances_nsinstanceid_instantiate(token=_token["id"],
                                    nsDescription=NSDESCRIPTION, 
                                    nsName="{}-{}".format(NSNAME, i), 
                                    nsdId=_nsd, 
                                    vimAccountId=VIMACCOUNTID))
                    # Store init
                    individual_init_times[i] = time.time()
                    # print(response)
                    time.sleep(60/REQUESTS_PER_MINUTE)

                # Helpers._delete_test_nsd("test_osm_cirros_2vnf_nsd")
                experiment_timestamps["ns_inst_end_time"] = int(time.time())

                print("PHASE 2 : Recording Metrics Post NS instantiation...")

                successThread.join()

                print("PHASE 3 : Starting Termination Sequence...")
                experiment_timestamps["ns_term_start_time"] = int(time.time())

                _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])

                _ns_list = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
                _ns_list = json.loads(_ns_list["data"])

                get_individual_times(individual_init_times, nit, experiment_timestamps["ns_inst_time"], _ns_list)

                _ns = None
                print("Printing Status Of Instances...")
                for _n in _ns_list:
                    try:
                        if nsdId == _n['nsd']['id']:            
                            _ns = _n['_id']
                            response = None

                            if "detailed-status" in _n:
                                print(_n["detailed-status"])
                            else:
                                print("detailed-status not available")

                            if _ns:
                                response = json.loads(osm_nslcm.post_ns_instances_nsinstanceid_terminate(
                                                        token=_token["id"], 
                                                        nsInstanceId=_ns))
                                # print(response)
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
                for _container in client_docker.containers.list():        
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
                    _file.write("\nhttp://{host}:9000/interactive?host={host}&after={after}&before={before}&start_time={start_time}&ns_inst_time={ns_inst_time}&ns_inst_end_time={ns_inst_end_time}&ns_term_start_time={ns_term_start_time}&ns_term_end_time={ns_term_end_time}&end_time={end_time}&exp_description={exp_description}".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"],start_time=experiment_timestamps["start_time"],ns_inst_time=experiment_timestamps["ns_inst_time"],ns_inst_end_time=experiment_timestamps["ns_inst_end_time"],ns_term_start_time=experiment_timestamps["ns_term_start_time"],ns_term_end_time=experiment_timestamps["ns_term_end_time"],end_time=experiment_timestamps["end_time"],exp_description=NSDESCRIPTION))

                with open('./{nit}/end-to-end-time.csv'.format(nit=nit), 'w') as _file:
                    _file.write("end-to-end-time\n{0}".format(experiment_timestamps["end_to_end_lifecycle_time"]))

                print("Metrics saved in folder ./{nit}".format(nit=nit))

                print("\nhttp://{host}:9000/?host={host}&after={after}&before={before}&start_time={start_time}&ns_inst_time={ns_inst_time}&ns_inst_end_time={ns_inst_end_time}&ns_term_start_time={ns_term_start_time}&ns_term_end_time={ns_term_end_time}&end_time={end_time}&exp_description={exp_description}".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"],start_time=experiment_timestamps["start_time"],ns_inst_time=experiment_timestamps["ns_inst_time"],ns_inst_end_time=experiment_timestamps["ns_inst_end_time"],ns_term_start_time=experiment_timestamps["ns_term_start_time"],ns_term_end_time=experiment_timestamps["ns_term_end_time"],end_time=experiment_timestamps["end_time"],exp_description=NSDESCRIPTION))

                print("\nhttp://{host}:9000/interactive?host={host}&after={after}&before={before}&start_time={start_time}&ns_inst_time={ns_inst_time}&ns_inst_end_time={ns_inst_end_time}&ns_term_start_time={ns_term_start_time}&ns_term_end_time={ns_term_end_time}&end_time={end_time}&exp_description={exp_description}".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"],start_time=experiment_timestamps["start_time"],ns_inst_time=experiment_timestamps["ns_inst_time"],ns_inst_end_time=experiment_timestamps["ns_inst_end_time"],ns_term_start_time=experiment_timestamps["ns_term_start_time"],ns_term_end_time=experiment_timestamps["ns_term_end_time"],end_time=experiment_timestamps["end_time"],exp_description=NSDESCRIPTION))

                print("\n\n\n\n\n\n ENDED \n\n\n\n\n\n")
                delete_instances()
                time.sleep(INTER_EXPERIMENT_SLEEP)






