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
    return []

@fixture
def post_ns_descriptors_keys():
    return ['id']