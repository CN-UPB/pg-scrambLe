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
# import psutil

from sonmanobase.plugin import ManoBasePlugin
import sonmanobase.messaging as messaging

try:
    from son_mano_slm import slm_helpers as tools
except:
    import slm_helpers as tools

try:
    from son_mano_slm import slm_helpers_old as oldtools
except:
    import slm_helpers_old as oldtools

try:
    from son_mano_slm import slm_topics as t
except:
    import slm_topics as t

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("plugin:slm")
LOG.setLevel(logging.DEBUG)


class ServiceLifecycleManager(ManoBasePlugin):
    """
    This class implements the service lifecycle manager.
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

        # Create the ledger that saves state
        self.services = {}

        # The frequency of state sharing events
        self.state_share_frequency = 1

        # Create a configuration dict that contains config info of SLM
        # Setting the number of SLMs and the rank of this SLM
        self.slm_config = {}
        self.slm_config['slm_rank'] = 0
        self.slm_config['slm_total'] = 1
        self.slm_config['old_slm_rank'] = 0
        self.slm_config['old_slm_total'] = 1
        self.slm_config['tasks_other_slm'] = {}

        self.publickey = None
        self.token = None
        self.password = '1234'
        self.clientId = 'son-slm'

        # Create the list of known other SLMs
        self.known_slms = []

        self.thrd_pool = pool.ThreadPoolExecutor(max_workers=10)

        # Create some flags that will be used for SLM management
        self.bufferAllRequests = False
        self.bufferOldRequests = False
        self.deltaTnew = 1
        self.deltaTold = 1

        self.old_reqs = {}
        self.new_reqs = {}

        self.flm_ledger = {}

        self.ssm_connections = {}
        self.ssm_user = 'specific-management'
        self.ssm_pass = 'sonata'
        base = 'amqp://' + self.ssm_user + ':' + self.ssm_pass
        self.ssm_url_base = base + '@son-broker:5672/'

        # The following can be removed once transition is done
        self.service_requests_being_handled = {}
        self.service_updates_being_handled = {}

        # call super class (will automatically connect to
        # broker and register the SLM to the plugin manger)
        ver = "0.1-dev"
        des = "This is the SLM plugin"

        wait_reg = wait_for_registration
        super(self.__class__, self).__init__(version=ver,
                                             description=des,
                                             auto_register=auto_register,
                                             wait_for_registration=wait_reg,
                                             start_running=start_running)

    def __del__(self):
        """
        Destroy SLM instance. De-register. Disconnect.
        :return:
        """
        super(self.__class__, self).__del__()

    def declare_subscriptions(self):
        """
        Declare topics that SLM subscribes on.
        """
        # We have to call our super class here
        super(self.__class__, self).declare_subscriptions()

        # The topic on which deploy requests are posted.
        self.manoconn.subscribe(self.service_instance_create, t.GK_CREATE)

        # The topic on which pause requests are posted.
        self.manoconn.subscribe(self.service_instance_pause, t.GK_PAUSE)

        # The topic on which resume requests are posted.
        self.manoconn.subscribe(self.service_instance_resume, t.GK_RESUME)

        # The topic on which termination requests are posted.
        self.manoconn.subscribe(self.service_instance_kill, t.GK_KILL)

        # The topic on which SLMs share state with eachother
        self.manoconn.subscribe(self.inter_slm, t.MANO_STATE)

        # The topic on which update requests are posted.
        self.manoconn.subscribe(self.service_update, t.GK_UPDATE)

        # The topic on which plugin status info is shared
        self.manoconn.subscribe(self.plugin_status, t.PL_STATUS)

#        # The topic on which the FLM receives deploy request from SLM
#        self.manoconn.subscribe(self.flm_deploy, t.MANO_DEPLOY)

        # The topic on which monitoring information is received
        self.manoconn.subscribe(self.monitoring_feedback, t.MON_RECEIVE)

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
        LOG.info("SLM started and operational. Registering with the GK...")

        self.register_slm_with_gk()

    def register_slm_with_gk(self):
        """
        This methods tries to register the SLM with the GK
        """
        counter = 0
        while counter < 3:
            try:
                user = self.clientId
                secr = self.password
                # Get Public key
                url = t.BASE_URL + t.API_VER + t.REG_PATH + t.PUPLIC_KEY_PATH
                self.publickey = tools.get_platform_public_key(url)
                LOG.info("Received key: " + str(self.publickey))

                # Register
                response = tools.client_register(t.GK_REGISTER, user, secr)
                LOG.info("Registration response: " + str(response))

                # Login
                self.token = tools.client_login(t.GK_LOGIN, user, secr)
                LOG.info("Login response: " + str(self.token))
            except:
                pass

            if self.token is None:
                LOG.info("Registration with GK failed, retrying...")
                counter = counter + 1
            else:
                break

        if self.token is None:
            LOG.info("Registration with GK failed, continuing without token.")
        else:
            LOG.info("Registration with GK succeeded, token obtained.")

    def deregister(self):
        """
        Send a deregister request to the plugin manager.
        """
        LOG.info('Deregistering SLM with uuid ' + str(self.uuid))
        message = {"uuid": self.uuid}
        self.manoconn.notify("platform.management.plugin.deregister",
                             json.dumps(message))
        os._exit(0)

    def on_registration_ok(self):
        """
        This method is called when the SLM is registered to the plugin mananger
        """
        super(self.__class__, self).on_registration_ok()
        LOG.debug("Received registration ok event.")

        # This SLM is currently the only known SLM
        self.known_slms.append(str(self.uuid))


##########################
# SLM Threading management
##########################

    def get_ledger(self, serv_id):

        return self.services[serv_id]

    def get_services(self):

        return self.services

    def set_services(self, service_dict):

        self.services = service_dict

        return

    def error_handling(self, serv_id, topic, message):

        LOG.info("Service " + serv_id + ": Error occured, killing workflow")
        LOG.info("Service " + serv_id + ": Error: " + str(message))
        self.services[serv_id]['kill_chain'] = True

        message = {'error': message,
                   'timestamp': time.time(),
                   'status': 'ERROR'}

        corr_id = self.services[serv_id]['original_corr_id']
        self.manoconn.notify(topic,
                             yaml.dump(message),
                             correlation_id=corr_id)

        return

    def start_next_task(self, serv_id):
        """
        This method makes sure that the next task in the schedule is started
        when a task is finished, or when the first task should begin.

        :param serv_id: the instance uuid of the service that is being handled.
        :param first: indicates whether this is the first task in a chain.
        """

        # If the kill field is active, the chain is killed
        if self.services[serv_id]['kill_chain']:
            LOG.info("Service " + serv_id + ": Killing running workflow")

            if (self.services[serv_id]["current_workflow"] == 'instantiation'):
                # If the current workflow is an instantiation workflow, we need
                # to delete the stack, the SSMs/FSMs and the generated records, if
                # they already exist
                self.roll_back_instantiation(serv_id)

            del self.services[serv_id]
            return

        # Select the next task, only if task list is not empty
        if len(self.services[serv_id]['schedule']) > 0:

            # share state with other SLMs
            next_task = getattr(self,
                                self.services[serv_id]['schedule'].pop(0))

            # Push the next task to the threadingpool
            task = self.thrd_pool.submit(next_task, serv_id)

            # Log the result of the task, for future reference
#            new_log = [next_task, task.result()]
#            self.services[serv_id]['task_log'].append(new_log)

            # Log if a task fails
            if task.exception() is not None:
                print(task.result())

#            if tasknumber % (1 / self.state_share_frequency) == 0:
#                self.slm_share('IN PROGRESS', self.services[serv_id])

            # When the task is done, the next task should be started if no flag
            # is set to pause the chain.
            if self.services[serv_id]['pause_chain']:
                self.services[serv_id]['pause_chain'] = False
            else:
                self.start_next_task(serv_id)

        else:
            # share state with other SLMs
            self.slm_share('DONE', self.services[serv_id])

            del self.services[serv_id]

####################
# SLM input - output
####################

    def plugin_status(self, ch, method, properties, payload):
        """
        This method is called when the plugin manager broadcasts new
        information on the plugins.
        """
        # TODO: needs unit testing

        message = yaml.load(payload)

        # If the plugin configuration has changed, it needs to be checked
        # whether the number of SLMs has changed.
        self.update_slm_configuration(message['plugin_dict'])

    def slm_down(self):
        """
        This method is called when this SLM notices that another SLM
        has gone missing. This SLM needs to determine whether it should
        take over unfinished tasks from this SLM.
        """
        # TODO: needs unit testing

        for serv_id in self.slm_config['tasks_other_slm'].keys():

            tasks_other_slm = self.slm_config['tasks_other_slm']
            # TODO: only take over when ID's match
            LOG.info('SLM down, taking over requests')
            self.services[serv_id] = tasks_other_slm[serv_id]

            if 'schedule' not in self.services[serv_id].keys():
                del self.services[serv_id]
                ch = self.tasks_other_slm[serv_id]['ch']
                method = tasks_other_slm[serv_id]['method']
                properties = tasks_other_slm[serv_id]['properties']
                payload = tasks_other_slm[serv_id]['payload']

                self.service_instance_create(ch, method, properties, payload)

            else:
                self.start_next_task(serv_id)

        self.slm_config['tasks_other_slm'] = {}

    def inter_slm(self, ch, method, properties, payload):
        """
        This method handles messages that are shared between different SLMs.
        """
        # TODO: needs unit testing

        msg = yaml.load(payload)

        if msg['slm_id'] != str(self.uuid):
            tasks_other_slm = self.slm_config['tasks_other_slm']

            if msg['status'] == 'DONE':
                if (str(msg['corr_id'])) in tasks_other_slm.keys():
                    del tasks_other_slm[str(msg['corr_id'])]

            if msg['status'] == 'IN PROGRESS':
                tasks_other_slm[str(msg['corr_id'])] = msg['state']

    def service_instance_create(self, ch, method, properties, payload):
        """
        This function handles a received message on the *.instance.create
        topic.
        """

        # Check if the messages comes from the GK or is forward by another SLM
        message_from_gk = True
        if properties.app_id == self.name:
            message_from_gk = False
            if properties.reply_to is None:
                return

        # Bypass for backwards compatibility, to be removed after
        # transition to new version of SLM is completed
        message = yaml.load(payload)

        # Extract the correlation id and generate a reduced id
        corr_id = properties.correlation_id
        reduced_id = tools.convert_corr_id(corr_id)

        # If the message comes from another SLM, check if the request has made
        # a round trip
        if not message_from_gk:
            calc_rank = reduced_id % self.slm_config['slm_total']
            roundtrip = (calc_rank == self.slm_config['slm_rank'])

            if roundtrip:
                # If the message made a round trip, a new SLM should be started
                # as this implies that the resources are exhausted
                deploy_new_slm()

            else:
                # TODO: check if this SLM has the resources for this request
                has_enough_resources = True
                if has_enough_resources:
                    pass
                else:
                    # TODO: forward to next SLM
                    return

        # Start handling the request
        message = yaml.load(payload)

        # Add the service to the ledger
        serv_id = self.add_service_to_ledger(message, corr_id)

        # Add workflow to ledger
        self.services[serv_id]['topic'] = t.GK_CREATE
        self.services[serv_id]['current_workflow'] = 'instantiation'

        # Schedule the tasks that the SLM should do for this request.
        add_schedule = []

        add_schedule.append('validate_deploy_request')
        add_schedule.append('contact_gk')

        # Onboard and instantiate the SSMs, if required.
        if self.services[serv_id]['service']['ssm']:
            add_schedule.append('onboard_ssms')
            add_schedule.append('instant_ssms')

        if 'task' in self.services[serv_id]['service']['ssm'].keys():
            add_schedule.append('trigger_task_ssm')

        add_schedule.append('request_topology')

        # Perform the placement
        if 'placement' in self.services[serv_id]['service']['ssm'].keys():
            add_schedule.append('req_placement_from_ssm')
        else:
            add_schedule.append('SLM_mapping')

        add_schedule.append('ia_prepare')
        add_schedule.append('vnf_deploy')
        add_schedule.append('vnfs_start')
        add_schedule.append('cs_deploy')
        add_schedule.append('vnf_chain')
        add_schedule.append('store_nsr')
        add_schedule.append('wan_configure')
        add_schedule.append('start_monitoring')
        add_schedule.append('inform_gk_instantiation')

        self.services[serv_id]['schedule'].extend(add_schedule)

        msg = ": New instantiation request received. Instantiation started."
        LOG.info("Service " + serv_id + msg)
        # Start the chain of tasks
        self.start_next_task(serv_id)

        return self.services[serv_id]['schedule']

    def service_instance_pause(self, ch, method, prop, payload):

        pass

    def service_instance_resume(self, ch, method, prop, payload):

        pass

    def service_instance_kill(self, ch, method, prop, payload):
        """
        This function handles a received message on the *.instance.kill
        topic.
        """

        # Check if the messages comes from the GK or is forward by another SLM
        if prop.app_id == self.name:
            return

        content = yaml.load(payload)
        serv_id = content['instance_id']
        LOG.info("Termination request received for service " + str(serv_id))

        self.terminate_workflow(serv_id,
                                prop.correlation_id,
                                t.GK_KILL,
                                orig='GK')

    def reconfigure_workflow(self, serv_id):
        """
        This method triggers a reconfiguration workflow.
        """

        LOG.info('Service ' + str(serv_id) + ': reconfigure workflow request')
        self.services[serv_id]['status'] = 'reconfigurating'
        self.services[serv_id]["current_workflow"] = 'reconfigure'

        add_schedule = []
        add_schedule.append("configure_ssm")
        add_schedule.append("vnfs_config")
        add_schedule.append("inform_config_ssm")

        self.services[serv_id]['schedule'].extend(add_schedule)

        LOG.info('Service ' + str(serv_id) + ': reconfigure workflow started')
        # Start the chain of tasks
        self.start_next_task(serv_id)

        return self.services[serv_id]['schedule']

    def terminate_workflow(self, serv_id, corr_id=None, topic=None, orig=None):
        """
        This function handles the actual termination
        """

        # Check if the ledger has an entry for this instance
        if serv_id not in self.services.keys():
            # Based on the received payload, the ledger entry is recreated.
            LOG.info("Recreating ledger.")
            self.recreate_ledger(corr_id, serv_id)

        # Add workflow to ledger
        self.services[serv_id]['topic'] = topic
        self.services[serv_id]['status'] = 'TERMINATING'
        self.services[serv_id]["current_workflow"] = 'termination'
        # Schedule the tasks that the SLM should do for this request.
        add_schedule = []

        if orig == 'GK':
            add_schedule.append('contact_gk')
        add_schedule.append("stop_monitoring")
        add_schedule.append("wan_deconfigure")
        add_schedule.append("vnf_unchain")
        add_schedule.append("vnfs_stop")
        add_schedule.append("terminate_service")

        if self.services[serv_id]['service']['ssm']:
            add_schedule.append("terminate_ssms")

        for vnf in self.services[serv_id]['function']:
            if vnf['fsm'] is not None:
                add_schedule.append("terminate_fsms")
                break

        add_schedule.append("update_records_to_terminated")
        if orig == 'GK':
            add_schedule.append("inform_gk")

        self.services[serv_id]['schedule'].extend(add_schedule)

        LOG.info("Termination workflow started for service " + str(serv_id))
        # Start the chain of tasks
        self.start_next_task(serv_id)

        return self.services[serv_id]['schedule']

    def service_instance_custom(self, serv_id, schedule):
        """
        This method creates a customized workflow. It is not called by
        the user through the GK, but from an SSM. The SSM has created
        the task schedule
        """

        # TODO: validate whether the proposed schedule by the SSM makes sense
        LOG.info("Custom workflow requested for service " + str(serv_id))

        if serv_id not in self.services.keys():
            # Based on the received payload, the ledger entry is recreated.
            LOG.info("Recreating ledger.")
            self.recreate_ledger(None, serv_id)

        self.services[serv_id]["current_workflow"] = 'custom'
        self.services[serv_id]['schedule'] = schedule

        LOG.info("Custom workflow started for service " + str(serv_id))
        # Start the chain of tasks
        self.start_next_task(serv_id)

        return self.services[serv_id]['schedule']

    def service_update(self, ch, method, prop, payload):

        pass

    def monitoring_feedback(self, ch, method, prop, payload):

        LOG.info("Monitoring message received")
        LOG.info(payload)

        try:
            content = json.loads(str(payload))

            content['ssm_type'] = 'monitor'
            uuid = content['serviceID']
            new_payload = yaml.dump(content)

            # Forward the received monitoring message to the SSM
            topic = 'generic.ssm.' + uuid

            ssm_conn = self.ssm_connections[uuid]

            ssm_conn.notify(topic, new_payload)
        except:
            pass

    def from_monitoring_ssm(self, ch, method, prop, payload):
        """
        This method is called every time the SLM receives a message from
        a monitoring SSM.
        """
        content = yaml.load(payload)
        LOG.info("monitoring SSM responded: " + str(content))

        serv_id = content['service_instance_id']
        self.recreate_ledger(None, serv_id)

        # Extract additional content provided by the SSM
        if 'vnf' in content.keys():
            vnfs = content['vnf']
            for vnf in vnfs:
                vnf_id = vnf['id']
                for vnf_slm in self.services[serv_id]['function']:
                    if vnf_id == vnf_slm['id']:
                        for key in vnf.keys():
                            vnf_slm[key] = vnf[key]

        if 'service' in content.keys():
            if 'configure' in content['service'].keys():
                data = content['service']['configure']
                self.services[serv_id]['service']['configure'] = data

        if 'workflow' in content.keys():
            if content['workflow'] == 'termination':
                self.terminate_workflow(serv_id)
            if content['workflow'] == 'pause':
                pass
            if content['workflow'] == 'reconfigure':
                self.reconfigure_workflow(serv_id)
            # TODO: add additional workflows
        if 'schedule' in content.keys():
            schedule = content['schedule']
            LOG.info("schedule found: " + str(schedule))
            self.service_instance_custom(serv_id, schedule)

        return

    def resp_topo(self, ch, method, prop, payload):
        """
        This function handles responses to topology requests made to the
        infrastructure adaptor.
        """
        message = yaml.load(payload)

        # Retrieve the service uuid
        serv_id = tools.servid_from_corrid(self.services, prop.correlation_id)

        LOG.info("Service " + serv_id + ": Topology received from IA.")
        LOG.debug("Requested info on topology: " + str(message))

        # Add topology to ledger
        self.services[serv_id]['infrastructure']['topology'] = message

        # Continue with the scheduled tasks
        self.start_next_task(serv_id)

    def resp_onboard(self, ch, method, prop, payload):
        """
        This function handles responses to a request to onboard the ssms
        of a new service.
        """
        # Retrieve the service uuid
        serv_id = tools.servid_from_corrid(self.services, prop.correlation_id)
        LOG.info("Service " + serv_id + ": Onboarding resp received from SMR.")

        message = yaml.load(payload)

        for key in message.keys():
            if message[key]['error'] == 'None':
                LOG.info("Service " + serv_id + ": SSMs onboarded succesfully")
            else:
                msg = ": SSM onboarding failed: " + message[key]['error']
                LOG.info("Service " + serv_id + msg)
                self.error_handling(serv_id,
                                    t.GK_CREATE,
                                    message[key]['error'])

        # Continue with the scheduled tasks
        self.start_next_task(serv_id)

    def resp_instant(self, ch, method, prop, payload):
        """
        This function handles responses to a request to onboard the ssms
        of a new service.
        """

        # Retrieve the service uuid
        serv_id = tools.servid_from_corrid(self.services, prop.correlation_id)
        msg = ": Instantiating response received from SMR."
        LOG.info("Service " + serv_id + msg)
        LOG.debug(payload)

        message = yaml.load(payload)
        for ssm_type in self.services[serv_id]['service']['ssm'].keys():
            ssm = self.services[serv_id]['service']['ssm'][ssm_type]
            response = message[ssm['id']]
            ssm['instantiated'] = False
            if response['error'] == 'None':
                LOG.info("Service " + serv_id + ": SSM instantiated correct.")
                ssm['instantiated'] = True
            else:
                msg = ": SSM instantiation failed: " + response['error']
                LOG.info("Service " + serv_id + msg)
                self.error_handling(serv_id, t.GK_CREATE, response['error'])

            ssm['uuid'] = response['uuid']

        # Setup broker connection with the SSMs of this service.
        url = self.ssm_url_base + 'ssm-' + serv_id
        ssm_conn = messaging.ManoBrokerRequestResponseConnection(self.name,
                                                                 url=url)

        self.ssm_connections[serv_id] = ssm_conn

        # Continue with the scheduled tasks
        self.start_next_task(serv_id)

    def resp_task(self, ch, method, prop, payload):
        """
        This method handles updates of the task schedule by the an SSM.
        """
        # TODO: Test this method

        # Retrieve the service uuid
        serv_id = tools.servid_from_corrid(self.services, prop.correlation_id)

        LOG.info("Service " + serv_id + ": Response from task ssm: " + payload)

        message = yaml.load(payload)

        if message['status'] == 'COMPLETED':
            self.services[serv_id]['schedule'] = message['schedule']
            msg = ": New schedule: " + str(self.services[serv_id]['schedule'])
            LOG.info("Service " + serv_id + msg)

            # Continue with the scheduled tasks
            self.start_next_task(serv_id)
        else:
            LOG.info("Service " + serv_id + ": Schedule update failed")

    def resp_place(self, ch, method, prop, payload):
        """
        This method handles a placement performed by an SSM.
        """
        # TODO: Test this method

        message = yaml.load(payload)

        is_dict = isinstance(message, dict)
        LOG.debug("Type Dict: " + str(is_dict))

        # Retrieve the service uuid
        serv_id = tools.servid_from_corrid(self.services, prop.correlation_id)

        mapping = message['mapping']
        error = message['error']

        if error is not None:
            LOG.info("Service " + serv_id + ": Error from place: " + error)
            self.error_handling(serv_id, t.GK_CREATE, error)

        else:
            # Add mapping to ledger
            msg = ": Calculated SSM mapping: " + str(mapping)
            LOG.info("Service " + serv_id + msg)
            self.services[serv_id]['service']['mapping'] = mapping
            for function in self.services[serv_id]['function']:
                vnf_id = function['id']
                function['vim_uuid'] = mapping[vnf_id]['vim']

        # Check if the placement does not contain any loops
        vim_list = tools.get_ordered_vim_list(self.services[serv_id])

        if vim_list is None:
            # the placement contains loops
            msg = 'Placement contains loop, improve Placement SSM.'
            self.error_handling(serv_id,
                                t.GK_CREATE,
                                msg)

            return
        else:
            LOG.info("Service " + serv_id + ": VIM list ordered")
            self.services[serv_id]['service']['ordered_vim_list'] = vim_list

        self.start_next_task(serv_id)

    def resp_ssm_configure(self, ch, method, prop, payload):
        """
        This method handles an ssm configuration response
        """

        # Retrieve the service uuid
        serv_id = tools.servid_from_corrid(self.services, prop.correlation_id)

        msg = ": Response received from configuration SSM."
        LOG.info("Service " + serv_id + msg)

        content = yaml.load(payload)

        # TODO: check if content is correctly formatted

        if 'vnf' in content.keys():
            vnfs = content['vnf']
            for vnf in vnfs:
                vnf_id = vnf['id']
                for vnf_slm in self.services[serv_id]['function']:
                    if vnf_id == vnf_slm['id']:
                        for key in vnf.keys():
                            vnf_slm[key] = vnf[key]

        self.start_next_task(serv_id)

    def resp_vnf_depl(self, ch, method, prop, payload):
        """
        This method handles a response from the FLM to a vnf deploy request.
        """
        message = yaml.load(payload)

        # Retrieve the service uuid
        serv_id = tools.servid_from_corrid(self.services, prop.correlation_id)
        msg = ": Message received from FLM on VNF deploy call."
        LOG.info("Service " + serv_id + msg)

        # Inform GK if VNF deployment failed
        if message['error'] is not None:

            LOG.info("Service " + serv_id + ": Deployment of VNF failed")
            LOG.debug("Message: " + str(message))
            self.error_handling(serv_id, t.GK_CREATE, message['error'])

        else:
            LOG.info("Service " + serv_id + ": VNF correctly Deployed.")
            for function in self.services[serv_id]['function']:
                if function['id'] == message['vnfr']['id']:
                    function['vnfr'] = message['vnfr']
                    LOG.info("Added vnfr for inst: " + message['vnfr']['id'])

        vnfs_to_depl = self.services[serv_id]['vnfs_to_resp'] - 1
        self.services[serv_id]['vnfs_to_resp'] = vnfs_to_depl

        # Only continue if all vnfs are deployed
        if vnfs_to_depl == 0:
            self.services[serv_id]['act_corr_id'] = None
            self.start_next_task(serv_id)

    def resp_vnfs_csss(self, ch, method, prop, payload):
        """
        This method handles a response from the FLM to a vnf csss request.
        """
        message = yaml.load(payload)

        # Retrieve the service uuid
        serv_id = tools.servid_from_corrid(self.services, prop.correlation_id)
        msg = ": Response received from FLM on VNF csss call."
        LOG.info("Service " + serv_id + msg)

        # Inform GK if VNF deployment failed
        if message['error'] is not None:

            LOG.info("Service " + serv_id + ": VNF csss event failed")
            LOG.debug("Message: " + str(message))
            topic = self.services[serv_id]['topic']
            self.services[serv_id]['config_status'] = 'failed'
            self.error_handling(serv_id, topic, message['error'])

        else:
            vnf_id = str(message["vnf_id"])
            self.services[serv_id]['config_status'] = 'ready'
            message = ": VNF " + vnf_id + " correctly handled."
            LOG.info("Service " + serv_id + message)

        vnfs_to_resp = self.services[serv_id]['vnfs_to_resp'] - 1
        self.services[serv_id]['vnfs_to_resp'] = vnfs_to_resp

        # Only continue if all vnfs are done
        if vnfs_to_resp == 0:
            self.services[serv_id]['act_corr_id'] = None
            self.start_next_task(serv_id)

    def resp_prepare(self, ch, method, prop, payload):
        """
        This method handles a response to a prepare request.
        """
        # Retrieve the service uuid
        serv_id = tools.servid_from_corrid(self.services, prop.correlation_id)

        response = yaml.load(payload)
        LOG.debug("Response from IA on .prepare call: " + str(response))

        if response['request_status'] == "COMPLETED":
            LOG.info("Service " + serv_id + ": Msg from IA: Infra prepared")
        else:
            msg = ": Error occured while preparing vims, aborting workflow"
            LOG.info("Service " + serv_id + msg)
            self.error_handling(serv_id, t.GK_CREATE, response['message'])

        self.start_next_task(serv_id)

    def contact_gk(self, serv_id):
        """
        This method handles communication towards the gatekeeper.`

        :param serv_id: the instance uuid of the service
        """

        # Get the correlation_id for the message
        corr_id = self.services[serv_id]['original_corr_id']

        # Build the message for the GK
        message = {}
        message['status'] = self.services[serv_id]['status']
        message['error'] = self.services[serv_id]['error']
        message['timestamp'] = time.time()

        if 'add_content' in self.services[serv_id].keys():
            message.update(self.services[serv_id]['add_content'])

        payload = yaml.dump(message)
        self.manoconn.notify(self.services[serv_id]['topic'],
                             payload,
                             correlation_id=corr_id)

    def request_topology(self, serv_id):
        """
        This method is used to request the topology of the available
        infrastructure from the Infrastructure Adaptor.

        :param serv_id: The instance uuid of the service
        """

        # Generate correlation_id for the call, for future reference
        corr_id = str(uuid.uuid4())
        self.services[serv_id]['act_corr_id'] = corr_id

        self.manoconn.call_async(self.resp_topo,
                                 t.IA_TOPO,
                                 None,
                                 correlation_id=corr_id)

        # Pause the chain of tasks to wait for response
        self.services[serv_id]['pause_chain'] = True

        LOG.info("Service " + serv_id + ": Topology requested from IA.")

    def ia_prepare(self, serv_id):
        """
        This method informs the IA which PoPs will be used and which
        type the image will be (by linking the image)

        :param serv_id: The instance uuid of the service
        """

        msg = ": Requesting IA to prepare the infrastructure."
        LOG.info("Service " + serv_id + msg)
        # Build mapping message for IA
        IA_mapping = {}

        # Add the service instance uuid
        IA_mapping['instance_id'] = serv_id

        # Create the VIM list
        IA_mapping['vim_list'] = []

        # Add the vnfs
        for function in self.services[serv_id]['function']:
            vim_uuid = function['vim_uuid']

            # Add VIM uuid if new
            new_vim = True
            for vim in IA_mapping['vim_list']:
                if vim['uuid'] == vim_uuid:
                    new_vim = False
                    index = IA_mapping['vim_list'].index(vim)

            if new_vim:
                IA_mapping['vim_list'].append({'uuid': vim_uuid,
                                               'vm_images': []})
                index = len(IA_mapping['vim_list']) - 1

            for vdu in function['vnfd']['virtual_deployment_units']:
                url = vdu['vm_image']
                vm_uuid = tools.generate_image_uuid(vdu, function['vnfd'])

                content = {'image_uuid': vm_uuid, 'image_url': url}

                if 'vm_image_md5' in vdu.keys():
                    content['image_md5'] = vdu['vm_image_md5']

                IA_mapping['vim_list'][index]['vm_images'].append(content)

        for cloud_service in self.services[serv_id]['cloud_service']:
            vim_uuid = cloud_service['vim_uuid']

            # Add VIM uuid if new
            new_vim = True
            for vim in IA_mapping['vim_list']:
                if vim['uuid'] == vim_uuid:
                    new_vim = False

            if new_vim:
                IA_mapping['vim_list'].append({'uuid': vim_uuid,
                                               'vm_images': []})

        # Add correlation id to the ledger for future reference
        corr_id = str(uuid.uuid4())
        self.services[serv_id]['act_corr_id'] = corr_id

        # Send this mapping to the IA
        self.manoconn.call_async(self.resp_prepare,
                                 t.IA_PREPARE,
                                 yaml.dump(IA_mapping),
                                 correlation_id=corr_id)

        # Pause the chain of tasks to wait for response
        self.services[serv_id]['pause_chain'] = True

    def vnf_deploy(self, serv_id):
        """
        This method triggeres the deployment of all the vnfs.
        """

        if len(self.services[serv_id]['function']) == 0:
            msg = ": Service doesn't contain any functions. Skipping VNF deploy."
            LOG.info("Service " + serv_id + msg)
            return

        functions = self.services[serv_id]['function']
        self.services[serv_id]['vnfs_to_resp'] = len(functions)

        self.services[serv_id]['act_corr_id'] = []

        for function in functions:

            corr_id = str(uuid.uuid4())
            self.services[serv_id]['act_corr_id'].append(corr_id)

            message = {}
            message['vnfd'] = function['vnfd']
            message['id'] = function['id']
            message['vim_uuid'] = function['vim_uuid']
            message['serv_id'] = serv_id
            message['public_key'] = self.services[serv_id]['public_key']
            message['private_key'] = self.services[serv_id]['private_key']

            msg = ": Requesting the deployment of vnf " + function['id']
            LOG.info("Service " + serv_id + msg)
            LOG.debug("Payload of request: " + str(message))
            self.manoconn.call_async(self.resp_vnf_depl,
                                     t.MANO_DEPLOY,
                                     yaml.dump(message),
                                     correlation_id=corr_id)

        self.services[serv_id]['pause_chain'] = True

    def cs_deploy(self, serv_id):
        """
        Deploy the cloud services of the complex service.
        """
        if len(self.services[serv_id]['cloud_service']) == 0:
            msg = ": Service doesn't contain any cloud services. Skipping CS deploy."
            LOG.info("Service " + serv_id + msg)
            return

        msg = ": Deploying cloud services."
        LOG.info("Service " + serv_id + msg)

        cloud_services = self.services[serv_id]['cloud_service']
        self.services[serv_id]['css_to_resp'] = len(cloud_services)

        self.services[serv_id]['act_corr_id'] = []

        for cloud_service in cloud_services:
            corr_id = str(uuid.uuid4())
            self.services[serv_id]['act_corr_id'].append(corr_id)

            message = {}
            message['csd'] = cloud_service['csd']
            message['id'] = cloud_service['id']
            message['vim_uuid'] = cloud_service['vim_uuid']
            message['serv_id'] = serv_id

            msg = ": Requesting the deployment of cs " + cloud_service['id']
            LOG.info("Service " + serv_id + msg)
            LOG.debug("Payload of request: " + str(message))
            self.manoconn.call_async(self.resp_cs_depl,
                                     t.MANO_CS_DEPLOY,
                                     yaml.dump(message),
                                     correlation_id=corr_id)

        self.services[serv_id]['pause_chain'] = True

    def resp_cs_depl(self, ch, method, prop, payload):
        """
        This method handles a response from the FLM to a cs deploy request.
        """
        message = yaml.load(payload)

        # Retrieve the service uuid
        serv_id = tools.servid_from_corrid(self.services, prop.correlation_id)
        msg = ": Message received from CLM on CS deploy call."
        LOG.info("Service " + serv_id + msg)

        # Inform GK if CS deployment failed
        if message['error'] is not None:

            LOG.info("Service " + serv_id + ": Deployment of CS failed")
            LOG.debug("Message: " + str(message))
            self.error_handling(serv_id, t.GK_CREATE, message['error'])

        else:
            LOG.info("Service " + serv_id + ": CS correctly Deployed.")
            for cloud_service in self.services[serv_id]['cloud_service']:
                if cloud_service['id'] == message['csr']['id']:
                    cloud_service['csr'] = message['csr']
                    LOG.info("Added csr for inst: " + message['csr']['id'])

        css_to_depl = self.services[serv_id]['css_to_resp'] - 1
        self.services[serv_id]['css_to_resp'] = css_to_depl

        # Only continue if all css are deployed
        if css_to_depl == 0:
            LOG.info("Deployment of CSs completed.")
            self.services[serv_id]['act_corr_id'] = None
            self.start_next_task(serv_id)


    def vnfs_start(self, serv_id):
        """
        This method gives a trigger to the FLM for each VNF that needs
        a FSM start life cycle event.
        """
        if len(self.services[serv_id]['function']) == 0:
            msg = ": Service doesn't contain any functions. Skipping VNFs start."
            LOG.info("Service " + serv_id + msg)
            return

        msg = ": Triggering VNF start events"
        LOG.info("Service " + serv_id + msg)
        self.vnfs_csss(serv_id, 'start', t.MANO_START)

    def vnfs_stop(self, serv_id):
        """
        This method gives a trigger to the FLM for each VNF that needs
        a FSM stop life cycle event.
        """

        if len(self.services[serv_id]['function']) == 0:
            msg = ": Service doesn't contain any functions. Skipping VNFs stop."
            LOG.info("Service " + serv_id + msg)
            return

        msg = ": Triggering VNF stop events"
        LOG.info("Service " + serv_id + msg)
        self.vnfs_csss(serv_id, 'stop', t.MANO_STOP)

    def vnfs_config(self, serv_id):
        """
        This method gives a trigger to the FLM for each VNF that needs
        a FSM config life cycle event.
        """
        msg = ": Triggering VNF config events"
        LOG.info("Service " + serv_id + msg)
        self.vnfs_csss(serv_id, 'configure', t.MANO_CONFIG)

    def vnfs_scale(self, serv_id):
        """
        This method gives a trigger to the FLM for each VNF that needs
        a FSM scale life cycle event.
        """
        msg = ": Triggering VNF scale events"
        LOG.info("Service " + serv_id + msg)
        self.vnfs_csss(serv_id, 'scale', t.MANO_SCALE)

    def vnfs_csss(self, serv_id, csss_type, topic):
        """
        This generic method gives a trigger to the FLM for each VNF that needs
        a FSM csss life cycle event. Can be used for start, stop and config
        triggers.
        """
        functions = self.services[serv_id]['function']
        self.services[serv_id]['act_corr_id'] = []

        # Counting the number of vnfs that you need a response from
        vnfs_to_resp = 0
        for vnf in functions:
            if vnf[csss_type]['trigger']:
                vnfs_to_resp = vnfs_to_resp + 1
        self.services[serv_id]['vnfs_to_resp'] = vnfs_to_resp

        # Actually triggering the FLM
        for vnf in functions:
            if vnf[csss_type]['trigger']:
                # Check if payload was provided
                payload = {}
                payload['vnf_id'] = vnf['id']
                payload['vnfd'] = vnf['vnfd']
                payload['serv_id'] = serv_id
                if bool(vnf[csss_type]['payload']):
                    payload['data'] = vnf[csss_type]['payload']
                # if not, create it
                else:
                    if csss_type == "configure":
                        nsr = self.services[serv_id]['service']['nsr']
                        vnfrs = []
                        for vnf_new in functions:
                            vnfrs.append(vnf_new['vnfr'])
                        data = {'nsr': nsr, 'vnfrs': vnfrs}
                    else:
                        data = {'vnfr': vnf['vnfr'], 'vnfd': vnf['vnfd']}

                    payload['data'] = data

                corr_id = str(uuid.uuid4())
                self.services[serv_id]['act_corr_id'].append(corr_id)

                msg = " " + csss_type + " event requested for vnf " + vnf['id']
                LOG.info("Service " + serv_id + msg)

                self.manoconn.call_async(self.resp_vnfs_csss,
                                         topic,
                                         yaml.dump(payload),
                                         correlation_id=corr_id)

                self.services[serv_id]['pause_chain'] = True

    def onboard_ssms(self, serv_id):
        """
        This method instructs the ssm registry manager to onboard the
        required SSMs.

        :param serv_id: The instance uuid of the service
        """

        corr_id = str(uuid.uuid4())
        # Sending the NSD to the SRM triggers it to onboard the ssms
        msg = {}
        if 'nsd' in self.services[serv_id]['service']:
            msg['NSD'] = self.services[serv_id]['service']['nsd']
        else:
            msg['NSD'] = self.services[serv_id]['service']['cosd']
        msg['VNFD'] = []
        for function in self.services[serv_id]['function']:
            msg['VNFD'].append(function['vnfd'])

        pyld = yaml.dump(msg)
        self.manoconn.call_async(self.resp_onboard,
                                 t.SRM_ONBOARD,
                                 pyld,
                                 correlation_id=corr_id)

        # Add correlation id to the ledger for future reference
        self.services[serv_id]['act_corr_id'] = corr_id

        # Pause the chain of tasks to wait for response
        self.services[serv_id]['pause_chain'] = True

        LOG.info("Service " + serv_id + ": SSM on-board trigger sent to SMR.")

    def instant_ssms(self, serv_id):
        """
        This method instructs the ssm registry manager to instantiate the
        required SSMs.

        :param serv_id: The instance uuid of the service
        :param ssm_id: which ssm you want to deploy
        """

        corr_id = str(uuid.uuid4())
        # Sending the NSD to the SRM triggers it to instantiate the ssms

        msg_for_smr = {}
        if 'nsd' in self.services[serv_id]['service']:
            msg_for_smr['NSD'] = self.services[serv_id]['service']['nsd']
        else:
            msg_for_smr['NSD'] = self.services[serv_id]['service']['cosd']
        msg_for_smr['UUID'] = serv_id

        msg = ": Keys in message for SSM instant: " + str(msg_for_smr.keys())
        LOG.info("Service " + serv_id + msg)
        pyld = yaml.dump(msg_for_smr)

        self.manoconn.call_async(self.resp_instant,
                                 t.SRM_INSTANT,
                                 pyld,
                                 correlation_id=corr_id)

        # Add correlation id to the ledger for future reference
        self.services[serv_id]['act_corr_id'] = corr_id

        # Pause the chain of tasks to wait for response
        self.services[serv_id]['pause_chain'] = True

        LOG.info("SSM instantiation trigger sent to SMR")

    def trigger_task_ssm(self, serv_id):
        """
        This method contacts the master SSM and allows it to update
        the task schedule.

        :param serv_id: the instance uuid of the service
        """

        corr_id = str(uuid.uuid4())
        self.services[serv_id]['act_corr_id'] = corr_id

        # Select the master SSM and create topic to reach it on
        ssm_id = self.services[serv_id]['service']['ssm']['task']['uuid']
        topic = "generic.ssm." + str(serv_id)

        # Adding the schedule to the message
        message = {'schedule': self.services[serv_id]['schedule'],
                   'ssm_type': 'task'}

        # Contact SSM
        payload = yaml.dump(message)

        ssm_conn = self.ssm_connections[serv_id]

        ssm_conn.call_async(self.resp_task,
                            topic,
                            payload,
                            correlation_id=corr_id)

        LOG.info("Service " + serv_id + ": task registered on " + str(topic))

        # Pause the chain of tasks to wait for response
        self.services[serv_id]['pause_chain'] = True

    def req_placement_from_ssm(self, serv_id):
        """
        This method requests the placement by an ssm.

        :param serv_id: The instance uuid of the service.
        """

        corr_id = str(uuid.uuid4())
        self.services[serv_id]['act_corr_id'] = corr_id

        # Check if placement SSM is available
        ssm_place = self.services[serv_id]['service']['ssm']['placement']
        # If not available, fall back on SLM placement
        if ssm_place['instantiated'] is False:
            return self.SLM_mapping(serv_id)
        # build message for placement SSM
        if 'nsd' in self.services[serv_id]['service']:
            nsd = self.services[serv_id]['service']['nsd']
        else:
            nsd = self.services[serv_id]['service']['cosd']
        top = self.services[serv_id]['infrastructure']['topology']

        vnfds = []
        for function in self.services[serv_id]['function']:
            vnfd_to_add = function['vnfd']
            vnfd_to_add['instance_uuid'] = function['id']
            vnfds.append(function['vnfd'])

        message = {'nsd': nsd,
                   'topology': top,
                   'uuid': serv_id,
                   'vnfds': vnfds}

        message['nap'] = {}

        if self.services[serv_id]['ingress'] is not None:
            message['nap']['ingresses'] = self.services[serv_id]['ingress']
        if self.services[serv_id]['egress'] is not None:
            message['nap']['egresses'] = self.services[serv_id]['egress']

        # Contact SSM
        payload = yaml.dump(message)

        msg = ": Placement requested from SSM: " + str(message.keys())
        LOG.info("Service " + serv_id + msg)

        self.manoconn.call_async(self.resp_place,
                                 t.EXEC_PLACE,
                                 payload,
                                 correlation_id=corr_id)

        # Pause the chain of tasks to wait for response
        self.services[serv_id]['pause_chain'] = True

    def configure_ssm(self, serv_id):
        """
        This method contacts a configuration ssm with the descriptors
        and the records if they are available.

        :param serv_id: The instance uuid of the service.
        """

        corr_id = str(uuid.uuid4())
        self.services[serv_id]['act_corr_id'] = corr_id

        if 'configure' not in self.services[serv_id]['service']['ssm'].keys():
            LOG.info("Configuration SSM requested but not available")
            return

        # ssm = self.services[serv_id]['service']['ssm']
        # if not ssm['configure']['instantiated']:
        #     LOG.info("Configuration SSM not instantiated")
        #     return

        # Building the content message for the configuration ssm
        content = {'service': self.services[serv_id]['service'],
                   'functions': self.services[serv_id]['function']}
        
        if self.services[serv_id]["current_workflow"] == 'instantiation':
            content['ingress'] = self.services[serv_id]['ingress']
            content['egress'] = self.services[serv_id]['egress']
                    
        content['ssm_type'] = 'configure'
        content['workflow'] = self.services[serv_id]["current_workflow"]

        topic = "generic.ssm." + str(serv_id)

        ssm_conn = self.ssm_connections[serv_id]

        ssm_conn.call_async(self.resp_ssm_configure,
                            topic,
                            yaml.dump(content),
                            correlation_id=corr_id)

        # Pause the chain of tasks to wait for response
        self.services[serv_id]['pause_chain'] = True

    def inform_config_ssm(self, serv_id):
        """
        Sent the status to the configuration SSM.
        """

        corr_id = str(uuid.uuid4())

        msg = ": Sending status to config SSM"
        LOG.info("Service " + serv_id + msg)

        content = {}
        content['ssm_type'] = 'configure'
        content['workflow'] = 'status'
        content['status'] = self.services[serv_id]['config_status']

        topic = "generic.ssm." + str(serv_id)

        ssm_conn = self.ssm_connections[serv_id]

        ssm_conn.notify(topic,
                        yaml.dump(content),
                        correlation_id=corr_id)

    def slm_share(self, status, content):

        message = {'status': status,
                   'state': content,
                   'corr_id': content['original_corr_id'],
                   'slm_id': self.uuid}

        payload = yaml.dump(message)
        self.manoconn.notify('mano.inter.slm', payload)

    def flm_deploy(self, ch, method, prop, payload):
        """
        This methods fakes the FLM by handling requests from the SLM to dpeloy
        a specific function
        """

        message = yaml.load(payload)

        if 'vnfd' in message.keys():

            outg_message = {}
            outg_message['vnfd'] = message['vnfd']
            outg_message['vnfd']['instance_uuid'] = message['id']
            outg_message['vim_uuid'] = message['vim_uuid']
            outg_message['service_instance_id'] = message['serv_id']

            payload = yaml.dump(outg_message)

            corr_id = str(uuid.uuid4())
            # adding the vnfd to the flm ledger
            self.flm_ledger[corr_id] = {}
            self.flm_ledger[corr_id]['vnfd'] = message['vnfd']
            self.flm_ledger[corr_id]['orig_corr_id'] = prop.correlation_id

            LOG.info("VNF deployment request from fake FLM to IA.")
            LOG.debug("Payload of request: " + payload)
            # Contact the IA
            self.manoconn.call_async(self.IA_deploy_response,
                                     t.IA_DEPLOY,
                                     payload,
                                     correlation_id=corr_id)

    def IA_deploy_response(self, ch, method, prop, payload):
        """
        This method fakes the FLMs reaction to a IA response.
        """

        # When the IA responses, the FLM builds the record and then
        # forwards this to the SLM.
        LOG.info("IA reply to fake FLM on VNF deploy call")
        LOG.debug("Payload of request: " + str(payload))

        inc_message = yaml.load(payload)

        # Build the message for the SLM
        outg_message = {}
        outg_message['status'] = inc_message['request_status']

        # Getting vnfd from the FLM ledger
        vnfd = self.flm_ledger[prop.correlation_id]['vnfd']

        error = None
        if inc_message['message'] != '':
            error = inc_message['message']

        if inc_message['request_status'] == "COMPLETED":

            # Build the record
            vnfr = tools.build_vnfr(inc_message['vnfr'], vnfd)
            outg_message['vnfr'] = vnfr

            # Store the record
#            try:
            url = t.VNFR_REPOSITORY_URL + 'vnf-instances'
            header = {'Content-Type': 'application/json'}
            vnfr_response = requests.post(url,
                                          data=json.dumps(vnfr),
                                          headers=header,
                                          timeout=1.0)
            LOG.info("Storing VNFR on " + url)
            LOG.debug("VNFR: " + str(vnfr))

            if (vnfr_response.status_code == 200):
                LOG.info("VNFR storage accepted.")
                outg_message['vnfr'] = vnfr
            # If storage fails, add error code and message to rply to gk
            else:
                error = {'http_code': vnfr_response.status_code,
                         'message': vnfr_response.json()}
                LOG.info('vnfr to repo failed: ' + str(error))
            # except:
            #     error = {'http_code': '0',
            #              'message': 'Timeout contacting VNFR server'}
            #     LOG.info('time-out on vnfr to repo')

        outg_message['error'] = error
        outg_message['inst_id'] = vnfd['instance_uuid']

        corr_id = self.flm_ledger[prop.correlation_id]['orig_corr_id']
        self.manoconn.notify(t.MANO_DEPLOY,
                             yaml.dump(outg_message),
                             correlation_id=corr_id)

    def store_nsr(self, serv_id):

        # TODO: get request_status from response from IA on chain
        is_nsd = 'nsd' in self.services[serv_id]['service']
        request_status = 'normal operation'

        if request_status == 'normal operation':
            LOG.info("Service " + serv_id + ": Update status of the VNFR")
            for function in self.services[serv_id]['function']:
                function['vnfr']['status'] = "normal operation"
                function['vnfr']['version'] = '2'

                url = t.VNFR_REPOSITORY_URL + 'vnf-instances/' + function['id']
                LOG.info("Service " + serv_id + ": URL VNFR update: " + url)

                error = None
                try:
                    header = {'Content-Type': 'application/json'}
                    vnfr_resp = requests.put(url,
                                             data=json.dumps(function['vnfr']),
                                             headers=header,
                                             timeout=1.0)
                    vnfr_resp_json = str(vnfr_resp.json())
                    if (vnfr_resp.status_code == 200):
                        msg = ": VNFR update accepted for " + function['id']
                        LOG.info("Service " + serv_id + msg)
                    else:
                        msg = ": VNFR update not accepted: " + vnfr_resp_json
                        LOG.info("Service " + serv_id + msg)
                        error = {'http_code': vnfr_resp.status_code,
                                 'message': vnfr_resp_json}
                except:
                    error = {'http_code': '0',
                             'message': 'Timeout when contacting VNFR repo'}

                if error is not None:
                    self.error_handling(serv_id, t.GK_CREATE, error)
                    return

            LOG.info("Service " + serv_id + ": Update status of the CSR")
            for cloud_service in self.services[serv_id]['cloud_service']:
                cloud_service['csr']['status'] = "normal operation"
                cloud_service['csr']['version'] = '1'

                url = t.CSR_REPOSITORY_URL + 'cs-instances/' + cloud_service['id']
                LOG.info("Service " + serv_id + ": URL CSR update: " + url)

                error = None
                try:
                    header = {'Content-Type': 'application/json'}
                    csr_resp = requests.put(url,
                                             data=json.dumps(cloud_service['csr']),
                                             headers=header,
                                             timeout=1.0)
                    csr_resp_json = str(csr_resp.json())
                    if (csr_resp.status_code == 200):
                        msg = ": CSR update accepted for " + cloud_service['id']
                        LOG.info("Service " + serv_id + msg)
                    else:
                        msg = ": CSR update not accepted: " + csr_resp_json
                        LOG.info("Service " + serv_id + msg)
                        error = {'http_code': csr_resp.status_code,
                                 'message': csr_resp_json}
                except:
                    error = {'http_code': '0',
                             'message': 'Timeout when contacting CSR repo'}

                if error is not None:
                    self.error_handling(serv_id, t.GK_CREATE, error)
                    return

        descriptor = self.services[serv_id]['service']['nsd'] if is_nsd else self.services[serv_id]['service']['cosd']

        vnfr_ids = []
        for function in self.services[serv_id]['function']:
            vnfr_ids.append(function['id'])

        csr_ids = []
        for cloud_service in self.services[serv_id]['cloud_service']:
            csr_ids.append(cloud_service['id'])

        if is_nsd:
            record = tools.build_nsr(request_status, descriptor, vnfr_ids, serv_id)
        else:
            record = tools.build_cosr(request_status, descriptor, vnfr_ids, csr_ids, serv_id)

        LOG.debug("Record to be stored: " + yaml.dump(record))

        error = None

        try:
            header = {'Content-Type': 'application/json'}
            url = t.NSR_REPOSITORY_URL + 'ns-instances' if is_nsd else t.COSR_REPOSITORY_URL + 'cos-instances'
            record_resp = requests.post(url,
                                     data=json.dumps(record),
                                     headers=header,
                                     timeout=1.0)
            record_resp_json = record_resp.json()
            if (record_resp.status_code == 200):
                msg = ": Record accepted and stored for instance " + serv_id
                LOG.info("Service " + serv_id + msg)
            else:
                msg = ": Record not accepted: " + str(record_resp_json)
                LOG.info("Service " + serv_id + msg)
                error = {'http_code': record_resp.status_code,
                         'message': record_resp_json}
        except:
            error = {'http_code': '0',
                     'message': 'Timeout when contacting record repo'}

        self.services[serv_id]['service']['nsr' if is_nsd else 'cosr'] = record

        if error is not None:
            self.error_handling(serv_id, t.GK_CREATE, error)

        return

    def vnf_chain(self, serv_id):
        """
        This method instructs the IA how to chain the functions together.
        """

        # We're gonna skip chaining for now if we're handling a complex service.
        # TODO: Implement chaining for complex services
        if 'cosd' in self.services[serv_id]['service']:
            return

        corr_id = str(uuid.uuid4())
        self.services[serv_id]['act_corr_id'] = corr_id

        chain = {}
        chain["service_instance_id"] = serv_id
        chain["nsd"] = self.services[serv_id]['service']['nsd']

        vnfrs = []
        vnfds = []

        for function in self.services[serv_id]['function']:
            vnfrs.append(function['vnfr'])

            vnfd = function['vnfd']
            vnfd['instance_uuid'] = function['id']
            vnfds.append(vnfd)

        chain['vnfrs'] = vnfrs
        chain['vnfds'] = vnfds

        # Add egress and ingress fields
        chain['nap'] = {}
        nap_empty = True

        if self.services[serv_id]['ingress'] is not None:
            chain['nap']['ingresses'] = self.services[serv_id]['ingress']
            nap_empty = False
        if self.services[serv_id]['egress'] is not None:
            chain['nap']['egresses'] = self.services[serv_id]['egress']
            nap_empty = False

        # Check if `nap` is empty
        if nap_empty:
            chain.pop('nap')

        LOG.info(str(yaml.dump(chain)))
        self.manoconn.call_async(self.IA_chain_response,
                                 t.IA_CONF_CHAIN,
                                 yaml.dump(chain),
                                 correlation_id=corr_id)

        LOG.info("Service " + serv_id + ": Requested to chain the VNFs.")
        # Pause the chain of tasks to wait for response
        self.services[serv_id]['pause_chain'] = True

    def IA_chain_response(self, ch, method, prop, payload):
        """
        This method handles the IA response to the chain request
        """
        # Get the serv_id of this service
        serv_id = tools.servid_from_corrid(self.services,
                                           prop.correlation_id)

        message = yaml.load(payload)

        LOG.info("Service " + serv_id + ": Chaining request completed.")

        if message['message'] != '':
            error = message['message']
            LOG.info('Error occured during chaining: ' + str(error))
            self.error_handling(serv_id, t.GK_CREATE, error)

        self.start_next_task(serv_id)

    def vnf_unchain(self, serv_id):
        """
        This method instructs the IA to unchain the functions in the service.
        """
        msg = ": Deconfiguring the chaining of the service"
        LOG.info("Service " + serv_id + msg)

        corr_id = str(uuid.uuid4())
        self.services[serv_id]['act_corr_id'] = corr_id

        payload = json.dumps({'service_instance_id': serv_id})
        self.manoconn.call_async(self.IA_unchain_response,
                                 t.IA_DECONF_CHAIN,
                                 payload,
                                 correlation_id=corr_id)

        # Pause the chain of tasks to wait for response
        self.services[serv_id]['pause_chain'] = True

    def IA_unchain_response(self, ch, method, prop, payload):
        """
        This method handles the IA response on the unchain request
        """

        # Get the serv_id of this service
        serv_id = tools.servid_from_corrid(self.services,
                                           prop.correlation_id)

        message = yaml.load(payload)

        if message['request_status'] == 'COMPLETED':
            msg = ": Response from IA: Service unchaining succeeded."
            LOG.info("Service " + serv_id + msg)
        else:
            error = message['message']
            msg = ": Response from IA: Service unchaining failed: " + error
            LOG.info("Service " + serv_id + msg)
            self.error_handling(serv_id, t.GK_KILL, error)
            return

        self.start_next_task(serv_id)

    def terminate_service(self, serv_id):
        """
        This method requests the termination of a service to the IA
        """
        LOG.info("Service " + serv_id + ": Requesting IA to terminate service")

        corr_id = str(uuid.uuid4())
        self.services[serv_id]['act_corr_id'] = corr_id

        payload = json.dumps({'instance_uuid': serv_id})
        self.manoconn.call_async(self.IA_termination_response,
                                 t.IA_REMOVE,
                                 payload,
                                 correlation_id=corr_id)

        # Pause the chain of tasks to wait for response
        self.services[serv_id]['pause_chain'] = True

    def IA_termination_response(self, ch, method, prop, payload):
        """
        This method handles the response from the IA on the termination call.
        """

        # Get the serv_id of this service
        serv_id = tools.servid_from_corrid(self.services,
                                           prop.correlation_id)

        message = yaml.load(payload)

        if message['request_status'] == 'COMPLETED':
            msg = ": Response from IA: Service termination succeeded."
            LOG.info("Service " + serv_id + msg)
        else:
            error = message['message']
            msg = ": IA response: Service termination failed: " + error
            LOG.info("Service " + serv_id + msg)
            self.error_handling(serv_id, t.GK_KILL, error)
            return

        self.start_next_task(serv_id)

    def terminate_ssms(self, serv_id, require_resp=True):
        """
        This method contacts the SMR to terminate the running ssms.
        """

        if self.services[serv_id]['service']['ssm']:
            corr_id = str(uuid.uuid4())
            self.services[serv_id]['act_corr_id'] = corr_id

            LOG.info("Service " + serv_id + ": Setting kill flag for ssms.")

            nsd = self.services[serv_id]['service']['nsd']

            for ssm in nsd['service_specific_managers']:
                if 'options' not in ssm.keys():
                    ssm['options'] = []
                ssm['options'].append({'key': 'termination', 'value': 'true'})

            msg = ": SSM part of NSD: " + str(nsd['service_specific_managers'])
            LOG.info("Service " + serv_id + msg)

            payload = yaml.dump({'NSD': nsd, 'UUID': serv_id})

            if require_resp:
                self.manoconn.call_async(self.ssm_termination_response,
                                         t.SSM_TERM,
                                         payload,
                                         correlation_id=corr_id)

                # Pause the chain of tasks to wait for response
                self.services[serv_id]['pause_chain'] = True

            else:
                self.manoconn.call_async(self.no_resp_needed,
                                         t.SSM_TERM,
                                         payload)

    def ssm_termination_response(self, ch, method, prop, payload):
        """
        This method handles a response from the SMR on the ssm termination
        call.
        """
        # Get the serv_id of this service
        serv_id = tools.servid_from_corrid(self.services,
                                           prop.correlation_id)

        message = yaml.load(payload)
        LOG.info("Response from SMR: " + str(message))

        self.start_next_task(serv_id)

    def terminate_fsms(self, serv_id, require_resp=True):
        """
        This method contacts the SMR to terminate the running ssms.
        """
        for vnf in self.services[serv_id]['function']:

            if 'function_specific_managers' in vnf['vnfd'].keys():

                # If the vnf has fsms, continue with this process.
                corr_id = str(uuid.uuid4())
                self.services[serv_id]['act_corr_id'] = corr_id

                LOG.info("Service " + serv_id +
                         ": Setting termination flag for fsms.")

                LOG.info(str(vnf['vnfd']))
                for fsm in vnf['vnfd']['function_specific_managers']:
                    if 'options' not in fsm.keys():
                        fsm['options'] = []
                    fsm['options'].append({'key': 'termination',
                                          'value': 'true'})

                vnfd = vnf['vnfd']
                fsm_segment = str(vnfd['function_specific_managers'])
                msg = ": FSM in VNFD: " + fsm_segment
                LOG.info("Service " + serv_id + msg)

                payload = yaml.dump({'VNFD': vnf['vnfd'], 'UUID': vnf['id']})

                self.manoconn.call_async(self.no_resp_needed,
                                         t.FSM_TERM,
                                         payload)

    def fsm_termination_response(self, ch, method, prop, payload):
        """
        This method handles a response from the SMR on the ssm termination
        call.
        """
        serv_id = tools.servid_from_corrid(self.services,
                                           prop.correlation_id)

        message = yaml.load(payload)
        LOG.info("Response from SMR: " + str(message))

        self.start_next_task(serv_id)

    def no_resp_needed(self, ch, method, prop, payload):
        """
        Dummy response method when other component will send a response, but
        SLM does not need it
        """

        pass

    def update_records_to_terminated(self, serv_id):
        """
        This method updates the records of the service and function instances
        to reflect that they have been terminated.
        """

        error = None

        is_nsd = 'nsr' in self.services[serv_id]['service']

        record = self.services[serv_id]['service']['nsr' if is_nsd else 'cosr']

        # Updating the version number
        old_version = int(record['version'])
        cur_version = old_version + 1
        record['version'] = str(cur_version)

        # Updating the record
        record_id = serv_id
        record['status'] = "terminated"
        record['id'] = record_id
        del record["uuid"]
        del record["updated_at"]
        del record["created_at"]

        # Put it
        url = t.NSR_REPOSITORY_URL + 'ns-instances/' + record_id if is_nsd else t.COSR_REPOSITORY_URL + 'cos-instances/' + record_id
        header = {'Content-Type': 'application/json'}

        LOG.info("Service " + serv_id + ": Record update: " + url)

        try:
            record_resp = requests.put(url,
                                    data=json.dumps(record),
                                    headers=header,
                                    timeout=1.0)
            record_resp_json = str(record_resp.json())

            if (record_resp.status_code == 200):
                msg = ": Record update accepted for " + record_id
                LOG.info("Service " + serv_id + msg)
            else:
                msg = ": Record update not accepted: " + record_resp_json
                LOG.info("Service " + serv_id + msg)
                error = {'http_code': record_resp.status_code,
                         'message': record_resp_json}
        except:
            error = {'http_code': '0',
                     'message': 'Timeout when contacting NSR repo'}

        for vnf in self.services[serv_id]['function']:
            vnfr = vnf["vnfr"]
            vnfr_id = vnf["id"]

            # Updating version number
            old_version = int(vnfr['version'])
            cur_version = old_version + 1
            vnfr['version'] = str(cur_version)

            # Updating the record
            vnfr['status'] = "terminated"
            vnfr["id"] = vnfr_id
            del vnfr["uuid"]
            del vnfr["updated_at"]
            del vnfr["created_at"]

            # Put it
            url = t.VNFR_REPOSITORY_URL + 'vnf-instances/' + vnfr_id
            header = {'Content-Type': 'application/json'}

            LOG.info("Service " + serv_id + ": VNFR update: " + url)

            try:
                vnfr_resp = requests.put(url,
                                         data=json.dumps(vnfr),
                                         headers=header,
                                         timeout=1.0)
                vnfr_resp_json = str(vnfr_resp.json())

                if (vnfr_resp.status_code == 200):
                    msg = ": VNFR update accepted for " + vnfr_id
                    LOG.info("Service " + serv_id + msg)
                else:
                    msg = ": VNFR update not accepted: " + vnfr_resp_json
                    LOG.info("Service " + serv_id + msg)
                    error = {'http_code': vnfr_resp.status_code,
                             'message': vnfr_resp_json}
            except:
                error = {'http_code': '0',
                         'message': 'Timeout when contacting VNFR repo'}

        for cloud_service in self.services[serv_id]['cloud_service']:
            csr = cloud_service["csr"]
            csr_id = csr["uuid"]

            # Updating version number
            old_version = int(csr['version'])
            cur_version = old_version + 1
            csr['version'] = str(cur_version)

            # Updating the record
            csr['status'] = "terminated"
            csr['id'] = csr_id
            del csr["uuid"]
            del csr["updated_at"]
            del csr["created_at"]

            # Put it
            url = t.CSR_REPOSITORY_URL + 'cs-instances/' + csr_id
            header = {'Content-Type': 'application/json'}

            LOG.info("Service " + serv_id + ": CSR update: " + url)

            try:
                csr_resp = requests.put(url,
                                         data=json.dumps(csr),
                                         headers=header,
                                         timeout=1.0)
                csr_resp_json = str(csr_resp.json())

                if (csr_resp.status_code == 200):
                    msg = ": CSR update accepted for " + csr_id
                    LOG.info("Service " + serv_id + msg)
                else:
                    msg = ": CSR update not accepted: " + csr_resp_json
                    LOG.info("Service " + serv_id + msg)
                    error = {'http_code': csr_resp.status_code,
                             'message': csr_resp_json}
            except:
                error = {'http_code': '0',
                         'message': 'Timeout when contacting VNFR repo'}

        if error is not None:
            self.error_handling(serv_id, t.GK_KILL, error)

    def wan_configure(self, serv_id):
        """
        This method configures the WAN of a service
        """

        LOG.info("Service " + serv_id + ": WAN Configuration")
        corr_id = str(uuid.uuid4())
        self.services[serv_id]['act_corr_id'] = corr_id

        message = {}
        message['service_instance_id'] = serv_id

        # Add egress and ingress fields
        message['nap'] = {}
        nap_empty = True

        if self.services[serv_id]['ingress'] is not None:
            message['nap']['ingresses'] = self.services[serv_id]['ingress']
            nap_empty = False
        if self.services[serv_id]['egress'] is not None:
            message['nap']['egresses'] = self.services[serv_id]['egress']
            nap_empty = False

        # Check if `nap` is empty
        if nap_empty:
            message.pop('nap')

        # Create ordered vim_list
        ordered_vim = []
        calc_list = self.services[serv_id]['service']['ordered_vim_list']
        for vim in calc_list:
            ordered_vim.append({'uuid': vim, 'order': calc_list.index(vim)})

        message['vim_list'] = ordered_vim

        self.manoconn.call_async(self.wan_configure_response,
                                 t.IA_CONF_WAN,
                                 yaml.dump(message),
                                 correlation_id=corr_id)

        # # Pause the chain of tasks to wait for response
        self.services[serv_id]['pause_chain'] = True

    def wan_configure_response(self, ch, method, prop, payload):
        """
        This method handles the IA response to the WAN request
        """
        # Get the serv_id of this service
        serv_id = tools.servid_from_corrid(self.services, prop.correlation_id)

        message = yaml.load(payload)

        LOG.info("Service " + serv_id + ": WAN configure request completed.")

        if message['message'] != '':
            error = message['message']
            LOG.info('Error occured during WAN: ' + str(error))
            self.error_handling(serv_id, t.GK_CREATE, error)

        self.start_next_task(serv_id)

    def wan_deconfigure(self, serv_id):
        """
        This method will deconfigure the WAN
        """

        LOG.info("Service " + serv_id + ": WAN Deonfiguration")
        corr_id = str(uuid.uuid4())
        self.services[serv_id]['act_corr_id'] = corr_id

        message = {}
        message['service_instance_id'] = serv_id

        self.manoconn.call_async(self.wan_deconfigure_response,
                                 t.IA_DECONF_WAN,
                                 yaml.dump(message),
                                 correlation_id=corr_id)

        self.services[serv_id]['pause_chain'] = True

    def wan_deconfigure_response(self, ch, method, prop, payload):
        """
        This method handles responses on the wan_deconfigure call
        """

        # Get the serv_id of this service
        serv_id = tools.servid_from_corrid(self.services, prop.correlation_id)

        message = yaml.load(payload)

        LOG.info("Service " + serv_id + ": WAN deconfigure request completed.")

        if message['message'] != '':
            error = message['message']
            LOG.info('Error occured during deconfiguring WAN: ' + str(error))
            self.error_handling(serv_id, t.GK_KILL, error)

        self.start_next_task(serv_id)

    def stop_monitoring(self, serv_id):
        """
        This method stops the monitoring of a service.
        """

        url = t.MONITORING_URL + "services/" + serv_id
        msg = ": Stopping Monitoring by sending on " + url
        LOG.info("Service " + serv_id + msg)

        error = None
        # try:
        header = {'Content-Type': 'application/json'}
        mon_resp = requests.delete(url,
                                   headers=header,
                                   timeout=10.0)
        msg = ": response from monitoring manager: " + str(mon_resp)
        LOG.info("Service " + serv_id + msg)

        if (mon_resp.status_code == 204):
            LOG.info("Service " + serv_id + ": Monitoring DEL msg accepted")

        else:
            monitoring_json = mon_resp.json()
            LOG.info("Service " + serv_id + ": Monitoring DEL msg not acceptd")
            msg = ": Monitoring response: " + str(monitoring_json)
            LOG.info("Service " + serv_id + msg)
            error = {'http_code': mon_resp.status_code,
                     'message': monitoring_json}

        # except:
        #     LOG.info('timeout on monitoring communication.')
        #     error = {'http_code': '0',
        #              'message': 'Timeout when contacting monitoring manager'}

        # If an error occured, the workflow is aborted and the GK is informed
        if error is not None:
            self.error_handling(serv_id, t.GK_KILL, error)

        return

    def start_monitoring(self, serv_id):
        """
        This method instructs the monitoring manager to start monitoring
        """

        is_nsd = 'nsd' in self.services[serv_id]['service']

        # Configure the Monitoring SSM, if present
        if 'monitor' in self.services[serv_id]['service']['ssm'].keys():
            LOG.info("Service " + serv_id + ": Sending descriptors to Mon SSM")
            message = {}
            message['nsd' if is_nsd else 'cosd'] = self.services[serv_id]['service']['nsd' if is_nsd else 'cosd']
            message['nsr' if is_nsd else 'cosr'] = self.services[serv_id]['service']['nsr' if is_nsd else 'cosr']
            vnfs = []
            for vnf in self.services[serv_id]['function']:
                vnfs.append({'vnfd': vnf['vnfd'],
                             'id': vnf['id'],
                             'vnfr': vnf['vnfr']})
            css = []
            for cs in self.services[serv_id]['cloud_service']:
                css.append({'csd': cs['csd'],
                             'id': cs['id'],
                             'csr': cs['csr']})
            message['css'] = css
            message['vnfs'] = vnfs
            message['ssm_type'] = 'monitor'
            topic = 'generic.ssm.' + serv_id

            ssm_conn = self.ssm_connections[serv_id]

            ssm_conn.notify(topic, yaml.dump(message))

            # subscribe to messages from the monitoring SSM
            topic = t.FROM_MON_SSM + serv_id
            ssm_conn.subscribe(self.from_monitoring_ssm, topic)

        LOG.info("Service " + serv_id + ": Setting up Monitoring Manager")
        service = self.services[serv_id]['service']
        functions = self.services[serv_id]['function']
        cloud_services = self.services[serv_id]['cloud_service']
        userdata = self.services[serv_id]['user_data']

        mon_mess = tools.build_monitoring_message(service, functions, cloud_services, userdata)

        LOG.debug("Monitoring message created: " + yaml.dump(mon_mess))

        error = None
        try:
            header = {'Content-Type': 'application/json'}
            mon_resp = requests.post(t.MONITORING_URL + 'service/new',
                                     data=json.dumps(mon_mess),
                                     headers=header,
                                     timeout=10.0)
            monitoring_json = mon_resp.json()

            if (mon_resp.status_code == 200):
                LOG.info("Service " + serv_id + ": Monitoring started")

            else:
                LOG.info("Service " + serv_id + ": Monitoring msg not acceptd")
                msg = ": Monitoring response: " + str(monitoring_json)
                LOG.info("Service " + serv_id + msg)
                error = {'http_code': mon_resp.status_code,
                         'message': mon_resp.json()}

        except:
            LOG.info("Service " + serv_id + ": timeout on monitoring server.")
            error = {'http_code': '0',
                     'message': 'Timeout when contacting server'}

        # If an error occured, the workflow is aborted and the GK is informed
        if error is not None:
            self.error_handling(serv_id, t.GK_CREATE, error)

        return

    def inform_gk_instantiation(self, serv_id):
        """
        This method informs the gatekeeper.
        """
        LOG.info("Service " + serv_id + ": Reporting result to GK")

        is_nsd = 'nsd' in self.services[serv_id]['service']

        message = {}

        message['status'] = 'READY'
        message['error'] = None
        message['timestamp'] = time.time()
        if is_nsd:
            message['nsr'] = self.services[serv_id]['service']['nsr']
        else:
            message['cosr'] = self.services[serv_id]['service']['cosr']
        message['vnfrs'] = []
        message['csrs'] = []

        for function in self.services[serv_id]['function']:
            message['vnfrs'].append(function['vnfr'])

        for cloud_service in self.services[serv_id]['cloud_service']:
            message['csrs'].append(cloud_service['csr'])

        LOG.debug("Payload of message " + str(message))

        orig_corr_id = self.services[serv_id]['original_corr_id']
        self.manoconn.notify(t.GK_CREATE,
                             yaml.dump(message),
                             correlation_id=orig_corr_id)

    def inform_gk(self, serv_id):
        """
        This method informs the gatekeeper.
        """
        topic = self.services[serv_id]['topic']

        LOG.info("Service " + serv_id + ": Reporting result to GK on " + topic)

        message = {}

        message['status'] = 'READY'
        message['error'] = None
        message['timestamp'] = time.time()

        LOG.debug("Payload of message " + str(message))

        orig_corr_id = self.services[serv_id]['original_corr_id']
        self.manoconn.notify(topic,
                             yaml.dump(message),
                             correlation_id=orig_corr_id)


###########
# SLM tasks
###########

    def add_service_to_ledger(self, payload, corr_id):
        """
        This method adds new services with their specifics to the ledger,
        so other functions can use this information.

        :param payload: the payload of the received message
        :param corr_id: the correlation id of the received message
        """

        # Generate an istance uuid for the service
        serv_id = str(uuid.uuid4())

        descriptor = payload['NSD'] if 'NSD' in payload else payload['COSD']

        # Add the service to the ledger and add instance ids
        self.services[serv_id] = {}
        self.services[serv_id]['service'] = {}
        if 'NSD' in payload:
            self.services[serv_id]['service']['nsd'] = payload['NSD']
        else:
            self.services[serv_id]['service']['cosd'] = payload['COSD']
        self.services[serv_id]['service']['id'] = serv_id

        msg = ": NSD uuid is " + str(descriptor['uuid'])
        LOG.info("Service " + serv_id + msg)

        self.services[serv_id]['function'] = []
        self.services[serv_id]['cloud_service'] = []
        for key in payload.keys():
            if key[:4] == 'VNFD':
                vnf_id = str(uuid.uuid4())
                msg = "VNFD instance id generated: " + vnf_id
                LOG.info("Service " + serv_id + msg)
                vnfd = payload[key]
                vnf_base_dict = {'start': {'trigger': True, 'payload': {}},
                                 'stop': {'trigger': True, 'payload': {}},
                                 'configure': {'trigger': True, 'payload': {}},
                                 'scale': {'trigger': True, 'payload': {}},
                                 'vnfd': vnfd,
                                 'id': vnf_id}
                self.services[serv_id]['function'].append(vnf_base_dict)
            elif key[:3] == 'CSD':
                cs_id = str(uuid.uuid4())
                msg = "CSD instance id generated: " + cs_id
                LOG.info("Service " + serv_id + msg)
                csd = payload[key]
                cs_base_dict = {'start': {'trigger': True, 'payload': {}},
                                 'stop': {'trigger': True, 'payload': {}},
                                 'configure': {'trigger': True, 'payload': {}},
                                 'scale': {'trigger': True, 'payload': {}},
                                 'csd': csd,
                                 'id': cs_id}
                self.services[serv_id]['cloud_service'].append(cs_base_dict)

        # Add to correlation id to the ledger
        self.services[serv_id]['original_corr_id'] = corr_id

        # Add payload to the ledger
        self.services[serv_id]['payload'] = payload

        self.services[serv_id]['infrastructure'] = {}

        # Create the service schedule
        self.services[serv_id]['schedule'] = []

        # Create a log for the task results
        self.services[serv_id]['task_log'] = []

        # Create the SSM dict if SSMs are defined in NSD
        ssm_dict = tools.get_sm_from_descriptor(descriptor)

        self.services[serv_id]['service']['ssm'] = ssm_dict

        print(self.services[serv_id]['service']['ssm'])

        # Create counter for vnfs and css
        self.services[serv_id]['vnfs_to_resp'] = 0
        self.services[serv_id]['css_to_resp'] = 0

        # Create the chain pause and kill flag
        self.services[serv_id]['pause_chain'] = False
        self.services[serv_id]['kill_chain'] = False

        # Add ingress and egress fields
        self.services[serv_id]['ingress'] = None
        self.services[serv_id]['egress'] = None

        if 'ingresses' in payload.keys():
            if payload['ingresses']:
                if payload['ingresses'] != '[]':
                    self.services[serv_id]['ingress'] = payload['ingresses']

        if 'egresses' in payload.keys():
            if payload['egresses']:
                if payload['ingresses'] != '[]':
                    self.services[serv_id]['egress'] = payload['egresses']

        # Add user data to ledger
        self.services[serv_id]['user_data'] = payload['user_data']

        # Add keys to ledger
        try:
            keys = payload['user_data']['customer']['keys']
            self.services[serv_id]['public_key'] = keys['public']
            self.services[serv_id]['private_key'] = keys['private']
        except:
            msg = ": extracting keys failed " + str(payload['user_data'])
            LOG.info("Service " + serv_id + msg)
            self.services[serv_id]['public_key'] = None
            self.services[serv_id]['private_key'] = None

        return serv_id

    def recreate_ledger(self, corr_id, serv_id):
        """
        This method recreates an entry in the ledger for a service
        based on the service instance id.

        :param corr_id: the correlation id of the received message
        :param serv_id: the service instance id
        """

        def request_returned_with_error(request):
            code = str(request['error'])
            mess = str(request['content'])
            LOG.info("Retrieving of record failed: " + code + " " + mess)
            # TODO: get out of this

        # Update the token of the SLM
        if self.token is None:
            self.register_slm_with_gk()

        token = tools.client_login(t.GK_LOGIN, self.clientId, self.password)
        self.token = token
        LOG.info("Service " + serv_id + ": new token: " + str(self.token))

        # base of the ledger
        self.services[serv_id] = {}
        self.services[serv_id]['original_corr_id'] = corr_id
        self.services[serv_id]['service'] = {}

        # Retrieve the service record based on the service instance id
        is_ns = True
        base = t.NSR_REPOSITORY_URL + "ns-instances/"
        request = tools.getRestData(base, serv_id)

        if request['error'] is not None:
            # Try COSRs
            LOG.info("NSR not found, trying COSR")
            is_ns = False
            base = t.COSR_REPOSITORY_URL + "cos-instances/"
            request = tools.getRestData(base, serv_id)

        if request['error'] is not None:
            request_returned_with_error(request)
            return

        self.services[serv_id]['service']['nsr' if is_ns else 'cosr'] = request['content']
        LOG.info("Service " + serv_id + ": Recreating ledger: Record retrieved.")

        # Retrieve the NSD
        record = self.services[serv_id]['service']['nsr' if is_ns else 'cosr']
        descriptor_uuid = record['descriptor_reference']

        url = t.GK_SERVICES if is_ns else t.GK_COMPLEX_SERVICES
        request = tools.getRestData(url, descriptor_uuid, token=self.token)

        if request['error'] is not None:
            request_returned_with_error(request)
            return

        self.services[serv_id]['service']['nsd' if is_ns else 'cosd'] = request['content']['nsd' if is_ns else 'cosd']
        LOG.info("Service " + serv_id + ": Recreating ledger: Descriptor retrieved.")

        # Retrieve the function records based on the service record
        self.services[serv_id]['function'] = []
        self.services[serv_id]['cloud_service'] = []
        record = self.services[serv_id]['service']['nsr' if is_ns else 'cosr']
        for vnf in record['network_functions']:
            base = t.VNFR_REPOSITORY_URL + "vnf-instances/"
            request = tools.getRestData(base, vnf['vnfr_id'])

            if request['error'] is not None:
                request_returned_with_error(request)
                return

            new_function = {'id': vnf['vnfr_id'],
                            'start': {'trigger': True, 'payload': {}},
                            'stop': {'trigger': True, 'payload': {}},
                            'configure': {'trigger': True, 'payload': {}},
                            'scale': {'trigger': True, 'payload': {}},
                            'vnfr': request['content']}

            self.services[serv_id]['function'].append(new_function)
            msg = ": Recreating ledger: VNFR retrieved."
            LOG.info("Service " + serv_id + msg)

        # Retrieve the VNFDS based on the function records
        for vnf in self.services[serv_id]['function']:
            vnfd_id = vnf['vnfr']['descriptor_reference']

            req = tools.getRestData(t.GK_FUNCTIONS, vnfd_id, token=self.token)

            if req['error'] is not None:
                request_returned_with_error(req)
                return

            vnf['vnfd'] = req['content']['vnfd']
            LOG.info("Service " + serv_id + ": Recreate: VNFD retrieved.")

        if 'cloud_services' in record:
            for cloud_service in record['cloud_services']:
                base = t.CSR_REPOSITORY_URL + "cs-instances/"
                request = tools.getRestData(base, cloud_service['csr_id'])

                if request['error'] is not None:
                    request_returned_with_error(request)
                    return

                new_cloud_service = {'id': cloud_service['csr_id'],
                                'start': {'trigger': True, 'payload': {}},
                                'stop': {'trigger': True, 'payload': {}},
                                'configure': {'trigger': True, 'payload': {}},
                                'scale': {'trigger': True, 'payload': {}},
                                'csr': request['content']}

                self.services[serv_id]['cloud_service'].append(new_cloud_service)
                msg = ": Recreating ledger: CSR retrieved."
                LOG.info("Service " + serv_id + msg)

        # Retrieve the CSDs based on the cloud service records
        for cloud_service in self.services[serv_id]['cloud_service']:
            csd_id = cloud_service['csr']['descriptor_reference']

            req = tools.getRestData(t.GK_CLOUD_SERVICES, csd_id, token=self.token)

            if req['error'] is not None:
                request_returned_with_error(req)
                return

            cloud_service['csd'] = req['content']['csd']
            LOG.info("Service " + serv_id + ": Recreate: CSD retrieved.")

        LOG.info("Service " +
                 serv_id + ": Recreating ledger: VNFDs and CSDs retrieved.")

        # Retrieve the deployed SSMs based on the NSD
        descriptor = self.services[serv_id]['service']['nsd' if is_ns else 'cosd']
        ssm_dict = tools.get_sm_from_descriptor(descriptor)

        self.services[serv_id]['service']['ssm'] = ssm_dict

        LOG.info("Service " + serv_id + ": ssm_dict: " + str(ssm_dict))

        # Retrieve the deployed FSMs based on the VNFD
        for vnf in self.services[serv_id]['function']:
            vnfd = vnf['vnfd']
            fsm_dict = tools.get_sm_from_descriptor(vnfd)
            vnf['fsm'] = fsm_dict
            LOG.info(str(vnfd))
            LOG.info(str(fsm_dict))

        # Create the service schedule
        self.services[serv_id]['schedule'] = []

        # Create some necessary fields for the ledger
        self.services[serv_id]['kill_chain'] = False
        self.services[serv_id]['infrastructure'] = {}
        self.services[serv_id]['task_log'] = []
        self.services[serv_id]['vnfs_to_resp'] = 0
        self.services[serv_id]['css_to_resp'] = 0
        self.services[serv_id]['pause_chain'] = False
        self.services[serv_id]['error'] = None

        return

    def validate_deploy_request(self, serv_id):
        """
        This metod checks the format of a received request. All neccesary
        fields should be present, and the available fields should not be
        conflicting with each other.

        :param serv_id: the instance id of the service
        """
        payload = self.services[serv_id]['payload']
        corr_id = self.services[serv_id]['original_corr_id']

        # TODO: check whether correlation_id is already being used.

        # The service request in the yaml file should be a dictionary
        if not isinstance(payload, dict):
            msg = ": Validation of request completed. Status: Not a Dict"
            LOG.info("Service " + serv_id + msg)
            response = "Request " + corr_id + ": payload is not a dict."
            self.services[serv_id]['status'] = 'ERROR'
            self.services[serv_id]['error'] = response
            return

        # The dictionary should contain a 'NSD' key
        if 'NSD' not in payload.keys() and 'COSD' not in payload.keys():
            msg = ": Validation of request completed. Status: No NSD/COSD"
            LOG.info("Service " + serv_id + msg)
            response = "Request " + corr_id + ": NSD/COSD is not a dict."
            self.services[serv_id]['status'] = 'ERROR'
            self.services[serv_id]['error'] = response
            return

        if 'NSD' in payload:
            descriptor = payload['NSD']
        else:
            descriptor = payload['COSD']

        # There should be as many VNFD keys in the dictionary as their
        # are network functions listed to the NSD.
        number_of_vnfds = 0
        for key in payload.keys():
            if key[:4] == 'VNFD':
                number_of_vnfds = number_of_vnfds + 1

        if (not 'network_functions' in descriptor and number_of_vnfds > 0) or \
                ('network_functions' in descriptor and len(descriptor['network_functions']) != number_of_vnfds):
            msg = ": Validation request completed. Number of VNFDs incorrect"
            LOG.info("Service " + serv_id + msg)
            response = "Request " + corr_id + ": # of VNFDs doesn't match NSD."
            self.services[serv_id]['status'] = 'ERROR'
            self.services[serv_id]['error'] = response
            return

        # There should be as many CSD keys in the dictionary as their
        # are cloud services listed to the NSD.
        number_of_csds = 0
        for key in payload.keys():
            if key[:3] == 'CSD':
                number_of_csds = number_of_csds + 1

        if (not 'cloud_services' in descriptor and number_of_csds > 0) or \
                ('cloud_services' in descriptor and len(descriptor['cloud_services']) != number_of_csds):
            msg = ": Validation request completed. Number of CSDs incorrect"
            LOG.info("Service " + serv_id + msg)
            response = "Request " + corr_id + ": # of CSDs doesn't match NSD."
            self.services[serv_id]['status'] = 'ERROR'
            self.services[serv_id]['error'] = response
            return

        # Check whether VNFDs or CSDs are empty.
        for key in payload.keys():
            if key[:4] == 'VNFD':
                if payload[key] is None:
                    msg = ": Validation request completed. Empty VNFD."
                    LOG.info("Service " + serv_id + msg)
                    response = "Request " + corr_id + ": empty VNFD."
                    self.services[serv_id]['status'] = 'ERROR'
                    self.services[serv_id]['error'] = response
                    return
            if key[:3] == 'CSD':
                if payload[key] is None:
                    msg = ": Validation request completed. Empty CSD."
                    LOG.info("Service " + serv_id + msg)
                    response = "Request " + corr_id + ": empty CSD."
                    self.services[serv_id]['status'] = 'ERROR'
                    self.services[serv_id]['error'] = response
                    return

        msg = ": Validation of request completed. Status: Instantiating"
        LOG.info("Service " + serv_id + msg)
        # If all tests succeed, the status changes to 'INSTANTIATING'
        message = {'status': 'INSTANTIATING', 'error': None}
        self.services[serv_id]['status'] = 'INSTANTIATING'
        self.services[serv_id]['error'] = None
        return

#        except Exception as e:
#            tracebackString = traceback.format_exc(e)
#            self.services[serv_id]['traceback'] = tracebackString

    def SLM_mapping(self, serv_id):
        """
        This method is used if the SLM is responsible for the placement.

        :param serv_id: The instance uuid of the service
        """
        corr_id = str(uuid.uuid4())
        self.services[serv_id]['act_corr_id'] = corr_id

        LOG.info("Service " + serv_id + ": Calculating the placement")
        topology = self.services[serv_id]['infrastructure']['topology']
        if 'nsd' in self.services[serv_id]['service']:
            NSD = self.services[serv_id]['service']['nsd']
            functions = self.services[serv_id]['function']

            content = {'nsd': NSD,
                       'functions': functions,
                       'topology': topology,
                       'serv_id': serv_id}
        else:
            COSD = self.services[serv_id]['service']['cosd']
            functions = self.services[serv_id]['function']
            cloud_services = self.services[serv_id]['cloud_service']

            content = {'cosd': COSD,
                       'functions': functions,
                       'cloud_services': cloud_services,
                       'topology': topology,
                       'serv_id': serv_id}

        content['nap'] = {}

        if self.services[serv_id]['ingress'] is not None:
            content['nap']['ingresses'] = self.services[serv_id]['ingress']
        if self.services[serv_id]['egress'] is not None:
            content['nap']['egresses'] = self.services[serv_id]['egress']

        self.manoconn.call_async(self.resp_mapping,
                                 t.MANO_PLACE,
                                 yaml.dump(content),
                                 correlation_id=corr_id)

        self.services[serv_id]['pause_chain'] = True
        LOG.info("Service " + serv_id + ": Placement request sent")

    def resp_mapping(self, ch, method, prop, payload):
        """
        This method handles the response on a mapping request
        """
        content = yaml.load(payload)
        mapping = content["mapping"]

        serv_id = tools.servid_from_corrid(self.services, prop.correlation_id)
        LOG.info("Service " + serv_id + ": Placement response received")

        if mapping is None:
            # The GK should be informed that the placement failed and the
            # deployment was aborted.
            LOG.info("Service " + serv_id + ": Placement not possible")
            self.error_handling(serv_id,
                                t.GK_CREATE,
                                'Unable to perform placement.')

            return

        else:
            # Add mapping to ledger
            LOG.info("Service " + serv_id + ": Placement completed")
            LOG.debug("Calculated SLM placement: " + str(mapping))
            self.services[serv_id]['service']['mapping'] = mapping
            for function in self.services[serv_id]['function']:
                vnf_id = function['id']
                function['vim_uuid'] = mapping[vnf_id]['vim']
            for cloud_service in self.services[serv_id]['cloud_service']:
                cs_id = cloud_service['id']
                cloud_service['vim_uuid'] = mapping[cs_id]['vim']

        # Check if the placement does not contain any loops
        vim_list = tools.get_ordered_vim_list(self.services[serv_id])

        if vim_list is None:
            msg = 'Placement contains loop, improve Placement Plugin'
            # the placement contains loops
            self.error_handling(serv_id,
                                t.GK_CREATE,
                                msg)

            return
        else:
            LOG.info("Service " + serv_id + ": VIM list ordered")
            self.services[serv_id]['service']['ordered_vim_list'] = vim_list

        self.start_next_task(serv_id)

    def update_slm_configuration(self, plugin_dict):
        """
        This method checks if an SLM was added or removed from the
        pool of SLMs. If it was, this method updates the configuration
        of the SLM.

        :param plugin_dict: Dictionary of plugins registered in plugin manager
        """

        active_slms = []

        # Substract information on the different SLMs from the dict
        for plugin_uuid in plugin_dict.keys():
            if plugin_dict[plugin_uuid]['name'] == self.name:
                active_slms.append(plugin_uuid)

        # Check if the list of active SLMs is identical to the known list
        active_slms.sort()
#        print('########')
#        print(active_slms)
#        print(self.known_slms)
        if active_slms == self.known_slms:
            # No action te be taken
            return
        else:
            if self.uuid is None:
                for slm_uuid in active_slms:
                    if slm_uuid not in self.known_slms:
                        self.uuid = slm_uuid
            self.slm_config['old_slm_rank'] = self.slm_config['slm_rank']
            self.slm_config['old_slm_total'] = self.slm_config['slm_total']
            self.slm_config['slm_rank'] = active_slms.index(str(self.uuid))
            self.slm_config['slm_total'] = len(active_slms)
            down = False
            if len(active_slms) < len(self.known_slms):
                down = True

            self.known_slms = active_slms
            # Buffer incoming requests
#            self.bufferAllRequests = True
            # Wait some time to allow different SLMs to get on the same pages
#            time.sleep(self.deltaTnew)
            # Start handling the buffered requests in the new regime
#            self.bufferOldRequests = True
#            self.bufferAllRequests = False

#            for req in self.new_reqs:
#                task = self.thrd_pool.submit(req['mthd'], req['arguments'])

#            time.sleep(self.deltaTold)
            # Start handling the buffered requests from the old regime
#            self.bufferOldRequests = False

#            for req in self.old_reqs:
#                task = self.thrd_pool.submit(req['mthd'], req['arguments'])

            if down:
                self.slm_down()

    def roll_back_instantiation(self, serv_id):
        """
        This method tries to roll back the instantiation workflow if an error
        occured. It will send messages to the SMR and the IA to remove deployed
        SSMs, FSMs and stacks. It will instruct the Repositories to delete the
        records.
        """

        # Kill the stack
        corr_id = str(uuid.uuid4())
        payload = json.dumps({'instance_uuid': serv_id})
        self.manoconn.notify(t.IA_REMOVE,
                             payload,
                             reply_to=t.IA_REMOVE,
                             correlation_id=corr_id)

        # Kill the SSMs and FSMs
        self.terminate_ssms(serv_id, require_resp=False)

        self.terminate_fsms(serv_id, require_resp=False)

        LOG.info("Instantiation aborted, cleanup completed")

        # TODO: Delete the records


def main():
    """
    Entry point to start plugin.
    :return:
    """
    # reduce messaging log level to have a nicer output for this plugin
    logging.getLogger("son-mano-base:messaging").setLevel(logging.INFO)
    logging.getLogger("son-mano-base:plugin").setLevel(logging.INFO)
#    logging.getLogger("amqp-storm").setLevel(logging.DEBUG)
    # create our service lifecycle manager
    slm = ServiceLifecycleManager()

if __name__ == '__main__':
    main()
