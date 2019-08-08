# CPU array
# http://vm-hadik3r-06.cs.uni-paderborn.de:19999/api/v1/data?chart=system.cpu&format=array&points=5&after=-60
# http://vm-hadik3r-06.cs.uni-paderborn.de:19999/api/v1/data?chart=system.cpu&format=json&points=5&after=-60&options=jsonwrap

# Mem array
# http://vm-hadik3r-06.cs.uni-paderborn.de:19999/api/v1/data?chart=system.ram&format=json&points=5&after=-60&options=jsonwrap|percentage

# Load array
# http://vm-hadik3r-06.cs.uni-paderborn.de:19999/api/v1/data?chart=system.load&format=json&points=5&after=-60&options=jsonwrap

# Docker command
# docker run -d --name=netdata   -p 19999:19999   -v /proc:/host/proc:ro   -v /sys:/host/sys:ro   -v /var/run/docker.sock:/var/run/docker.sock:ro   --cap-add SYS_PTRACE   --security-opt apparmor=unconfined   netdata/netdata

# VM list
# http://vm-hadik3r-05.cs.uni-paderborn.de:19999 - Pishahang
# http://vm-hadik3r-06.cs.uni-paderborn.de:19999 - Pishahang scaling
# http://vm-hadik3r-07.cs.uni-paderborn.de:19999 - OSM

import requests
import json

def _getLoad(username=None, password=None, host=None, port=None, usehttps=False, num_points=5):
    """ netdata system Load API
    GET method which returns an an array of Load [1min, 5min, 15min]


    :param username: username for login
    :param password: password for login
    :param host: host url
    :param port: port where the netdata API can be accessed
    :usehttps: https or http
    :num_points: data points to fetch from netdata

    Example:

    """
    if usehttps:
        base_path = 'https://{0}:{1}'.format(host, port)
    else:
        base_path = 'http://{0}:{1}'.format(host, port)

    _endpoint = '{0}/api/v1/data?chart=system.load&format=json&points={1}&after=-60&options=jsonwrap'.format(base_path, num_points)

    # headers = {"Content-Type": "application/yaml", "accept": "application/json"}
    # data = {"username": username, "password": password}

    try:
        r = requests.get(_endpoint)

        if r.status_code != requests.codes.ok:
            return False

        response = json.loads(r.text)
        cpu_load = response["latest_values"]

    except Exception as e:
        # result["data"] = str(e)
        # LOG.info(str(e))
        return False

    return cpu_load


def _getMem(username=None, password=None, host=None, port=None, usehttps=False, num_points=5):
    """ netdata system Memory API
    GET method which returns free memory percentage
     
    :param username: username for login
    :param password: password for login
    :param host: host url
    :param port: port where the netdata API can be accessed
    :usehttps: https or http
    :num_points: data points to fetch from netdata
    
    Example:

    """
    if usehttps:
        base_path = 'https://{0}:{1}'.format(host, port)
    else:
        base_path = 'http://{0}:{1}'.format(host, port)

    _endpoint = '{0}/api/v1/data?chart=system.ram&format=json&points=5&after=-60&options=jsonwrap|percentage'.format(base_path, num_points)

    # headers = {"Content-Type": "application/yaml", "accept": "application/json"}
    # data = {"username": username, "password": password}

    try:
        r = requests.get(_endpoint)

        if r.status_code != requests.codes.ok:
            return False

        response = json.loads(r.text)
        free_mem_percent = response["view_latest_values"][0]

    except Exception as e:
        # result["data"] = str(e)
        # LOG.info(str(e))
        return False

    return free_mem_percent



print(_getLoad(host="vm-hadik3r-07.cs.uni-paderborn.de", port=19999))
print(_getMem(host="vm-hadik3r-07.cs.uni-paderborn.de", port=19999))