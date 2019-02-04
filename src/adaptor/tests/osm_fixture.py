from pytest import fixture

@fixture
def auth_keys():
    return ['_id', 'project_id', 'admin', 'expires',
                'id', 'issued_at', 'remote_port',
                'username', 'remote_host']

@fixture
def get_ns_descriptors_keys():
    return ['_id', 'logo', 'vld', 'short-name', 'constituent-vnfd',
                '_admin', 'description', 'name', 
                'vendor', 'id', 'version']

@fixture
def delete_ns_descriptors_keys():
    return ['']

@fixture
def post_ns_descriptors_keys():
    return ['id']

@fixture
def get_vnf_packages_keys():
    return ['logo', 'connection-point', 'name', 'mgmt-interface', 
                'short-name', 'vendor', 'id', '_id', '_admin', 
                'description', 'vdu', 'version']

@fixture
def post_vnf_packages_keys():
    return ['detail', 'status', 'code']

@fixture
def get_vnf_packages_vnfpkgid_keys():
    return ['id']

@fixture
def delete_vnf_packages_vnfpkgid_keys():
    return ['']