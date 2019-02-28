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

@fixture
def get_ns_instances_keys():
    return ['vld', 'short-name', 'ssh-authorized-key', 'constituent-vnfr-ref',
       'name', '_id', 'admin-status', 'nsd-name-ref', 'description', 'instantiate_params', 
          'config-status', 'operational-events', 'datacenter', 'orchestration-progress', 'id', 
            'name-ref', 'resource-orchestrator', 'nsd-ref', 'detailed-status', 'crete-time', 
                'ns-instance-config-ref', 'nsd', 'operational-status', '_admin']

@fixture
def delete_ns_instances_nsinstanceid_keys():
    return['_id']

@fixture
def get_ns_lcm_op_ops_keys():
    return['operationParams', 'isAutomaticInvocation', 'links', 'operationState', 
            'id', '_id', 'isCancelPending', 'startTime', 'nsInstanceId', '_admin', 
              'statusEnteredTime', 'lcmOperationType', 'detailed-status']

@fixture
def get_ns_lcm_op_ops_nslcmopoccid_keys():
    return['operationParams', 'isAutomaticInvocation']

@fixture
def post_ns_instances_keys():
    return['id']

@fixture
def get_user_list_keys():
  return ['_id', 'password', 'username', '_admin', 'projects']

@fixture()
def get_user_info_keys():
  return['_id', 'password', 'username', '_admin', 'projects']

@fixture()
def get_project_list_keys():
  return['_id', 'name', '_admin']

@fixture()
def get_project_info_keys():
  return['_id', 'name', '_admin']

    