from pytest import fixture

@fixture
def auth_keys():
    return ['_id', 'project_id', 'admin', 'expires',
                'id', 'issued_at', 'remote_port',
                'username', 'remote_host']

@fixture
def get_ns_descriptors_keys():
    return ['id', 'logo', 'vld', 'short-name', 'constituent-vnfd',
                '_admin', 'description', 'name', 
                'vendor', 'id', 'version']

@fixture
def delete_ns_descriptors_nsdinfoid_keys():
    return ['']

@fixture
def post_ns_descriptors_keys():
    return ['id']

@fixture
def get_vnf_packages_keys():
    return ['name', 'id', '_id', 'description']

@fixture
def post_vnf_packages_keys():
    return ['id']

@fixture
def get_vnf_packages_vnfpkgid_keys():
    return ['id']

@fixture
def delete_vnf_packages_vnfpkgid_keys():
    return ['']