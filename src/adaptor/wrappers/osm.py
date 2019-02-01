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

    @staticmethod
    def md5(filename):
        hash_md5 = hashlib.md5()
        for chunk in iter(lambda: filename.read(1024), b""):
            hash_md5.update(chunk)
        return hash_md5.hexdigest()


# if __name__ == "__main__":
#     osm_c = OSMClient("vm-hadik3r-05.cs.uni-paderborn.de")
#     _token = json.loads(osm_c.auth(username="admin", password="admin"))
#     _token = json.loads(_token["data"])
#     print(_token["id"])
#     print(osm_c.get_ns_descriptors(token=_token["id"]))
#     _nid = json.loads(osm_c.post_ns_descriptors(token=_token["id"], package_path="../samples/cirros_2vnf_ns.tar.gz"))
#     _nid = json.loads(_nid["data"])
#     print(_nid["id"])
    # time.sleep(10)
    # print(osm_c.delete_ns_descriptors(token=_token["id"], id=_nid["id"]))

    # cd adaptor/wrappers
    # python3 osm.py
