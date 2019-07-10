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
import psutil
import concurrent.futures as pool
import re
import wrappers

from son_mano_scaling.config import *
from sonmanobase.plugin import ManoBasePlugin
from son_mano_scaling.mano_manager import ManoManager

# TODO: Make NSD/VNFD for scaling instances

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("plugin:scaling")
LOG.setLevel(logging.INFO)


class ScalingPlugin(ManoBasePlugin):
    """
    This class implements the Pishahang scaling manager.
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
        # broker and register the Scaling plugin to the plugin manger)
        ver = "0.1-dev"
        des = "Scaling plugin"
        self.DEBUGMODE = True
        self.mano_manager = ManoManager()
        self.instantiating_mano_instance = False
        self.terminating_mano_instance = False
        self.child_mano_added = False
        self.parent_mano_loaded = False
        # TODO: store a list of MANO instances
        self.mano_instances = []
        self.parent_mano = {
            "host_ip":PARENT_IP,
            "monitoring_port": NETDATA_PORT,
            "username":"",
            "password":"",
            "type":"pishahang"
        }

        super(self.__class__, self).__init__(version=ver,
                                             description=des,
                                             auto_register=auto_register,
                                             wait_for_registration=wait_for_registration,
                                             start_running=start_running)

    @run_async
    def create_mano_instance(self, mano_type="pishahang"):
        """
        Instantiate a new MANO instance
        """
        # TODO: 1) send instantiation request for new MANO Instance
        #       2) monitor and find if the instance is ready and get IP address
        #       3) add instance to the list
        LOG.info(">>>> \n Creating MANO instance...")
        self.instantiating_mano_instance = True
        
        if mano_type == "pishahang":
            mano_instance_meta = self.mano_manager.create_pishahang_instance()
            LOG.info(mano_instance_meta)
            if not mano_instance_meta:
                LOG.info("!!! MANO could not be instantiated...")
                self.instantiating_mano_instance = False
                return False
        elif mano_type == "osm":
            mano_instance_meta = self.mano_manager.create_osm_instance()
            if not mano_instance_meta:
                LOG.info("!!! MANO could not be instantiated...")
                self.instantiating_mano_instance = False
                return False
        else:
            LOG.info("!!! MANO type not supported...")
            self.instantiating_mano_instance = False
            return False

        # TODO: FIX ME! should be ip from the instantiation
        # self.mano_instances.append(
        #     {
        #         "host_ip":mano_instance_meta["ip"],
        #         "monitoring_port": NETDATA_PORT,
        #         "username":"",
        #         "password":"",
        #         "type":mano_type
        #     }
        # )

        LOG.info("\n MANO instantiated with IP... {0}".format(mano_instance_meta))

        self.mano_instances.append(
            {
                "host_ip":DUMMY_INSTANCE_IP,
                "monitoring_port": NETDATA_PORT,
                "username":"",
                "password":"",
                "type":mano_type
            }
        )

        # TODO: Add loop to get AUTH before going forward
        self.child_mano_added = True
        self.instantiating_mano_instance = False
        LOG.info("\nFinished creating MANO instance...")

    @run_async
    def terminate_mano_instance(self, host_ip):
        """
        Instantiate a new MANO instance
        """
        # TODO: 1) send termination request
        #       2) fetch the metadata generated by MANO (NSRs, VNFRs)
        LOG.info("\nTerminating MANO instance...")
        self.terminating_mano_instance = True
        time.sleep(5)

        for instance in self.mano_instances:
            if instance['host_ip'] == host_ip:
                del self.mano_instances[self.mano_instances.index(instance)]
    
        if len(self.mano_instances) == 0:
            self.child_mano_added = False

        self.terminating_mano_instance = False
        LOG.info("\nFinished Terminating MANO instance...")


    def _getCPUCoreCount(self, username=None, password=None, host=None, port=None, usehttps=False):
        """ netdata system Load API
        GET method which returns an CPU core Count 

        TODO: there has to be a better way to get this

        :param username: username for login
        :param password: password for login
        :param host: host url
        :param port: port where the netdata API can be accessed
        :usehttps: https or http

        Example:

        """
        if usehttps:
            base_path = 'https://{0}:{1}'.format(host, port)
        else:
            base_path = 'http://{0}:{1}'.format(host, port)

        _endpoint = '{0}/api/v1/chart?chart=users.cpu'.format(base_path)

        # headers = {"Content-Type": "application/yaml", "accept": "application/json"}
        # data = {"username": username, "password": password}

        try:
            r = requests.get(_endpoint)

            if r.status_code != requests.codes.ok:
                return False

            response = json.loads(r.text)
            cpu_core_count = response["title"]
            cpu_core_count = re.search('% = (.*) cores', cpu_core_count)
            cpu_core_count = int(cpu_core_count.group(1))

        except Exception as e:
            # result["data"] = str(e)
            LOG.info(str(e))
            return False

        return cpu_core_count


    def _getLoad(self, username=None, password=None, host=None, port=None, usehttps=False, num_points=5):
        """ netdata system Load API
        GET method which returns an an array of Load [1min, 5min, 15min]


        :param username: username for login
        :param password: password for login
        :param host: host url
        :param port: port where the netdata API can be accessed
        :usehttps: https or http
        :num_points: data points to fetch from netdata

        Example:

        """
        if usehttps:
            base_path = 'https://{0}:{1}'.format(host, port)
        else:
            base_path = 'http://{0}:{1}'.format(host, port)

        _endpoint = '{0}/api/v1/data?chart=system.load&format=json&points={1}&after=-60&options=jsonwrap'.format(base_path, num_points)

        try:
            r = requests.get(_endpoint)

            if r.status_code != requests.codes.ok:
                return False

            response = json.loads(r.text)
            cpu_load = response["latest_values"]

        except Exception as e:
            # result["data"] = str(e)
            LOG.info(str(e))
            return False

        return cpu_load


    def _getMem(self, username=None, password=None, host=None, port=None, usehttps=False, num_points=5):
        """ netdata system Memory API
        GET method which returns free memory percentage
        
        :param username: username for login
        :param password: password for login
        :param host: host url
        :param port: port where the netdata API can be accessed
        :usehttps: https or http
        :num_points: data points to fetch from netdata
        
        Example:

        """
        if usehttps:
            base_path = 'https://{0}:{1}'.format(host, port)
        else:
            base_path = 'http://{0}:{1}'.format(host, port)

        _endpoint = '{0}/api/v1/data?chart=system.ram&format=json&points=5&after=-60&options=jsonwrap|percentage'.format(base_path, num_points)

        # headers = {"Content-Type": "application/yaml", "accept": "application/json"}
        # data = {"username": username, "password": password}

        try:
            r = requests.get(_endpoint)

            if r.status_code != requests.codes.ok:
                return False

            response = json.loads(r.text)
            free_mem_percent = response["view_latest_values"][0]

        except Exception as e:
            # result["data"] = str(e)
            # LOG.info(str(e))
            return False

        return free_mem_percent


    def normalizeManoMetrics(self, manodata):

        if self.DEBUGMODE:
            with open("/plugins/son-mano-scaling/debugnorm", "r") as f:
                # print(list(map(lambda x: float(x), f.read().rstrip().split(","))))                
                
                return list(map(lambda x: float(x), f.read().rstrip().split(",")))

        _load = self._getLoad(host=manodata["host_ip"], port=manodata["monitoring_port"])
        _mem = self._getMem(host=manodata["host_ip"], port=manodata["monitoring_port"])
        _cores = self._getCPUCoreCount(host=manodata["host_ip"], port=manodata["monitoring_port"])
        LOG.info(_load)
        LOG.info(_mem)
        LOG.info(_cores)

        if _load:
            if _cores:
                # Equate load to the number of cores in MANO
                divide_cpu = lambda x: x/_cores
                _load = list(map(divide_cpu, _load)) 
                LOG.info(_load)
                LOG.info("\n\n")
            else:
                return False

            return _load
        else:
            return False

    def run(self):

        """
        To be overwritten by subclass
        """
        # TODO: fetch CPU information from all the instances
        # TODO: if 5min aveerage crosses threshold 0.7 then start creating an instances 
        #       and when 15min average crosses threshold 0.7 add it to the priority list
        # TODO: Termination of the instance when the laod on both the lower MANO and parent
        #       MANO are less than 0.7
        while True:
            LOG.info("\n\n ##################### \n\nScaling run loop..")
            LOG.info("Checking parent MANO")
            _parent_normal = self.normalizeManoMetrics(self.parent_mano)
            LOG.info(_parent_normal)
            if _parent_normal:
                self.parent_mano["priority"] = _parent_normal

            self.mano_priority = []

            # self.mano_priority.append(self.parent_mano)
            
            # TODO: Use warning and critical values here
            if (float(_parent_normal[1]) > 0.7):
                # TODO: Currently supports only one child mano. make this a numbered limit
                if not self.child_mano_added:
                    LOG.info("Parent MANO is getting loaded loaded")
                    if not self.instantiating_mano_instance:
                        self.create_mano_instance()

            if (float(_parent_normal[2]) > 0.7):
                self.parent_mano_loaded = True
                if self.child_mano_added:
                    LOG.info("Parent MANO is loaded, checking instances")
                    for _mano in self.mano_instances:
                        LOG.info(_mano["host_ip"])
                        _mano_normal = self.normalizeManoMetrics(_mano)
                        if _mano_normal:                            
                            LOG.info(_mano_normal)
                            _mano["priority"] = _mano_normal
                            self.mano_priority.append(_mano)
                        else:
                            LOG.info("Could'nt get MANO Metrics")
                else:
                    LOG.info("Child MANO not avalable!!")

            # TODO: Better termination sequence
            if (float(_parent_normal[2]) < 0.5):
                self.parent_mano_loaded = False
                if self.child_mano_added:
                    LOG.info("Parent MANO load is now decreasing...")
                    for _mano in self.mano_instances:
                        LOG.info(_mano["host_ip"])
                        _mano_normal = self.normalizeManoMetrics(_mano)
                        if float(_mano_normal[2] < 0.5):
                            LOG.info(_mano_normal)
                            self.terminate_mano_instance(_mano["host_ip"])
                        else:
                            LOG.info("Could'nt get MANO Metrics")

            LOG.info("\n \nChild Instance List")
            LOG.info(self.mano_instances)

            if self.mano_priority:
                LOG.info("\n \nPriority List")
                LOG.info(self.mano_priority)
            # _memory = dict(psutil.virtual_memory()._asdict())
            # LOG.info("CPU: {0}% | Memory: {0}%".format(psutil.cpu_percent(interval=1), _memory['percent']))
            time.sleep(3)

    def __del__(self):
        """
        Destroy Scaling plugin instance. De-register. Disconnect.
        :return:
        """
        super(self.__class__, self).__del__()

    def declare_subscriptions(self):
        """
        Declare topics that Scaling Plugin subscribes on.
        """
        # We have to call our super class here
        super(self.__class__, self).declare_subscriptions()

        # The topic on which deploy requests are posted.
        topic = 'mano.service.scaling'
        self.manoconn.subscribe(self.scaling_request, topic)

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
        LOG.info("Scaling plugin started and operational.")

    def deregister(self):
        """
        Send a deregister request to the plugin manager.
        """
        LOG.info('Deregistering Scaling plugin with uuid ' + str(self.uuid))
        message = {"uuid": self.uuid}
        self.manoconn.notify("platform.management.plugin.deregister",
                             json.dumps(message))
        os._exit(0)

    def on_registration_ok(self):
        """
        This method is called when the Scaling plugin
        is registered to the plugin mananger
        """
        super(self.__class__, self).on_registration_ok()
        LOG.debug("Received registration ok event.")

##########################
# Scaling
##########################

    def scaling_request(self, ch, method, prop, payload):
        """
        This method handles a Scaling request
        """

        if prop.app_id == self.name:
            return

        content = yaml.load(payload)
        LOG.info("Scaling request for service: " + content['serv_id'])
        # topology = content['topology']
        # descriptor = content['nsd'] if 'nsd' in content else content['cosd']
        # functions = content['functions'] if 'functions' in content else []
        # cloud_services = content['cloud_services'] if 'cloud_services' in content else []

        # TODO: Check if the current MANO instance is not overloaded by checking CPU and Memory usage
        
        if self.parent_mano_loaded:
            if self.child_mano_added:
                # TODO: wait for a few seconds mano_priority to be filled
                # TODO: Select the best mano from the list
                response = {'system_loaded': True, 'error': None, 'mano_instance': self.mano_priority[0]}
            else:
                response = {'system_loaded': False, 'error': None, 'mano_instance': None}
        else:
            response = {'system_loaded': False, 'error': None, 'mano_instance': None}

        topic = 'mano.service.scaling'
        self.manoconn.notify(topic,
                             yaml.dump(response),
                             correlation_id=prop.correlation_id)

        LOG.info("Scaling response sent for service: " + content['serv_id'])
        LOG.info(response)


def main():
    """
    Entry point to start plugin.
    :return:
    """
    # reduce messaging log level to have a nicer output for this plugin
    logging.getLogger("son-mano-base:messaging").setLevel(logging.INFO)
    logging.getLogger("son-mano-base:plugin").setLevel(logging.INFO)
#    logging.getLogger("amqp-storm").setLevel(logging.DEBUG)
    # create our function lifecycle manager
    placement = ScalingPlugin()

if __name__ == '__main__':
    main()
