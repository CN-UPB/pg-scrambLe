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
import docker
from dateutil import parser
import threading

import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint

from kubernetes import client, config

ATOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4ta3pqNWoiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjRmMjkzM2MyLTgxM2UtNDhhMC1hNjI5LTc0ZTZiOTIxMjZjMSIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.VpFSCZNaxeH0Ulk6xipNRso3jVvKauBkIQ5ZY92BPoCMp0JpsWwfEL1aWG1v1t863HFburIXKb7utRrXJezdb8RCmY5dnHzjhMsO_Yh92w4_ILOp2u45YFOUnFebvxc39vwXOLa-3edHkiOC6gwlZAvnU4YuEgCQ3PmAMpo5E6GQa3fIM2q6AHwtC_fecIn8IN2-RMfnBadBBGd9J2DFkzPx93aUDrjfcpOoEXjJAbxd1t2B1Bc3BpBZVr7DfAD3SsC78rP0d0cv-jTJ1Xme00Woehb70fzye8Tj4ZjxwbOM24rkeOUkPktFzjfZwOGohxA4bYEkeUmIicbXWhAf4w"
K8_URL = "https://131.234.29.11"

aConfiguration = client.Configuration()
aConfiguration.host = K8_URL

aConfiguration.verify_ssl = False
aConfiguration.api_key = {"authorization": "Bearer " + ATOKEN}

aApiClient = client.ApiClient(aConfiguration)

docker_client = docker.DockerClient(base_url='unix://container/path/docker.sock')

DOCKER_EXCLUDE = ['experiment-runner']

IDLE_SLEEP = 0.1
NS_TERMINATION_SLEEP = 10
REQUESTS_PER_MINUTE = 10
INTER_EXPERIMENT_SLEEP = 30

USERNAME = "sonata"
PASSWORD = "1234"
HOST_URL = "sonatamano.cs.upb.de"
HOST_URL_2 = "serverdemo1.cs.upb.de"

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

def set_load(host=HOST_URL, port=9000, debugscale="0.55,0.55,0.5") :
    _base_path = 'http://{0}:{1}/scale?scale_metrics={2}'.format(host, port, debugscale)

    try:
        r = requests.get(_base_path, verify=False)
        print("Scale metrics")
        print(r.text)
    except Exception as e:
        print("Scale debug could'nt be set")

def set_dockers_id(host=HOST_URL, port=9000) :
    _base_path = 'http://{0}:{1}/get_docker_names'.format(host, port)
    try:
        r = requests.get(_base_path, verify=False)
        return json.loads(r.text)
    except Exception as e:
        print("Docker Names error")


def sonata_cleanup():

    print("Sonata NSD/VNFD Cleanup")

    _token = json.loads(sonata_auth.auth(
                    username=USERNAME,
                    password=PASSWORD))
    _token = json.loads(_token["data"])

    _csd_list = json.loads(sonata_pishahang.get_csd_descriptors(
                    token=_token, limit=1000,))
    _csd_list = json.loads(_csd_list["data"])

    print(len(_csd_list))
    for _csd in _csd_list:
        sonata_pishahang.delete_csd_descriptors_csdpkgid(
                    token=_token,
                    csdpkgid=_csd['uuid'])

    _cosd_list = json.loads(sonata_pishahang.get_cosd_descriptors(
                    token=_token, limit=1000))
    _cosd_list = json.loads(_cosd_list["data"])

    print(len(_cosd_list))
    for _cosd in _cosd_list:
        sonata_pishahang.delete_cosd_descriptors_cosdpkgid(
                    token=_token,
                    cosdpkgid=_cosd['uuid'])


    sonata_pishahang_2 = SONATAClient.Pishahang(HOST_URL_2)
    sonata_auth_2 = SONATAClient.Auth(HOST_URL_2)

    _token = json.loads(sonata_auth.auth(
                    username=USERNAME,
                    password=PASSWORD))
    _token = json.loads(_token["data"])

    _csd_list = json.loads(sonata_pishahang_2.get_csd_descriptors(
                    token=_token, limit=1000,))
    _csd_list = json.loads(_csd_list["data"])

    print(len(_csd_list))
    for _csd in _csd_list:
        sonata_pishahang_2.delete_csd_descriptors_csdpkgid(
                    token=_token,
                    csdpkgid=_csd['uuid'])

    _cosd_list = json.loads(sonata_pishahang_2.get_cosd_descriptors(
                    token=_token, limit=1000))
    _cosd_list = json.loads(_cosd_list["data"])

    print(len(_cosd_list))
    for _cosd in _cosd_list:
        sonata_pishahang_2.delete_cosd_descriptors_cosdpkgid(
                    token=_token,
                    cosdpkgid=_cosd['uuid'])



    time.sleep(5)


