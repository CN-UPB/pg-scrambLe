from __future__ import print_function
import time
import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint
from dateutil import parser

from kubernetes import client, config

aToken = "eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4ta3pqNWoiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjRmMjkzM2MyLTgxM2UtNDhhMC1hNjI5LTc0ZTZiOTIxMjZjMSIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.VpFSCZNaxeH0Ulk6xipNRso3jVvKauBkIQ5ZY92BPoCMp0JpsWwfEL1aWG1v1t863HFburIXKb7utRrXJezdb8RCmY5dnHzjhMsO_Yh92w4_ILOp2u45YFOUnFebvxc39vwXOLa-3edHkiOC6gwlZAvnU4YuEgCQ3PmAMpo5E6GQa3fIM2q6AHwtC_fecIn8IN2-RMfnBadBBGd9J2DFkzPx93aUDrjfcpOoEXjJAbxd1t2B1Bc3BpBZVr7DfAD3SsC78rP0d0cv-jTJ1Xme00Woehb70fzye8Tj4ZjxwbOM24rkeOUkPktFzjfZwOGohxA4bYEkeUmIicbXWhAf4w"
K8_URL = "https://131.234.29.11"

aConfiguration = client.Configuration()
aConfiguration.host = "https://131.234.29.11"

aConfiguration.verify_ssl = False
aConfiguration.api_key = {"authorization": "Bearer " + aToken}

aApiClient = client.ApiClient(aConfiguration)


def delete_replication_controller():

    v1 = client.CoreV1Api(aApiClient)
    print("Listing pods with their IPs:")
    ret = v1.list_namespaced_replication_controller(namespace='default', watch=False)
    for i in ret.items:
        # delete_pod('kargo-3','default')
      print("%s\t%s" %
            (i.metadata.name, i.metadata.creation_timestamp))

      api_instance = client.CoreV1Api(aApiClient)
      body = client.V1DeleteOptions()
      api_response = api_instance.delete_namespaced_replication_controller(i.metadata.name, i.metadata.namespace, body=body)

def delete_pod():

    v1 = client.CoreV1Api(aApiClient)
    print("Listing pods with their IPs:")
    ret = v1.list_namespaced_pod(namespace='default', watch=False)
    for i in ret.items:
        # delete_pod('kargo-3','default')
      print("%s\t%s" %
            (i.metadata.name, i.metadata.creation_timestamp))

      api_instance = client.CoreV1Api(aApiClient)
      body = client.V1DeleteOptions()
      api_response = api_instance.delete_namespaced_pod(i.metadata.name, i.metadata.namespace, body=body)

def get_count(init_time):

    v1 = client.CoreV1Api(aApiClient)
    print("Listing pods with their IPs:")
    _servers = v1.list_namespaced_pod(namespace='default', watch=False)

    active_count = 0
    build_count = 0
    error_count = 0
    try:
        for _s in _servers.items:
            print(_s.status.container_statuses[0].ready)
            # print(_s.status.phase)
            if int(_s.metadata.creation_timestamp.strftime("%s")) > int(init_time) :
                if _s.status.phase in ['Succeeded', 'Running']:
                    active_count += 1
                elif _s.status.phase in ['Pending']:
                    build_count += 1
                elif _s.status.phase in ['Failed', 'Unknown']:
                    error_count += 1
                else:
                    print("Other Status")
                    print(_s.status.phase)

        return active_count, build_count, error_count
    except Exception as identifier:
        pass




if __name__ == '__main__':
#     delete_replication_controller()
#     delete_replication_pod()
    while(1):
        get_count(0)
        time.sleep(2)