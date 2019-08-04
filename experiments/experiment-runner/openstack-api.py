from keystoneauth1.identity import v3
from keystoneauth1 import session
from heatclient import client
from novaclient import client as nvclient
from dateutil import parser
import time

AUTH_URL = "http://131.234.29.168/identity/v3"
OS_USERNAME = "demo"
OS_PASSWORD = "123"

def delete_stacks():
    auth = v3.Password(auth_url=AUTH_URL,
                    username=OS_USERNAME,
                    password=OS_PASSWORD,
                    project_name='demo',
                    user_domain_id='default',
                    project_domain_id='default')
    sess = session.Session(auth=auth)
    heat = client.Client('1', session=sess)

    for s in heat.stacks.list():
        try:
            s.delete()
        except Exception as e:
            print(e)


def get_count(init_time):
    auth = v3.Password(auth_url=AUTH_URL,
                    username=OS_USERNAME,
                    password=OS_PASSWORD,
                    project_name='demo',
                    user_domain_id='default',
                    project_domain_id='default')

    sess = session.Session(auth=auth)

    nova = nvclient.Client('2', session=sess)

    _servers = nova.servers.list()

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

def get_count_stack(init_time):
    auth = v3.Password(auth_url=AUTH_URL,
                    username=OS_USERNAME,
                    password=OS_PASSWORD,
                    project_name='demo',
                    user_domain_id='default',
                    project_domain_id='default')
    sess = session.Session(auth=auth)
    heat = client.Client('1', session=sess)

    active_count = 0
    build_count = 0
    error_count = 0

    for _s in heat.stacks.list():
        server_created = parser.parse(_s.creation_time)
        if int(server_created.strftime("%s")) > int(init_time) :
            print(_s.stack_status)
            if _s.stack_status == "UPDATE_COMPLETE":
                active_count += 1
            elif _s.stack_status in ["UPDATE_IN_PROGRESS", "CREATE_COMPLETE"]:
                build_count += 1
            elif _s.stack_status in ["CREATE_FAILED", "UPDATE_FAILED"]:
                error_count += 1
            else:
                # print("Other Status")
                pass
                # print(_s.stack_status)

    return active_count, build_count, error_count


START = time.time()
while(True):
    print(time.time()-START)
    print(get_count(0))
    # delete_stacks()
    time.sleep(5)