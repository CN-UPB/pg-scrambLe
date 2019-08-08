from __future__ import print_function
import time
import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint

from kubernetes import client, config

aToken = "eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tOWo3cTgiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjNjOTIxZjk4LTdhZTMtNDE2NS1hYjlmLWM1ZThiZTM5MjNjYyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.I-cs6gpNfHopqCJEnf9Jhhga9CQhovt--MY90uKlXKvPBhIQ-sdtkXf1_1cXTnmKcayA8p66FRliK61swlENTTZEj62OehfxfQz-7JQfqgp0g9xRae3laCYUyGwkCioLGnqI7sJILau4_2KXLw1nDiwy4gDGIT54q_JBR2Yhxwvz_N6uyJAt1rLdvHdpTKQc8ZnC0LlijgcbnGfXpWv6AO803E0ufUvAr6QpdoxUHO0BJcyEWTgE-xU97tgiX8CR1_QVtI8bGZa33_FhueMsILVt-BFZ5laxcSCYNK275mFX6ILRNcfWKKmKaFG8sC_xD5JWIES_VFpys6gem8qGCQ"

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

    for _s in _servers:
        server_created = parser.parse(_s.created)
        if int(server_created.strftime("%s")) > int(init_time) :
            if _s.status == "ACTIVE":
                active_count += 1
            elif _s.status == "BUILD":
                build_count += 1
            elif _s.status == "ERROR":
                error_count += 1
            else:
                print("Other Status")
                print(_s.status)

    return active_count, build_count, error_count


if __name__ == '__main__':
#     delete_replication_controller()
#     delete_replication_pod()