def delete_replication_controller():

    v1 = client.CoreV1Api(aApiClient)
    ret = v1.list_namespaced_replication_controller(namespace='default', watch=False)
    for i in ret.items:
    #   print("%s\t%s" %
    #         (i.metadata.name, i.metadata.creation_timestamp))

      api_instance = client.CoreV1Api(aApiClient)
      body = client.V1DeleteOptions()
      api_response = api_instance.delete_namespaced_replication_controller(i.metadata.name, i.metadata.namespace, body=body)

def delete_pod():

    v1 = client.CoreV1Api(aApiClient)
    ret = v1.list_namespaced_pod(namespace='default', watch=False)
    for i in ret.items:
    #   print("%s\t%s" %
    #         (i.metadata.name, i.metadata.creation_timestamp))

      api_instance = client.CoreV1Api(aApiClient)
      body = client.V1DeleteOptions()
      api_response = api_instance.delete_namespaced_pod(i.metadata.name, i.metadata.namespace, body=body)

def delete_services():

    v1 = client.CoreV1Api(aApiClient)
    ret = v1.list_namespaced_service(namespace='default', watch=False)
    for i in ret.items:
    #   print("%s\t%s" %
    #         (i.metadata.name, i.metadata.creation_timestamp))

      api_instance = client.CoreV1Api(aApiClient)
      body = client.V1DeleteOptions()
      api_response = api_instance.delete_namespaced_service(i.metadata.name, i.metadata.namespace, body=body)


def get_count(init_time):

    v1 = client.CoreV1Api(aApiClient)
    print("Pod count from k8")
    _servers = v1.list_namespaced_pod(namespace='default', watch=False)

    active_count = 0
    build_count = 0
    error_count = 0

    for _s in _servers.items:
        # print(_s.status.phase)
        if int(_s.metadata.creation_timestamp.strftime("%s")) > int(init_time) :
            if _s.status.container_statuses[0].ready:
                active_count += 1
            elif _s.status.phase in ['Pending']:
                build_count += 1
            elif _s.status.phase in ['Failed', 'Unknown']:
                error_count += 1
            else:
                print("Other Status")
                print(_s.status.phase)

    return active_count, build_count, error_count


def get_individual_times(individual_init_times, folder_path, init_time, _ns_list):
    time.sleep(10)
    try:
        v1 = client.CoreV1Api(aApiClient)
        print("Listing pods with their IPs:")
        _servers = v1.list_namespaced_pod(namespace='default', watch=False)

        sonata_nslcm = SONATAClient.Nslcm(HOST_URL) 
        sonata_auth = SONATAClient.Auth(HOST_URL)

        _token = json.loads(sonata_auth.auth(
                        username=USERNAME,
                        password=PASSWORD))
        _token = json.loads(_token["data"])

        _individual_init_times = {}
        for _i, _v in individual_init_times.items():
            # service_instance_uuid
            request = json.loads(sonata_nslcm.get_ns_instances_request_status(
                                token=_token["token"]["access_token"], nsInstanceId=_i))
            request = json.loads(request["data"])

            print(request)
            _individual_init_times[request['service_instance_uuid']] = _v
            time.sleep(1)

        with open('./{nit}/individual-build-times.csv'.format(nit=nit), 'w') as _file:
            _file.write("id,mano_time,ns_mano_time,vim_time\n")
            _id = 0
            for _s in _servers.items:

                # ns_init_time = next((item for item in _ns_list if item["short-name"] == "{}-{}".format(_s.name.split("-")[0], _s.name.split("-")[1])), False)
                # if not ns_init_time:
                #     ns_init_time = 0
                # else:
                #     ns_init_time = ns_init_time['crete-time']
                # print(_s.status.container_statuses)

                server_created = _s.metadata.creation_timestamp
                launch_time = _s.status.container_statuses[0].state.running.started_at

                if int(server_created.strftime("%s")) >= int(init_time):
                    # print(server_created.strftime("%s"), nsname, individual_init_times[int(_s.name.split("-")[1])])
                    _mano_time = float(server_created.strftime("%s")) - float(_individual_init_times[_s.metadata.labels['service']])
                    ns_mano_time = float(server_created.strftime("%s")) - float(_individual_init_times[_s.metadata.labels['service']])
                    # ns_mano_time = float(server_created.strftime("%s")) - float(ns_init_time)
                    _vim_time = float(launch_time.strftime("%s")) - float(server_created.strftime("%s"))

                    print("{},{},{},{}\n".format(_id, _mano_time, ns_mano_time, _vim_time))
                    _file.write("{},{},{},{}\n".format(_id, _mano_time, ns_mano_time, _vim_time))
                    _id += 1
    
    except Exception as e:
        print(e)
        print("get_individual_times")    


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

