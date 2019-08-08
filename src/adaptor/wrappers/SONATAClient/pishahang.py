import json
import requests

class Pishahang():
    """
    Pishahang Related Interfaces
    """
    
    def __init__(self, host, port=4002, requests_port=32001):
        self._host = host
        self._port = port
        self._requests_port = requests_port
        self._base_path = 'http://{0}:{1}'
        self._user_endpoint = '{0}'

    def get_csd_descriptors(self, token, offset=None, limit=None, host=None, port=None):
        """ CSD Package Management Interface - Cloud descriptors

        :param token: auth token retrieved by the auth call
        :param offset: offset index while returning
        :param limit: limit records while returning
        :param host: host url
        :param port: port where the MANO API can be accessed

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        if not offset:
            offset = 0
        if not limit:
            limit = 10

        _endpoint = "{0}/catalogues/api/v2/csds?offset={1}&limit={2}".format(base_path, offset, limit)

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

    def post_csd_descriptors(self, token, package_path, host=None, port=None):
        """ CSD Package Management Interface - Cloud descriptors

        /vnf_descriptors:
            POST - Create a new individual 
            VNFpackage resource

        :param token: auth token retrieved by the auth call
        :param package_path: file path of the package
        :param host: host url
        :param port: port where the MANO API can be accessed

        Example:
            .. code-block:: python

                sonata_pishahang = SONATAClient.Pishahang(HOST_URL)
                sonata_auth = SONATAClient.Auth(HOST_URL)

                _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])

                response = json.loads(sonata_pishahang.post_csd_descriptors(
                                        token=_token["token"]["access_token"],
                                        package_path="tests/samples/csd_example.yml"))

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/x-yaml", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/catalogues/api/v2/csds".format(base_path)
        try:
            r = requests.post(_endpoint, data=open(package_path, 'rb'), verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def get_cosd_descriptors(self, token, offset=None, limit=None, host=None, port=None):
        """ COSD Package Management Interface - Cloud descriptors

        :param token: auth token retrieved by the auth call
        :param offset: offset index while returning
        :param limit: limit records while returning
        :param host: host url
        :param port: port where the MANO API can be accessed

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        if not offset:
            offset = 0
        if not limit:
            limit = 10

        _endpoint = "{0}/catalogues/api/v2/complex-services?offset={1}&limit={2}".format(base_path, offset, limit)

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

    def post_cosd_descriptors(self, token, package_path, host=None, port=None):
        """ COSD Package Management Interface - Cloud descriptors

        /vnf_descriptors:
            POST - Create a new individual 
            VNFpackage resource

        :param token: auth token retrieved by the auth call
        :param package_path: file path of the package
        :param host: host url
        :param port: port where the MANO API can be accessed

        Example:
            .. code-block:: python

                sonata_pishahang = SONATAClient.Pishahang(HOST_URL)
                sonata_auth = SONATAClient.Auth(HOST_URL)

                _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])

                response = json.loads(sonata_pishahang.post_cosd_descriptors(
                                        token=_token["token"]["access_token"],
                                        package_path="tests/samples/csd_example.yml"))

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/x-yaml", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/catalogues/api/v2/complex-services".format(base_path)
        try:
            r = requests.post(_endpoint, data=open(package_path, 'rb'), verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def post_cs_instances_nsinstanceid_instantiate(self, token, nsInstanceId, egresses=[], ingresses=[], host=None, port=None):
        """  NS (CS) Lifecycle Management Interface - 
        Instantiate CS task

        :param token: auth token retrieved by the auth call
        :param nsInstanceId: NS instaniation description
        :param ingresses: ingresses list
        :param egresses: egresses list 
        :param host: host url
        :param port: port where the MANO API can be accessed

        Example:
            .. code-block:: python

                sonata_pishahang = SONATAClient.Pishahang(HOST_URL)
                sonata_auth = SONATAClient.Auth(HOST_URL)

                _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])

                _cosd_list = json.loads(sonata_pishahang.get_cosd_descriptors(token=_token["token"]["access_token"]))
                _cosd_list = json.loads(_cosd_list["data"])

                _ns = None
                for _n in _cosd_list:
                    if "A dummy Example." == _n['nsd']['description']:            
                        _ns = _n['uuid']

                if _ns:
                    response = json.loads(
                                sonata_pishahang.post_cs_instances_nsinstanceid_instantiate(
                                    token=_token["token"]["access_token"], nsInstanceId=_ns))

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._requests_port)
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
        _endpoint = "{0}/api/v2/requests".format(base_path)

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

    def post_cs_instances_nsinstanceid_terminate(self, token, nsInstanceId, host=None, port=None):
        """  NS (CS) Lifecycle Management Interface - 
        Terminate CS task

        :param token: auth token retrieved by the auth call
        :param nsInstanceId: id of the NS instance        
        :param host: host url
        :param port: port where the MANO API can be accessed
        :param force: true/false whether to force terminate 
        
        """
        if host is None:
            base_path = self._base_path.format(self._host, self._requests_port)
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

        _endpoint = "{0}/api/v2/requests".format(base_path)

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
    
    def delete_cosd_descriptors_cosdpkgid(self, token, cosdpkgid, host=None, port=None):
        """ COSD Management Interface - Individual COSD Descriptor

        :param token: auth token retrieved by the auth call
        :param cosdpkgid: id of the individual NSD
        :param host: host url
        :param port: port where the MANO API can be accessed

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/x-yaml", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/catalogues/api/v2/complex-services/{1}".format(base_path, cosdpkgid)
        
        try:
            r = requests.delete(_endpoint, params=None, verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        result['data'] = r.text        
        return json.dumps(result)        

    def delete_csd_descriptors_csdpkgid(self, token, csdpkgid, host=None, port=None):
        """ CSD Package Management Interface - 
        Individual CSD package

        :param token: auth token retrieved by the auth call
        :param csdpkgid: id of the vnf package to fetch
        :param host: host url
        :param port: port where the MANO API can be accessed

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/x-yaml", 'Authorization': 'Bearer {}'.format(token)}

        _endpoint = "{0}/catalogues/api/v2/csds/{1}".format(base_path, csdpkgid)

        try:
            r = requests.delete(_endpoint, params=None, verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)
