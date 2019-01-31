# Implement common_interfaces here

import hashlib
import logging
from abc import abstractmethod
import json
import time

import requests

import common_interface

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('helper.py')
logging.getLogger("urllib3").setLevel(logging.INFO)


class SONATAClient(common_interface.CommonInterface):
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


if __name__ == "__main__":
    sonata_c = SONATAClient("vm-hadik3r-08.cs.uni-paderborn.de")
    _token = json.loads(sonata_c.auth(username="sonata", password="1234"))
    _token = json.loads(_token["data"])
    print(_token["token"]["access_token"])
    print(sonata_c.get_ns_descriptors(token=_token["token"]["access_token"]))
    _nid = json.loads(sonata_c.post_ns_descriptors(token=_token["token"]["access_token"], package_path="../samples/nsd_example.yml"))
    _nid = json.loads(_nid["data"]["uuid"])
    print(_nid["token"]["access_token"])
   #time.sleep(10)
   # print(sonata_c.delete_ns_descriptors(token=_token["token"]["access_token"], uuid=_nid["token"]["access_token"]))

    # cd adaptor/wrappers
    # python3 sonata.py
