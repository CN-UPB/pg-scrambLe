from pytest import fixture

@fixture
def auth_keys():
    return ['username', 'session_began_at', 'token']

@fixture
def get_vnf_packages_keys():
    return ['created_at', 'md5', 'signature', 'status', 'updated_at', 'username', 'vnfd', 'uuid']

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

@fixture
def post_vnf_packages_keys():
    return ['id']

@fixture
def delete_ns_descriptors_nsdinfoid_keys():
    return ['']

@fixture
def delete_vnf_packages_vnfpkgid_keys():
    return ['']

@fixture
def get_vnf_packages_vnfpkgid_keys():
    return ['id']

@fixture
def post_ns_instances_nsinstanceid_terminate_keys():
    return ['id', 'created_at', 'updated_at', 'service_uuid', 'status', 'request_type', 'service_instance_uuid', 'began_at', 'callback']


@fixture
def post_ns_instances_nsinstanceid_instantiate_keys():
    return ['id', 'created_at', 'updated_at', 'service_uuid', 'status', 'request_type', 'service_instance_uuid', 'began_at', 'callback']

@fixture
def get_ns_instances_keys():
    return ['created_at', 'descriptor_reference', 'descriptor_version', 'network_functions', 'status', 'updated_at', 'version', 'uuid']
                
@fixture
def test_get_ns_instances_nsinstanceid_keys():
    return ['created_at', 'descriptor_reference', 'descriptor_version', 'network_functions', 'status', 'updated_at', 'version', 'uuid']


