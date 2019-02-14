from ..CommonInterface import CommonInterfaceVnfPkgm
from .helpers import Helpers
import json
import requests
import tarfile

class VnfPkgm(CommonInterfaceVnfPkgm):
    
    def __init__(self, host, port=9999):
        self._host = host
        self._port = port
        self._base_path = 'https://{0}:{1}/osm'
        self._user_endpoint = '{0}/admin/v1/users'

    def get_vnf_packages(self, token, _filter=None, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        query_path = ''
        if _filter:
            query_path = '?_admin.type='+_filter

        _endpoint = "{0}/vnfpkgm/v1/vnf_packages_content".format(base_path, query_path)
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
  
    def post_vnf_packages(self, token, package_path, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/gzip", "accept": "application/json",
                     'Authorization': 'Bearer {}'.format(token),
                     'Content-File-MD5': Helpers.md5(open(package_path, 'rb'))}
        _endpoint = "{0}/vnfpkgm/v1/vnf_packages_content".format(base_path)
        try:
            r = requests.post(_endpoint, data=open(package_path, 'rb'), verify=False, headers=headers)
        except Exception as e:
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
        _endpoint = "{0}/vnfpkgm/v1/vnf_packages_content/{1}".format(base_path, id)
        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
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
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
    
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
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)       
 
    def get_vnf_packages_vnfpkgid_vnfd(self, token, id , host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        _endpoint = "{0}/vnfpkgm/v1/vnf_packages/{1}/vnfd".format(base_path, id)
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

    def get_vnf_packages_vnfpkgid_package_content(self, token, id ,host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"accept": "application/zip",
                'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/vnfpkgm/v1/vnf_packages/{1}/package_content".format(base_path, id)
        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)
    
    def put_vnf_packages_vnfpkgid_package_content(self, token, data_path, id, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        
        headers = {"Content-Type": "application/gzip", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token),
                    'Content-File-MD5': Helpers.md5(open(data_path, 'rb'))}

        _endpoint = "{0}/vnfpkgm/v1/vnf_packages/{1}/package_content".format(base_path, id)
        
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
        
    def post_vnf_packages_vnfpkgid_package_content(self, vnfPkgId):
        """ VNF Package Management Interface - 
                Upload VNF package from URI task

        /vnf_packages/{vnfPkgId}/package_content/upload_from_uri
            POST - Upload a VNF package by providing
                    the address information of the VNF package
   
        """
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
    
    def get_vnf_packages_vnfpkgid_artifacts_artifactpath(self, token, id , host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        _endpoint = "{0}/vnfpkgm/v1/vnf_packages/{1}/artifacts".format(base_path, id)
        result = {'error': True, 'data': ''}
        headers = {'Content-Type': 'application/yaml', 'accept': 'text/plain',
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

    
    def get_vnf_packages_subscriptions(self):
        """ VNF Package Management Interface - 
                Subscriptions

        /subscriptions
            GET - Query multiple subscriptions
   
        """
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
  
    def post_vnf_packages_subscriptions(self):
        """ VNF Package Management Interface - 
                Subscriptions

        /subscriptions
            POST - Subscribe to notifications related
                to on-boarding and/or changes of VNF packages
   
        """
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
