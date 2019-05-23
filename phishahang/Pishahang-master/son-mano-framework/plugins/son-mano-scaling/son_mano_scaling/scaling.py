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

from sonmanobase.plugin import ManoBasePlugin

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
        # TODO: store a list of MANO instances
        self.mano_instances = [
            {
                "host_ip":"vm-hadik3r-05.cs.uni-paderborn.de",
                "monitoring_port": 19999,
                "username":"",
                "password":"",
                "type":"pishahang"
            },
            {
                "host_ip":"vm-hadik3r-06.cs.uni-paderborn.de",
                "monitoring_port": 19999,
                "username":"",
                "password":"",
                "type":"pishahang"
            },
            {
                "host_ip":"vm-hadik3r-07.cs.uni-paderborn.de",
                "monitoring_port": 19999,
                "username":"",
                "password":"",
                "type":"osm"
            }
        ]

        super(self.__class__, self).__init__(version=ver,
                                             description=des,
                                             auto_register=auto_register,
                                             wait_for_registration=wait_for_registration,
                                             start_running=start_running)

    def create_mano_instance(self):
        """
        Instantiate a new MANO instance
        """
        pass

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

        # headers = {"Content-Type": "application/yaml", "accept": "application/json"}
        # data = {"username": username, "password": password}

        try:
            r = requests.get(_endpoint)

            if r.status_code != requests.codes.ok:
                return False

            response = json.loads(r.text)
            cpu_load = response["latest_values"]

        except Exception as e:
            # result["data"] = str(e)
            # LOG.info(str(e))
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
        # TODO: For now take decision based on 15min load
        _load = self._getLoad(host=manodata["host_ip"], port=manodata["monitoring_port"])
        _mem = self._getMem(host=manodata["host_ip"], port=manodata["monitoring_port"])
        LOG.info(_load)
        LOG.info(_mem)
        if _load:
            return _load[2]
        else:
            return False

    def run(self):
        """
        To be overwritten by subclass
        """
        # TODO: fetch CPU information from all the instances
        # TODO: if going more than threshold (50%?) then create an instance and when it reaches
        #       second threshold (90%?) start delegating to new MANO
        while True:
            LOG.info("Scaling run loop..")
            self.mano_priority = []
            for _mano in self.mano_instances:
                _mano_normal = self.normalizeManoMetrics(_mano)
                LOG.info(_mano["host_ip"])
                if _mano_normal:
                    LOG.info(_mano_normal)
                    _mano["priority"] = _mano_normal
                    self.mano_priority.append(_mano)
                else:
                    LOG.info("Could'nt get MANO Metrics")

            LOG.info("Priority List")
            LOG.info(self.mano_priority)
            # _memory = dict(psutil.virtual_memory()._asdict())
            # LOG.info("CPU: {0}% | Memory: {0}%".format(psutil.cpu_percent(interval=1), _memory['percent']))
            time.sleep(5)

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
        self.manoconn.subscribe(self.scaling_engine, topic)

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

    def scaling_engine(self, ch, method, prop, payload):
        """
        This method handles a Scaling request
        """

        if prop.app_id == self.name:
            return

        content = yaml.load(payload)
        LOG.info("Scaling request for service: " + content['serv_id'])
        topology = content['topology']
        descriptor = content['nsd'] if 'nsd' in content else content['cosd']
        functions = content['functions'] if 'functions' in content else []
        cloud_services = content['cloud_services'] if 'cloud_services' in content else []

        # TODO: Check if the current MANO instance is not overloaded by checking CPU and Memory usage

        # placement = self.placement(descriptor, functions, cloud_services, topology)

        # response = {'mapping': placement}
        # topic = 'mano.service.place'

        # self.manoconn.notify(topic,
        #                      yaml.dump(response),
        #                      correlation_id=prop.correlation_id)

        # LOG.info("Placement response sent for service: " + content['serv_id'])
        # LOG.info(response)


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
