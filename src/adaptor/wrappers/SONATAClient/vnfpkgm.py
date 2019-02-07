from ..CommonInterface import CommonInterfaceVnfPkgm
import json
import yaml
import requests


class VnfPkgm(CommonInterfaceVnfPkgm):
    
    def __init__(self, host, port=4002):
        self._host = host
        self._port = port
        self._base_path = 'http://{0}:{1}'
        self._user_endpoint = '{0}'

    def get_vnf_packages(self, token, _filter=None, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        query_path = ''
        if _filter:
            query_path = '?_admin.type='+_filter

        _endpoint = "{0}/catalogues/api/v2/vnfs{1}".format(base_path,query_path)
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
        

    def post_vnf_packages(self, token, package_path, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/x-yaml", 'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/catalogues/api/v2/vnfs".format(base_path)
        try:
            r = requests.post(_endpoint, data=open(package_path, 'rb'), verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return yaml.dump(result)

    def get_vnf_packages_vnfpkgid(self, token, id, host=None, port=None):
        pass
        # if host is None:
        #     base_path = self._base_path.format(self._host, self._port)
        # else:
        #     base_path = self._base_path.format(host, port)

        # result = {'error': True, 'data': ''}
        # headers = {'Content-Type': 'application/x-yaml', 'Authorization': 'Bearer {}'.format(token)}
        # _endpoint = "{0}/vnfpkgm/v1/vnf_packages/{1}/vnfd".format(base_path, id)
        # try:
        #     r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        # except Exception as e:
        #     result['data'] = str(e)
        #     return result
        # if r.status_code == requests.codes.ok:
        #     result['error'] = False

        # result['data'] = r.text
        # return json.dumps(result)

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
        headers = {"Content-Type": "application/x-yaml", 'Authorization': 'Bearer {}'.format(token)}

        _endpoint = "{0}/catalogues/api/v2/vnfs{1}".format(base_path, id)

        try:
            r = requests.delete(_endpoint, params=None, verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        result['data'] = r.text
        return yaml.dump(result)

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