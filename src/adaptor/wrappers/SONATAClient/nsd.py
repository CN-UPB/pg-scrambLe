from ..CommonInterface import CommonInterfaceNsd
import json
import yaml
import requests


class Nsd(CommonInterfaceNsd):

    def __init__(self, host, port=4002):
        self._host = host
        self._port = port
        self._base_path = 'http://{0}:{1}'
        self._user_endpoint = '{0}'


    def get_ns_descriptors(self, token, _filter=None, host=None, port=None):
            if host is None:
                base_path = "http://{0}:{1}".format(self._host, self._port)
            else:
                base_path = "http://{0}:{1}".format(host, port)

            query_path = ''
            if _filter:
                query_path = '?_admin.type=' + _filter

            _endpoint = "{0}/catalogues/api/v2/network-services{1}".format(base_path, query_path)
            result = {'error': True, 'data': ''}
            headers = {"Content-Type": "application/json", 'Authorization': 'Bearer {}'.format(token)}

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
        headers = {"Content-Type": "application/x-yaml", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/catalogues/api/v2/network-services".format(base_path)
        try:
            r = requests.post(_endpoint, data=open(package_path, 'rb'), verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)
        

    def get_ns_descriptors_nsd_content(self):
        """ NSD Management Interface - Upload NSD

              Upload the content of NSD
              """
        pass

    def patch_ns_descriptors_nsd_content(self):
        """ NSD Management Interface - Individual NS Descriptor

        /ns_descriptors/{nsdInfoId}
            PATCH - Modify the operational state and/or 
                the user defined data of an individual
                NS descriptor resource.
        """
        pass

    def put_ns_descriptors_nsd_content(self):
        """ NSD Management Interface - Upload NSD

        Upload the content of NSD
        """
        pass

    def delete_ns_descriptors(self, token, id, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/x-yaml", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/catalogues/api/v2/network-services/{1}".format(base_path, id)
        
        try:
            r = requests.delete(_endpoint, params=None, verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        result['data'] = r.text
        print(r.text)
        
        return json.dumps(result)

        

    def get_ns_descriptors_nsdinfoid(self, token, _filter=None, host=None, port=None):
        if host is None:
                base_path = "http://{0}:{1}".format(self._host, self._port)
        else:
                base_path = "http://{0}:{1}".format(host, port)
           
        _endpoint = "{0}/catalogues/api/v2/network-services{1}".format(base_path, query_path)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json", 'Authorization': 'Bearer {}'.format(token)}

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
        pass


    def get_pnf_descriptors(self):
        """ NSD Management interface -
                PNF Descriptors

        /pnf_descriptors
            GET - Query information about multiple
                PNF descriptor resources.

        """
        pass

   
    def post_pnf_descriptors(self):
        """ NSD Management interface -
                PNF Descriptors

        /pnf_descriptors
            POST - Create a new PNF descriptor resource.

        """
        pass

 
    def get_pnf_descriptors_pnfdinfoid(self, pnfdInfoId):
        """ NSD Management interface -
                Individual PNF Descriptor

        /pnf_descriptors/pnfdinfoid
            GET - Read an individual PNFD resource.

        """
        pass

 
    def patch_pnf_descriptors_pnfdinfoid(self, pnfdInfoId):
        """ NSD Management interface -
                Individual PNF Descriptor

        /pnf_descriptors/pnfdinfoid
            PATCH - Modify the user defined data of an 
                        individual PNF descriptor resource.

        """
        pass

    
    def delete_pnf_descriptors_pnfdinfoid(self, token, id, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/x-yaml", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/catalogues/api/v2/network-services/{1}".format(base_path, id)
        
        try:
            r = requests.delete(_endpoint, params=None, verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)


    def get_pnf_descriptors_pnfd_content(self, pnfdInfoId):
        """ NSD Management interface -
                PNFD Content

        /pnf_descriptors/pnfdinfoid/pnfd_content
            GET - Fetch the content of a PNFD.

        """
        pass


    def put_pnf_descriptors_pnfd_content(self, pnfdInfoId):
        """ NSD Management interface -
                PNFD Content

        /pnf_descriptors/pnfdinfoid/pnfd_content
            PUT - Upload the content of a PNFD.

        """
        pass


    def post_subscriptions(self, pnfdInfoId):
        """ NSD Management interface -
                Subscriptions

        /subscriptions
            POST - Subscribe to NSD and PNFD change notifications.

        """
        pass


    def get_subscriptions(self, subscriptionId):
        """ NSD Management interface -
                Subscriptions

        /subscriptions
            GET - Query multiple subscriptions.

        """
        pass

  
    def get_subscriptions_subscriptionid(self, subscriptionid):
        """ NSD Management interface -
                Individual Subscription

        /subscriptions/subscriptionId
            GET - Read an individual subscription resource

        """
        pass


    def delete_subscriptions_subscriptionid(self, subscriptionid):
        """ NSD Management interface -
                Individual Subscription

        /subscriptions/subscriptionId
            DELETE - Terminate a subscription.

        """
        pass