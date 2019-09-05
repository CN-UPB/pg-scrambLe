from ..CommonInterface import CommonInterfaceDatabase
import json
import requests

class Database(CommonInterfaceDatabase):
    """
    Database calls management
    """

    def __init__(self, host, port=7001):
        self._host = host
        self._port = port
        self._base_path = 'http://{0}:{1}'
        
		
    def get_mano_list(self, host=None, port=None):
	
	    if host is None:
		    base_path = "http://{0}:{1}".format(self._host, self._port)
	    else:
		    base_path = "http://{0}:{1}".format(host, port)
	
	    _endpoint = "{0}/mano".format(base_path)
	    result = {'error': True, 'data': ''}
		
	    try:
		    r = requests.get(_endpoint, params=None, verify=False, stream=True)
	    except Exception as e:
		    result['data'] = str(e)
		    return result

	    if r.status_code == requests.codes.ok:
		    result['error'] = False

	    result['data'] = r.text
	    return json.dumps(result)
			
			
    def post_mano_create(self, host=None, port=None):
	
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
			
        _endpoint = "{0}/mano_create".format(base_path)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        data = {"name": "manoname", "type": "manotype", "user": "username", "pwd": "password", "ip": "ipaddress"}
        
        try:
            r = requests.post(_endpoint, json=data, verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

		
  
	
    def post_mano_remove(self, host=None, port=None):
	
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
			
        _endpoint = "{0}/mano/remove".format(base_path)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        data = {"_id": "manoid"}
        
        try:
            r = requests.post(_endpoint, json=data, verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)
	