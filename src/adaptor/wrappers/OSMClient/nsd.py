from ..CommonInterface import CommonInterfaceNsd
from .helpers import Helpers
import json
import requests

class Nsd(CommonInterfaceNsd):

    def __init__(self, host, port=9999):
        self._host = host
        self._port = port
        self._base_path = 'https://{0}:{1}/osm'
        self._user_endpoint = '{0}/admin/v1/users'

    def get_ns_descriptors(self, token, _filter=None, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        query_path = ''
        if _filter:
            query_path = '?_admin.type=' + _filter

        _endpoint = "{0}/nsd/v1/ns_descriptors_content{1}".format(base_path, query_path)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token)}

        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result

        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def post_ns_descriptors(self, token, package_path, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/gzip", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token),
                   'Content-File-MD5': Helpers.md5(open(package_path, 'rb'))}
        _endpoint = "{0}/nsd/v1/ns_descriptors_content/".format(base_path)
        try:
            r = requests.post(_endpoint, data=open(package_path, 'rb'), verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def get_ns_descriptors_nsdinfoid(self, token, id, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
        _endpoint = "{0}/nsd/v1/ns_descriptors/{1}/nsd".format(base_path, id)
        result = {'error': True, 'data': ''}
        headers = {'Content-Type': 'application/yaml',
                    'Authorization': 'Bearer {}'.format(token)}  
        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
            
        result['data'] = r.text
        return json.dumps(result)

    def patch_ns_descriptors_nsdinfoid(self):
        """ NSD Management Interface - Individual NS Descriptor

        /ns_descriptors/{nsdInfoId}
            PATCH - Modify the operational state and/or 
                the user defined data of an individual
                NS descriptor resource.
        """
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def delete_ns_descriptors_nsdinfoid(self, token, id, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token)}

        _endpoint = "{0}/nsd/v1/ns_descriptors_content/{1}".format(base_path, id)

        try:
            r = requests.delete(_endpoint, params=None, verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)
    
    def get_ns_descriptors_nsd_content(self, token, id ,host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"accept": "application/zip",
                    'Authorization': 'Bearer {}'.format(token)}

        _endpoint = "{0}/nsd/v1/ns_descriptors/{1}/nsd_content".format(base_path, id)
        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def put_ns_descriptors_nsd_content(self, token, data_path, id, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/gzip", "accept": "application/json",
                        'Authorization': 'Bearer {}'.format(token),
                        'Content-File-MD5': Helpers.md5(open(data_path, 'rb'))}

        _endpoint = "{0}/nsd/v1/ns_descriptors/{1}/nsd_content".format(base_path, id)

        try:
            r = requests.put(_endpoint, data=open(data_path, 'rb'), verify=False,
                                headers=headers)
        except Exception as e:
                result['data'] = str(e)
                return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def get_pnf_descriptors(self):
        """ NSD Management interface -
                PNF Descriptors

        /pnf_descriptors
            GET - Query information about multiple
                PNF descriptor resources.

        """
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def post_pnf_descriptors(self):
        """ NSD Management interface -
                PNF Descriptors

        /pnf_descriptors
            POST - Create a new PNF descriptor resource.

        """
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
 
    def get_pnf_descriptors_pnfdinfoid(self, pnfdInfoId):
        """ NSD Management interface -
                Individual PNF Descriptor

        /pnf_descriptors/pnfdinfoid
            GET - Read an individual PNFD resource.

        """
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
 
    def patch_pnf_descriptors_pnfdinfoid(self, pnfdInfoId):
        """ NSD Management interface -
                Individual PNF Descriptor

        /pnf_descriptors/pnfdinfoid
            PATCH - Modify the user defined data of an 
                        individual PNF descriptor resource.

        """
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
    
    def delete_pnf_descriptors_pnfdinfoid(self, pnfdInfoId):
        """ NSD Management interface -
                Individual PNF Descriptor

        /pnf_descriptors/pnfdinfoid
            DELETE - Delete an individual PNF descriptor resource.

        """
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def get_pnf_descriptors_pnfd_content(self, pnfdInfoId):
        """ NSD Management interface -
                PNFD Content

        /pnf_descriptors/pnfdinfoid/pnfd_content
            GET - Fetch the content of a PNFD.

        """
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def put_pnf_descriptors_pnfd_content(self, pnfdInfoId):
        """ NSD Management interface -
                PNFD Content

        /pnf_descriptors/pnfdinfoid/pnfd_content
            PUT - Upload the content of a PNFD.

        """
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def post_subscriptions(self, pnfdInfoId):
        """ NSD Management interface -
                Subscriptions

        /subscriptions
            POST - Subscribe to NSD and PNFD change notifications.

        """
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def get_subscriptions(self, subscriptionId):
        """ NSD Management interface -
                Subscriptions

        /subscriptions
            GET - Query multiple subscriptions.

        """
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
  
    def get_subscriptions_subscriptionid(self, subscriptionid):
        """ NSD Management interface -
                Individual Subscription

        /subscriptions/subscriptionId
            GET - Read an individual subscription resource

        """
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def delete_subscriptions_subscriptionid(self, subscriptionid):
        """ NSD Management interface -
                Individual Subscription

        /subscriptions/subscriptionId
            DELETE - Terminate a subscription.

        """
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)