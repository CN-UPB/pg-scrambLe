import hashlib
import logging
from abc import abstractmethod
import json
import time

import requests

from . import CommonInterface

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('helper.py')
logging.getLogger("urllib3").setLevel(logging.INFO)


class SONATAClient(CommonInterface):
    def __init__(self, host, port=4002):
        self._host = host
        self._port = port
        self._base_path = 'http://{0}:{1}/'
        self._user_endpoint = '{0}'

    def auth(self, username, password, host=None):
        if host is None:
            base_path = "http://{0}".format(self._host)
        else:
            base_path = "http://{0}".format(host)

        _endpoint = '{0}/api/v2/sessions'.format(base_path)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json", "accept": "application/json"}
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
                base_path = "http://{0}:{1}".format(self._host, self._port)
            else:
                base_path = "http://{0}:{1}".format(host, port)

            query_path = ''
            if _filter:
                query_path = '?_admin.type=' + _filter

            _endpoint = "{0}/catalogues/api/v2/network-services".format(base_path, query_path)
            result = {'error': True, 'data': ''}
            headers = {"Content-Type": "application/json", 'Authorization': 'Bearer {}'.format(token)}

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
            base_path = "http://{0}:{1}".format(self._host, self._port)
        else:
            base_path = "http://{0}:{1}".format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/x-yaml", 'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/catalogues/api/v2/network-services".format(base_path)
        try:
            r = requests.post(_endpoint, data=open(package_path, 'rb'), verify=False, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        #print(result)
        return json.dumps(result)
        pass

    def get_ns_descriptors_nsd_content(self):
        """ NSD Management Interface - Upload NSD

              Upload the content of NSD
              """
        pass

    def put_ns_descriptors_nsd_content(self):
        """ NSD Management Interface - Upload NSD

        Upload the content of NSD
        """
        pass

    def delete_ns_descriptors(self, token, uuid, host=None, port=None):
        if host is None:
            base_path = "http://{0}:{1}".format(self._host, self._port)
        else:
            base_path = "http://{0}:{1}".format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/x-yaml", 'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/catalogues/api/v2/network-services".format(base_path, uuid)

        try:
            r = requests.delete(_endpoint, params=None, verify=False, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)



    def get_vnf_packages(self):
        """ VNF Package Management Interface - VNF packages

        /vnf_packages
            GET - Query VNF packages information

        """
        pass

    def post_vnf_packages(self):
        """ VNF Package Management Interface - VNF packages

        /vnf_packages
            POST - Create a new individual 
                    VNFpackage resource

        """
        pass

    def get_vnf_packages_vnfpkgid(self, vnfPkgId):
        """ VNF Package Management Interface - 
                Individual VNF package

        /vnf_packages/{vnfPkgId}
            GET - Read information about an 
                    individual VNF package
   
        """
        pass

    def patch_vnf_packages_vnfpkgid(self, vnfPkgId):
        """ VNF Package Management Interface - 
                Individual VNF package

        /vnf_packages/{vnfPkgId}
        PATCH - Update information about an
                    individual VNF package

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


    def delete_vnf_packages_vnfpkgid(self, vnfPkgId):
        """ VNF Package Management Interface - 
                Individual VNF package

        /vnf_packages/{vnfPkgId}
            DELETE - Delete an individual VNF package

        """
        pass

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




# if __name__ == "__main__":
#     sonata_c = SONATAClient("vm-hadik3r-08.cs.uni-paderborn.de")
#     _token = json.loads(sonata_c.auth(username="sonata", password="1234"))
#     _token = json.loads(_token["data"])
#     print(_token["token"]["access_token"])
#     print(sonata_c.get_ns_descriptors(token=_token["token"]["access_token"]))
#     _nid = json.loads(sonata_c.post_ns_descriptors(token=_token["token"]["access_token"], package_path="../samples/nsd_example.yml"))
#     _nid = json.loads(_nid["data"]["uuid"])
#     print(_nid["token"]["access_token"])
#    #time.sleep(10)
#    # print(sonata_c.delete_ns_descriptors(token=_token["token"]["access_token"], uuid=_nid["token"]["access_token"]))

#     # cd adaptor/wrappers
#     # python3 sonata.py
