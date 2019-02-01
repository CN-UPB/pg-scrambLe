from pytest import fixture

@fixture
def auth_keys():
    return ['username', 'session_began_at', 'token']

@fixture
def get_ns_descriptors_keys():
    return ['created_at', 'md5', 'nsd', 'signature', 'status',
                'updated_at', 'username', 'uuid']

@fixture
def delete_ns_descriptors_keys():
    return ['']

@fixture
def post_ns_descriptors_keys():
    return ['id']