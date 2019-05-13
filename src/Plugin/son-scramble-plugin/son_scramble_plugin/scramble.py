"""
Copyright (c) 2015 SONATA-NFV
ALL RIGHTS RESERVED.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
Neither the name of the SONATA-NFV [, ANY ADDITIONAL AFFILIATION]
nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written
permission.
This work has been performed in the framework of the SONATA project,
funded by the European Commission under Grant number 671517 through
the Horizon 2020 and 5G-PPP programmes. The authors would like to
acknowledge the contributions of their colleagues of the SONATA
partner consortium (www.sonata-nfv.eu).a
"""

import logging
import yaml
import time
import os
import requests
import copy
import uuid
import json
import threading
import sys
import concurrent.futures as pool
import wrappers
import requests
import numpy as np
# import psutil
from osm_helpers import generatePackage
from sonmanobase.plugin import ManoBasePlugin

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("plugin:scramble")
LOG.setLevel(logging.INFO)


class ScramblePlugin(ManoBasePlugin):
    """
    This class implements the scramble plugin.
    """

    def __init__(self,
                 auto_register=True,
                 wait_for_registration=True,
                 start_running=True):
        """
        Initialize class and son-mano-base.plugin.BasePlugin class.
        This will automatically connect to the broker, contact the
        plugin manager, and self-register this plugin to the plugin
        manager.

        After the connection and registration procedures are done, the
        'on_lifecycle_start' method is called.
        :return:
        """

        # call super class (will automatically connect to
        # broker and register the Placement plugin to the plugin manger)
        ver = "0.1-dev"
        des = "This is the Scramble Plugin"

        super(self.__class__, self).__init__(version=ver,
                                             description=des,
                                             auto_register=auto_register,
                                             wait_for_registration=wait_for_registration,
                                             start_running=start_running)

    def __del__(self):
        """
        Destroy Scramble plugin instance. De-register. Disconnect.
        :return:
        """
        super(self.__class__, self).__del__()

    def declare_subscriptions(self):
        """
        Declare topics that Scramble Plugin subscribes on.
        """
        # We have to call our super class here
        super(self.__class__, self).declare_subscriptions()

        # The topic on which deploy requests are posted.
        topic = 'mano.service.place'
        self.manoconn.subscribe(self.scramble_engine, topic)

        LOG.info("Subscribed to topic: " + str(topic))

    def on_lifecycle_start(self, ch, mthd, prop, msg):
        """
        This event is called when the plugin has successfully registered itself
        to the plugin manager and received its lifecycle.start event from the
        plugin manager. The plugin is expected to do its work after this event.

        :param ch: RabbitMQ channel
        :param method: RabbitMQ method
        :param properties: RabbitMQ properties
        :param message: RabbitMQ message content
        :return:
        """
        super(self.__class__, self).on_lifecycle_start(ch, mthd, prop, msg)
        LOG.info("Scramble plugin started and operational.")

    def deregister(self):
        """
        Send a deregister request to the plugin manager.
        """
        LOG.info('Deregistering Scramble plugin with uuid ' + str(self.uuid))
        message = {"uuid": self.uuid}
        self.manoconn.notify("platform.management.plugin.deregister",
                             json.dumps(message))
        os._exit(0)

    def on_registration_ok(self):
        """
        This method is called when the Scramble plugin
        is registered to the plugin mananger
        """
        super(self.__class__, self).on_registration_ok()
        LOG.debug("Received registration ok event.")

