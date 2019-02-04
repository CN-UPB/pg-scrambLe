import hashlib
import logging
from abc import abstractmethod
import json
import yaml
import time
import requests
from . import CommonInterface

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('helper.py')
logging.getLogger("urllib3").setLevel(logging.INFO)


class OSMClient(CommonInterface):
    def __init__(self, host, port=9999):
        self._host = host
        self._port = port
        self._base_path = 'https://{0}:{1}/osm'
        self._user_endpoint = '{0}/admin/v1/users'

    def auth(self, username, password, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        _endpoint = '{0}/admin/v1/tokens'.format(base_path)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json"}
        data = {"username": username, "password": password}

        try:
            # TODO: make verify=false as a fallback
            r = requests.post(_endpoint, headers=headers,  json=data, verify=False)
        except Exception as e:
            log.exception(e)
            result["data"] = str(e)
            return result

        if r.status_code == requests.codes.ok:
            result['error'] = False

        result["data"] = r.text
        return json.dumps(result)

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
                log.exception(e)
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
                   'Content-File-MD5': self.md5(open(package_path, 'rb'))}
        _endpoint = "{0}/nsd/v1/ns_descriptors_content/".format(base_path)
        try:
            r = requests.post(_endpoint, data=open(package_path, 'rb'), verify=False, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)
        pass

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
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token)}

        _endpoint = "{0}/nsd/v1/ns_descriptors_content/{1}".format(base_path, id)

        try:
            r = requests.delete(_endpoint, params=None, verify=False, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

        ###################################
        # VNF Package Management Interfaces

        # Base: {apiRoot}/vnfpkgm/v1
        ###################################

    
    def get_vnf_packages(self, token, _filter=None, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        query_path = ''
        if _filter:
            query_path = '?_admin.type='+_filter

        _endpoint = "{0}/vnfpkgm/v1/vnf_packages_content{1}".format(base_path, query_path)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token)}

        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
        
        result['data'] = r.text
        return json.dumps(result)


  
    def post_vnf_packages(self, token, package_path, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/gzip", "accept": "application/json",
                     'Authorization': 'Bearer {}'.format(token),
                     'Content-File-MD5': self.md5(open(package_path, 'rb'))}
        _endpoint = "{0}/vnfpkgm/v1/vnf_packages_content".format(base_path)
        try:
            r = requests.post(_endpoint, data=open(package_path, 'rb'), verify=False, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)
        


    def get_vnf_packages_vnfpkgid(self, token, id, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {'Content-Type': 'application/yaml',
                        'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/vnfpkgm/v1/vnf_packages/{1}/vnfd".format(base_path, id)
        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    
    def patch_vnf_packages_vnfpkgid(self, vnfPkgId):
        """ VNF Package Management Interface - 
                Individual VNF package

        /vnf_packages/{vnfPkgId}
        PATCH - Update information about an
                    individual VNF package

        """
        pass

    
    def delete_vnf_packages_vnfpkgid(self, token, id, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token)}

        _endpoint = "{0}/vnfpkgm/v1/vnf_packages_content/{1}".format(base_path, id)

        try:
            r = requests.delete(_endpoint, params=None, verify=False, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)
       

 
    def get_vnf_packages_vnfpkgid_vnfd(self, vnfPkgId):
        """ VNF Package Management Interface - 
                VNFD of an individual VNF package

        /vnf_packages/{vnfPkgId}/vnfd
            GET - Read VNFD of an on-boarded VNF package
   
        """
        pass

   
    def get_vnf_packages_vnfpkgid_package_content(self, vnfPkgId):
        """ VNF Package Management Interface - 
                VNF package content

        /vnf_packages/{vnfPkgId}/package_content
            GET - Fetch an on-boarded VNF package
   
        """
        pass

    
    def put_vnf_packages_vnfpkgid_package_content(self, vnfPkgId):
        """ VNF Package Management Interface - 
                VNF package content

        /vnf_packages/{vnfPkgId}/package_content
            PUT - Upload a VNF package by providing 
                    the content of the VNF package
   
        """
        pass

    
    def post_vnf_packages_vnfpkgid_package_content(self, vnfPkgId):
        """ VNF Package Management Interface - 
                Upload VNF package from URI task

        /vnf_packages/{vnfPkgId}/package_content/upload_from_uri
            POST - Upload a VNF package by providing
                    the address information of the VNF package
   
        """
        pass

    
    def get_vnf_packages_vnfpkgid_artifacts_artifactpath(self, 
            vnfPkgId, artifactPath):
        """ VNF Package Management Interface - 
                Individual VNF package artifact

        /vnf_packages/{vnfPkgId}/artifacts/{artifactPath}
            GET - Fetch individual VNF package artifact
   
        """
        pass

    
    def get_vnf_packages_subscriptions(self):
        """ VNF Package Management Interface - 
                Subscriptions

        /subscriptions
            GET - Query multiple subscriptions
   
        """
        pass

  
    def post_vnf_packages_subscriptions(self):
        """ VNF Package Management Interface - 
                Subscriptions

        /subscriptions
            POST - Subscribe to notifications related
                to on-boarding and/or changes of VNF packages
   
        """
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

    
    def delete_pnf_descriptors_pnfdinfoid(self, pnfdInfoId):
        """ NSD Management interface -
                Individual PNF Descriptor

        /pnf_descriptors/pnfdinfoid
            DELETE - Delete an individual PNF descriptor resource.

        """
        pass


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



    @staticmethod
    def md5(filename):
        hash_md5 = hashlib.md5()
        for chunk in iter(lambda: filename.read(1024), b""):
            hash_md5.update(chunk)
        return hash_md5.hexdigest()