delete_replication_controller()
delete_pod()
delete_services()
set_load(debugscale="0.4,0.4,0.4")

for _image in IMAGES:
    for _case in CASES:
        for _instances in INSTANCES:
            for _run in range(1, RUNS+1):
                print("{image}_case{case}_{instances}_Run{run}".format(image=_image, case=_case, instances=_instances, run=_run))
                # NO_INSTANCES = _instances
                NSNAME = "{image}_case{case}-{_id}"
                NSDESCRIPTION = "{image}_case{case}_{instances}_Run{run}".format(image=_image, case=_case, instances=_instances, run=_run)

                NSD_PATH = "/app/SONATA/Container/CASE{case}/{image}_case{case}_cosd_sonata.yml".format(image=_image, case=_case)
                # VNFD_PATHS = ["/app/SONATA/Descriptors/CASE{case}/{image}_vnfd.1.yml".format(image=_image, case=_case), "/app/SONATA/Descriptors/CASE{case}/{image}_vnfd.2.yml".format(image=_image, case=_case), "/app/SONATA/Descriptors/CASE{case}/{image}_vnfd.3.yml".format(image=_image, case=_case), "/app/SONATA/Descriptors/CASE{case}/{image}_vnfd.4.yml".format(image=_image, case=_case), "/app/SONATA/Descriptors/CASE{case}/{image}_vnfd.5.yml".format(image=_image, case=_case)]
                with open(NSD_PATH, 'r') as file:
                    nsd_data = file.read()

                # with open(VNFD_PATH, 'r') as file:
                #     vnfd_data = file.read()

                sonata_nsd = SONATAClient.Nsd(HOST_URL)
                sonata_pishahang = SONATAClient.Pishahang(HOST_URL)
                sonata_nslcm = SONATAClient.Nslcm(HOST_URL) 
                sonata_auth = SONATAClient.Auth(HOST_URL)
                sonata_vnfpkgm = SONATAClient.VnfPkgm(HOST_URL)

                experiment_timestamps = {}

                sonata_cleanup()

                _token = json.loads(sonata_auth.auth(
                                username=USERNAME,
                                password=PASSWORD))
                _token = json.loads(_token["data"])


                for _c in range(1, 6):
                    # for _vnfd in VNFD_PATHS:
                    VNFD_PATH = "/app/SONATA/Container/CASE{case}/{image}_csd_{vnfid}.yml".format(image=_image, case=_case, vnfid=_c)
                    _res = sonata_pishahang.post_csd_descriptors(token=_token,
                        package_path=VNFD_PATH)
                    # print(_res)
                    time.sleep(0.5)

                if IS_EXPERIMENT_VNF_INSTANCES_BASED:
                    no_instantiate = int(_instances/cases_vnfs[_case])
                else:
                    no_instantiate = _instances

                print("Instantiating {0} NS instances".format(no_instantiate))

                for i in range(0, no_instantiate):

                    with open("/tmp/" + NSNAME.format(_id=str(i), image=_image, case=_case) + "nsd.yml", "w") as _file:
                        _file.write(nsd_data.format(_id=i))

                    _res = sonata_pishahang.post_cosd_descriptors(token=_token,
                        package_path="/tmp/" + NSNAME.format(_id=str(i), image=_image, case=_case) + "nsd.yml")
                    # print(_res)
                    time.sleep(0.5)

                print("PHASE 1 : Recording idle metrics...")
                experiment_timestamps["start_time"] = int(time.time())

                time.sleep(60*IDLE_SLEEP)

                print("PHASE 2 : Starting Instantiation Sequence...")

                experiment_timestamps["ns_inst_time"] = int(time.time())

                time.sleep(5)

                _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])


                _cosd_list = json.loads(sonata_pishahang.get_cosd_descriptors(
                                    token=_token["token"]["access_token"],
                                    limit=1000))
                _cosd_list = json.loads(_cosd_list["data"])

                def createFolder(directory):
                    try:
                        if not os.path.exists(directory):
                            os.makedirs(directory)
                    except OSError:
                        print ('Error: Creating directory. ' + directory)

                nit = "{0}-{1}-PARENT".format(str(experiment_timestamps["ns_inst_time"]), NSDESCRIPTION)
                nit2 = "{0}-{1}-CHILD".format(str(experiment_timestamps["ns_inst_time"]), NSDESCRIPTION)

                createFolder("./{nit}/".format(nit=nit))
                createFolder("./{nit}/".format(nit=nit2))

                def successRatioThread():
                    TIME_OUT = 60*NS_TERMINATION_SLEEP
                    QUERY_FREQUENCY = 5
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
                                print("###")
                                
                                _file.write(_successratio)

                                if (ACTIVE_INSTANCES + ERROR_INSTANCES) == TOTAL_INSTANCES:
                                    experiment_timestamps["end_to_end_lifecycle_time"] = int(time.time())-int(experiment_timestamps["ns_inst_time"])
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

                print(len(_cosd_list))

                individual_init_times = {}

                for i in range(0, no_instantiate):
                    if (i == no_instantiate/3):
                        # Set Warning
                        set_load(debugscale="0.71,0.71,0.5")

                    if (i == no_instantiate/2):
                        # Set Load
                        set_load(debugscale="0.71,0.71,0.71")

                    _ns = None
                    for _n in _cosd_list:
                        if NSNAME.format(_id=str(i), image=_image, case=_case) == _n['cosd']['name']:            
                            _ns = _n['uuid']
                            # print("UUID")
                            # print(_ns)
                            continue

                    if _ns:
                        response = json.loads(
                                    sonata_pishahang.post_cs_instances_nsinstanceid_instantiate(
                                        token=_token["token"]["access_token"], nsInstanceId=_ns))
                        if response["error"]:
                            print("ERROR - request error")
                        else:
                            instantiation = json.loads(response["data"])
                            print(i, instantiation['id'])
                        # Store init
                        individual_init_times[instantiation['id']] = time.time()
                    else:
                        print("ERROR - no ns uuid")
                    # print(response)
                    # time.sleep(0.1) - 0.1 sleep not working with pishahang                    
                    time.sleep(60/REQUESTS_PER_MINUTE)

                # Helpers._delete_test_nsd("test_osm_cirros_2vnf_nsd")
                experiment_timestamps["ns_inst_end_time"] = int(time.time())

                print("PHASE 2 : Recording Metrics Post NS instantiation...")

                successThread.join()

                print("PHASE 3 : Starting Termination Sequence...")
                experiment_timestamps["ns_term_start_time"] = int(time.time())

                _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])

                _nsd_list = json.loads(sonata_nsd.get_ns_descriptors(
                                        token=_token["token"]["access_token"], limit=1000))
                _nsd_list = json.loads(_nsd_list["data"])

                _ns_list = json.loads(sonata_nslcm.get_ns_instances(
                                        token=_token["token"]["access_token"], limit=1000))
                _ns_list = json.loads(_ns_list["data"])

                get_individual_times(individual_init_times, nit, experiment_timestamps["ns_inst_time"], _ns_list)

                # _ns = None
                # for _n in _nsd_list:
                #     try:
                #         if NSNAME.format(_id=str(i), image=_image, case=_case) == _n['nsd']['name']:
                #             # TODO: Print status
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

