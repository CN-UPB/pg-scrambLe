from keystoneauth1.identity import v3
from keystoneauth1 import session
from heatclient import client
from novaclient import client as nvclient

AUTH_URL = "http://131.234.28.181/identity/v3"
OS_USERNAME = "demo"
OS_PASSWORD = "1234"

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
        s.delete()

def get_count():
    auth = v3.Password(auth_url=AUTH_URL,
                    username=OS_USERNAME,
                    password=OS_PASSWORD,
                    project_name='scale',
                    user_domain_id='default',
                    project_domain_id='default')

    sess = session.Session(auth=auth)

    nova = nvclient.Client('2', session=sess)

    _servers = nova.servers.list()

    active_count = 0
    error_count = 0

    for _s in _servers:
        if _s.status == "ACTIVE":
            active_count += 1
        else:
            error_count += 1

    return active_count, error_count


print(get_count())