##########################
# Scramble
##########################

    def get_network_functions(self,network_functions):
        '''
            extract the list of function ids.
        '''

        list_vnf = []
        list_vnf_nm = []
        for keyss in network_functions.keys():
            if keyss == 'network_functions':
                network_functions_data = network_functions[keyss]

                for data in network_functions_data:
                    vnf_id = data['vnf_id']
                    vnf_name = data['vnf_name']
                    list_vnf.append(vnf_id)
                    list_vnf_nm.append(vnf_name)

        return [list_vnf,list_vnf_nm]
        
        
    def random_combination(self,vnf,mano=['PISHAHANG','OSM']):
        '''
            generate a random set of function ids and MANOs. 
        '''
    
        vnf_ids = vnf[0] # get the ids of the vnf
        vnf_nm = vnf[1]  # get the names of the vnf
        
        mano_len = len(mano) # no.of MANOs
        vnf_len = len(vnf_ids) # no.of vnfs

        for random_i in np.random.choice(vnf_len,size=1,replace=False):
        
            vnf_set1 = [vnf_ids[random_i]] # storing 1st set of vnf-ids
            vnf_nm_set1 = [vnf_nm[random_i]]  # storing 1st set of vnf-names
        
        mano_set1 = [mano[random_i] for random_i in np.random.choice(mano_len,size=1,replace=False)]
        # storing 1st set of MANO
        
        vnf_set2 = list(set(vnf_ids) - set(vnf_set1)) # storing 2nd set of vnf-ids
        vnf_nm_set2 = list(set(vnf_nm) - set(vnf_nm_set1)) # storing 2nd set of vnf-names
        mano_set2 = list(set(mano) - set(mano_set1)) # storing 2nd set of MANO
        
        return [[vnf_set1,vnf_nm_set1,mano_set1 ],[vnf_set2,vnf_nm_set2,mano_set2]]
            
    def scramble_engine(self, ch, method, prop, payload):
        '''
            Scramble placement plugin to decide and split VNFs randomly among MANOs and assign and send splitted vnfs 
            to respective MANO framework.
        '''
        
        content = yaml.load(payload)
        LOG.info("Scramble plugin handling the placement request: " + content['serv_id'])

        topology = content['topology']
        descriptor = content['nsd'] if 'nsd' in content else content['cosd']
        functions = content['functions'] if 'functions' in content else []
        cloud_services = content['cloud_services'] if 'cloud_services' in content else []

        
        # create a set of vnfs for different MANO frameworks through random logic
        # Number of Splits is by default 2.
        
        function_list = self.get_network_functions(descriptor)
        random_set = self.random_combination(function_list)
        
        vnfid_set = [rndm_sets[0][0], rndm_sets[1][0]]  # vnf-ids of sets 1 and 2
        vnfname_set = [rndm_sets[0][1], rndm_sets[1][1]] # vnf-names of sets 1 and 2
        mano_set = [rndm_sets[0][2], rndm_sets[1][2]] # MANOs of sets 1 and 2
        
        # send the random vnf split to SCRAMBLE Splitter and get back sub NSDs for each split.
        splitter_url = os.environ['splitter_url']#'http://131.234.250.202:8000/Main_splitter/hello'
        nsd = { 'descriptor' : descriptor, 'sets': vnfid_set}
        
        response  = requests.post(splitter_url,data=json.dumps(nsd))
        nsds_splitted = json.loads(response.text) # get back 2 sets of sub-nsds

       
        # logic to check which vnf is to be send to which MANO
        
        function_pish =[] # list to store vnfs for PISHAHANG
        function_osm = [] # list to store vnfs for OSM
        
        for i,sets in enumerate(random_set):
        
            if sets[2] == 'PISHAHANG':
            
                for vnf in functions:
                
                    if(vnf['name'] in sets[1]):
                        function_pish.append(vnf)
                        
            elif sets[2] == 'OSM':
            
                # translating NSD to OSM
                
                translator_url = os.environ['translator_url']#'http://131.234.250.202:8000/translator/hello'
                headers = {"Content-Type": "application/json", "Accept": "application/json"}
                nsd = {"instruction": "sonata_to_osm","descriptor" : nsds_splitted['message'][i]}
                
                response  = requests.post(translator_url,data=json.dumps(nsd))
                osm_nsd = json.loads(response)
                osm_nsd = osm_nsd['message']['descriptor']
                
                # translating VNFD to OSM
                
                # getting the vnfds list from Pishahang to translate to osm
                for vnf in functions:
                
                    if(vnf['name'] in sets[1]):
                        vnfd = {"instruction": "sonata_to_osm","descriptor" : vnf}
                        response  = requests.post(translator_url,data=json.dumps(vnfd))
                        osm_vnfd = json.loads(response)
                        osm_vnfd = osm_vnfd['message']['descriptor']
                        
                        function_osm.append(osm_vnfd)
                      
        
        # creating packages
        nsd_name = osm_nsd['nsd:nsd-catalog']['nsd'][0]['name']
        generatePackage(packageType="nsd", descriptorName=nsd_name, payload=osm_nsd)
        for vnf in functions_osm:
            vnf_name = vnf['vnfd-catalog']['vnfd'][0]['name']
            generatePackage(packageType="vnfd", descriptorName=vnf_name, payload=vnf)
        
        
        # connecting to OSM to send the NS package
        username = os.environ['username']#'admin'
        password = os.environ['password']#'admin'
        host = os.environ['host_5']#'vm-hadik3r-05.cs.uni-paderborn.de'
        
        osm_auth = wrappers.OSMClient.Auth(host)
        token = json.loads(osm_auth.auth(username =username , password= password))
        _token = json.loads(token["data"])
        _token['id']

        osm_nsd_client = wrappers.OSMClient.Nsd(host)
        osm_nslcm = wrappers.OSMClient.Nslcm(HOST_URL) 
        osm_vnfpkgm = wrappers.OSMClient.VnfPkgm(host)
        
        #posting the packages to OSM
        osm_nsd_client.post_ns_descriptors(token=_token['id'],package_path="./"+nsd_name+".tar.gz")
        
        osm_vnf_names = [] # to store the osm vnf names to be used to reference VNFRs later
        
        for vnf in functions_osm:
            vnf_name = vnf['vnfd-catalog']['vnfd'][0]['name']
            osm_vnfpkgm.post_vnf_packages(token=_token["id"],package_path="./"+vnf_name+".tar.gz")
            osm_vnf_names.append(vnf_name)
        

        #instantiate the ns on OSM
        _nsd_list = json.loads(osm_nsd_client.get_ns_descriptors(token=_token["id"]))
        _nsd_list = json.loads(_nsd_list["data"])
        _nsd = None

        for _n in _nsd_list:
            if nsd_name == _n['id']:            
                _nsd = _n['_id']

        NSDESCRIPTION = '' 
        NSNAME = _nsd
        VIMACCOUNTID = ''# TODO : how to get this ??
        
        response = json.loads(osm_nslcm.post_ns_instances_nsinstanceid_instantiate(token=_token["id"],
                            nsDescription=NSDESCRIPTION, 
                            nsName=NSNAME, 
                            nsdId=_nsd, 
                            vimAccountId=VIMACCOUNTID))

        instantiate_resp = json.loads(response["data"])
        
        
        # get the VNFRs 
        
        response = json.loads(osm_nslcm.get_vnf_instances(token=_token["id"]))
        vnfr_resp = json.loads(response["data"])
        
        osm_vnfrs = [] # to store all the instantiated vnfrs
        for vnfr in vnfr_resp:
            if vnfr['vnfd-ref'] in osm_vnf_names:            
                osm_vnfrs.append(vnfr)
        
        #TODO
        # 1. map the ip address obtained in vnfr in previous step to the original vnf of PISHAHANG
        
        
        
        
        # post the vnfrs to the repository of PISHAHANG
		host = os.environ['host_8']#'vm-hadik3r-08.cs.uni-paderborn.de'
		VNFR_REPOSITORY_URL= 'http://'+host+':4002//records/vnfr/'
		son_auth = wrappers.SONATAClient.Auth(host)
		token = json.loads(son_auth.auth(username =username , password= password))
		_token = json.loads(token["data"])
		
		
        for vnfr in osm_vnfrs:
            url = VNFR_REPOSITORY_URL + 'vnf-instances/' + vnfr['id']
            header = headers={"Content-Type": "application/json", 
								'Authorization': 'Bearer {}'.format(_token['token']['access_token'])}
            vnfr_resp = requests.put(url,data=json.dumps(vnfr),
                                         headers=header)
                                         
            vnfr_resp_json = str(vnfr_resp.json())
            
            if (vnfr_resp.status_code == 200):
                msg = ": VNFR update accepted for " + vnfr['id']
                
            else:
                msg = ": VNFR update not accepted: " + vnfr_resp_json
                error = {'http_code': vnfr_resp.status_code,
                         'message': vnfr_resp_json}
                         
        
        placement = self.placement(descriptor, function_pish, cloud_services, topology) # sending only the vnfs assigned for PIshahang

        response = {'mapping': placement}
        topic = 'mano.service.place'

        self.manoconn.notify(topic,
                             yaml.dump(response),
                             correlation_id=prop.correlation_id)

        LOG.info("Scramble plugin sends Placement response for service: " + content['serv_id'])
        LOG.info(response)

    def placement(self, descriptor, functions, cloud_services, topology):
        """
        This is the default placement algorithm that is used if the SLM
        is responsible to perform the placement
        """
        LOG.info("Embedding started on following topology: " + str(topology))

        mapping = {}

        for function in functions:
            vnfd = function['vnfd']
            vdu = vnfd['virtual_deployment_units']
            needed_cpu = vdu[0]['resource_requirements']['cpu']['vcpus']
            needed_mem = vdu[0]['resource_requirements']['memory']['size']
            needed_sto = vdu[0]['resource_requirements']['storage']['size']

            for vim in topology:
                if vim['vim_type'] == 'Kubernetes':
                    continue
                cpu_req = needed_cpu <= (vim['core_total'] - vim['core_used'])
                mem_req = needed_mem <= (vim['memory_total'] - vim['memory_used'])

                if cpu_req and mem_req:
                    mapping[function['id']] = {}
                    mapping[function['id']]['vim'] = vim['vim_uuid']
                    vim['core_used'] = vim['core_used'] + needed_cpu
                    vim['memory_used'] = vim['memory_used'] + needed_mem
                    break

        for cloud_service in cloud_services:
            csd = cloud_service['csd']
            vdu = csd['virtual_deployment_units']
            needed_mem = 0
            if 'resource_requirements' in vdu[0] and 'memory' in vdu[0]['resource_requirements']:
                needed_mem = vdu[0]['resource_requirements']['memory']['size']

            for vim in topology:
                if vim['vim_type'] != 'Kubernetes':
                    continue
                mem_req = needed_mem <= (vim['memory_total'] - vim['memory_used'])

                if mem_req:
                    mapping[cloud_service['id']] = {}
                    mapping[cloud_service['id']]['vim'] = vim['vim_uuid']
                    vim['memory_used'] = vim['memory_used'] + needed_mem
                    break

        # Check if all VNFs and CSs have been mapped
        if len(mapping.keys()) == len(functions) + len(cloud_services):
            return mapping
        else:
            LOG.info("Placement was not possible")
            return None

def main():
    """
    Entry point to start plugin.
    :return:
    """
    # reduce messaging log level to have a nicer output for this plugin
    logging.getLogger("son-mano-base:messaging").setLevel(logging.INFO)
    logging.getLogger("son-mano-base:plugin").setLevel(logging.INFO)
    # logging.getLogger("amqp-storm").setLevel(logging.DEBUG)
    # create our function lifecycle manager
    scramble = ScramblePlugin()

if __name__ == '__main__':
    main()