# Parent 
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

                for _dName, _dId in set_dockers_id().items():                    
                    _charts["{0}-{1}".format(_dName, "cpu")] = { "url" : "http://{host}:19999/api/v1/data?chart=cgroup_{_name}.cpu&format=csv&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"], _name=_dName)}
                    _charts["{0}-{1}".format(_dName, "throttle_io")] = { "url" : "http://{host}:19999/api/v1/data?chart=cgroup_{_name}.throttle_io&format=csv&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"], _name=_dName)}
                    _charts["{0}-{1}".format(_dName, "mem_usage")] = { "url" : "http://{host}:19999/api/v1/data?chart=cgroup_{_name}.mem_usage&format=csv&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"], _name=_dName)}

                            
                        
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

# Child

                _charts = {
                    "system-cpu" : { 
                        "url": "http://{host}:19999/api/v1/data?chart=system.cpu&after={after}&before={before}&format=csv&options=nonzero".format(host=HOST_URL_2,after=experiment_timestamps["start_time"],before=experiment_timestamps["end_time"])
                    },
                    "system-load" : { 
                        "url": "http://{host}:19999/api/v1/data?chart=system.load&after={after}&before={before}&format=csv&options=nonzero".format(host=HOST_URL_2, after=experiment_timestamps['start_time'], before=experiment_timestamps["end_time"])
                    },
                    "system-ram" : { 
                        "url": "http://{host}:19999/api/v1/data?chart=system.ram&format=datasource&after={after}&before={before}&format=csv&options=nonzero".format(host=HOST_URL_2, after=experiment_timestamps['start_time'], before=experiment_timestamps["end_time"])
                    },
                    "system-net" : { 
                        "url": "http://{host}:19999/api/v1/data?chart=system.net&format=datasource&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL_2, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"])
                    },
                    "system-io" : { 
                        "url": "http://{host}:19999/api/v1/data?chart=system.io&format=datasource&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL_2, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"])
                    }
                    }

                docker_list = {}

                for _dName, _dId in set_dockers_id().items():                    
                    _charts["{0}-{1}".format(_dName, "cpu")] = { "url" : "http://{host}:19999/api/v1/data?chart=cgroup_{_name}.cpu&format=csv&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL_2, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"], _name=_dName)}
                    _charts["{0}-{1}".format(_dName, "throttle_io")] = { "url" : "http://{host}:19999/api/v1/data?chart=cgroup_{_name}.throttle_io&format=csv&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL_2, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"], _name=_dName)}
                    _charts["{0}-{1}".format(_dName, "mem_usage")] = { "url" : "http://{host}:19999/api/v1/data?chart=cgroup_{_name}.mem_usage&format=csv&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL_2, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"], _name=_dName)}

                            
                        
                for _sc, value  in _charts.items():
                    print(_sc)
                    try:
                        # TODO: make verify=false as a fallback
                        r = requests.get(value["url"], verify=False)

                        if r.status_code == requests.codes.ok:
                            print("success")

                            with open('./{nit}/{sc}.csv'.format(nit=nit2,sc=_sc), 'w') as csv_file:
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

                with open('./{nit}/end-to-end-time.csv'.format(nit=nit), 'w') as _file:
                    _file.write("end-to-end-time\n{0}".format(experiment_timestamps["end_to_end_lifecycle_time"]))
                
                print("Metrics saved in folder ./{nit}".format(nit=nit))

                print("\nhttp://{host}:9000/?host={host}&after={after}&before={before}&start_time={start_time}&ns_inst_time={ns_inst_time}&ns_inst_end_time={ns_inst_end_time}&ns_term_start_time={ns_term_start_time}&ns_term_end_time={ns_term_end_time}&end_time={end_time}&exp_description={exp_description}".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"],start_time=experiment_timestamps["start_time"],ns_inst_time=experiment_timestamps["ns_inst_time"],ns_inst_end_time=experiment_timestamps["ns_inst_end_time"],ns_term_start_time=experiment_timestamps["ns_term_start_time"],ns_term_end_time=experiment_timestamps["ns_term_end_time"],end_time=experiment_timestamps["end_time"],exp_description=NSDESCRIPTION))

                print("\nhttp://{host}:9000/interactive?host={host}&after={after}&before={before}&start_time={start_time}&ns_inst_time={ns_inst_time}&ns_inst_end_time={ns_inst_end_time}&ns_term_start_time={ns_term_start_time}&ns_term_end_time={ns_term_end_time}&end_time={end_time}&exp_description={exp_description}".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"],start_time=experiment_timestamps["start_time"],ns_inst_time=experiment_timestamps["ns_inst_time"],ns_inst_end_time=experiment_timestamps["ns_inst_end_time"],ns_term_start_time=experiment_timestamps["ns_term_start_time"],ns_term_end_time=experiment_timestamps["ns_term_end_time"],end_time=experiment_timestamps["end_time"],exp_description=NSDESCRIPTION))

                print("\n\n\n\n\n\n ENDED \n\n\n\n\n\n")
                delete_replication_controller()
                delete_pod()
                delete_services()
                set_load(debugscale="0.4,0.4,0.4")

                time.sleep(INTER_EXPERIMENT_SLEEP)