from ..CommonInterface import CommonInterfaceNslcm
# from .helpers import Helpers
import json
import requests
# import tarfile

class Nslcm(CommonInterfaceNslcm):

    def __init__(self, host, port=32001):
        self._host = host
        self._port = port
        self._base_path = 'http://{0}:{1}/api/v2'
        
    def get_ns_instances(self, token, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
        
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", 
                    "accept": "application/json" ,
                    "Authorization": 'Bearer {}'.format(token)}
        _endpoint = "{0}/records/services".format(base_path)
        
        try:
            r = requests.get(_endpoint, params=None, verify=False, 
                                headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result

        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)   

    def get_ns_instances_nsinstanceid(self, token, nsInstanceId ,host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json",
                    "accept": "application/json",
                    "Authorization": 'Bearer {}'.format(token)}
        _endpoint = "{0}/records/services/{1}".format(base_path, nsInstanceId)

        try:
            r = requests.get(_endpoint, params=None, verify=False,
                                headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

   
    def post_ns_instances_nsinstanceid_instantiate(self, token, nsInstanceId, egresses=[], ingresses=[], host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
        result = {'error': True, 'data': ''}
        headers = {
                "Content-Type": "application/json",
                "accept": "application/json",
                "Authorization": 'Bearer {}'.format(token)}
        data = {
                "service_uuid": nsInstanceId,
                "egresses" : egresses,
                "ingresses" : ingresses
        }
        _endpoint = "{0}/requests".format(base_path)

        try:
            r = requests.post(_endpoint, params=None, verify=False,
                                headers=headers, json=data)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def post_ns_instances_nsinstanceid_terminate(self, token, nsInstanceId, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
        result = {'error': True, 'data': ''}
        headers = {
                "Content-Type": "application/json",
                "accept": "application/json",
                "Authorization": 'Bearer {}'.format(token)}

        data = {
                "service_instance_uuid": nsInstanceId,
                "request_type": "TERMINATE"
        }

        _endpoint = "{0}/requests".format(base_path)

        try:
            r = requests.post(_endpoint, params=None, verify=False,
                                headers=headers, json=data)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def post_ns_instances_nsinstanceid_scale(self, nsInstanceId):
        """  NS Lifecycle Management interface - 
                Scale NS task

        /ns_instances_nsinstanceid_scale
            POST - Scale a NS instance.

        """
        pass
   
    def post_ns_instances_nsinstanceid_update(self, nsInstanceId):
        """  NS Lifecycle Management interface - 
                Update NS task

        /ns_instances_nsinstanceid_update
            POST - Updates a NS instance.

        """
        pass
    
    def post_ns_instances_nsinstanceid_heal(self, nsInstanceId):
        """  NS Lifecycle Management interface - 
                Heal NS task

        /ns_instances_nsinstanceid_heal
            POST - Heal a NS instance.

        """
        pass
        
    def post_ns_lcm_op_occs_nslcmopoccid_retry(self, nsLcmOpOccId):
        """  NS Lifecycle Management interface - 
                Retry operation task

        /ns_lcm_op_occs_nslcmopoccid_retry
            POST - Retry a NS lifecycle management operation occurrence.

        """
        pass
    
    def post_ns_lcm_op_occs_nslcmopoccid_rollback(self, nsLcmOpOccId):
        """  NS Lifecycle Management interface - 
                Rollback operation task

        /ns_lcm_op_occs_nslcmopoccid_rollback
            POST - Rollback a NS lifecycle management operation occurrence.

        """
        pass
  
    def post_ns_lcm_op_occs_nslcmopoccid_continue(self, nsLcmOpOccId):
        """  NS Lifecycle Management interface - 
                Continue operation task

        /ns_lcm_op_occs_nslcmopoccid_continue
            POST - Continue a NS lifecycle management operation occurrence.

        """
        pass
   
    def post_ns_lcm_op_occs_nslcmopoccid_fail(self, nsLcmOpOccId):
        """  NS Lifecycle Management interface - 
                Fail operation task

        /ns_lcm_op_occs_nslcmopoccid_fail
            POST - Mark a NS lifecycle management operation occurrence as failed.

        """
        pass
   
    def post_ns_lcm_op_occs_nslcmopoccid_cancel(self, nsLcmOpOccId):
        """  NS Lifecycle Management interface - 
                Cancel operation task

        /ns_lcm_op_occs_nslcmopoccid_cancel
            POST - Cancel a NS lifecycle management operation occurrence.

        """
        pass
 
    def post_ns_lcm_subscriptions(self):
        """  NS Lifecycle Management interface - 
                Subscriptions

        /ns_lcm_subscriptions
            POST - Subscribe to NS lifecycle change notifications.

        """
        pass
    
    def get_ns_lcm_subscriptions(self):
        """  NS Lifecycle Management interface - 
                Subscriptions

        /ns_lcm_subscriptions
            GET - Query multiple subscriptions.

        """
        pass

    def delete_ns_instances_nsinstanceid(self):
        pass

    def get_ns_lcm_op_ops(self):
        pass

    def get_ns_lcm_op_ops_nslcmopoccid(self):
        pass

    def post_ns_instances(self):
        pass
    
    def get_ns_lcm_subscriptions_subscriptionid(self, subscriptionId):
        """  NS Lifecycle Management interface - 
                Individual subscription

        /ns_lcm_subscriptions_subscriptionid
            GET - Read an individual subscription resource.

        """
        pass
   
    def delete_ns_lcm_subscriptions_subscriptionid(self, subscriptionId):
        """  NS Lifecycle Management interface - 
                Individual subscription

        /ns_lcm_subscriptions_subscriptionid
            DELETE - Terminate a subscription.

        """
        pass


    
    